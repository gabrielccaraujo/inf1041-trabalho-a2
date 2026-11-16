import hashlib
import hmac
import re
import secrets
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from domain.models import Expense, Group, Split, User
from domain.rules import BusinessError, money_to_cents, split_equally
from use_cases.ports import Repository


class RachaiService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def register_user(self, name: str, email: str, password: str) -> User:
        name = self._required_text(name, "Nome", 100)
        email = self._required_text(email, "E-mail", 254).lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise BusinessError("E-mail invalido.")
        if not isinstance(password, str) or len(password) < 8 or not any(c.isdigit() for c in password):
            raise BusinessError("Senha deve ter ao menos 8 caracteres e um numero.")
        if self.repository.get_user_by_email(email):
            raise BusinessError("E-mail ja cadastrado.", "email_exists", 409)
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
        user = User(str(uuid4()), name, email, f"{salt.hex()}:{digest.hex()}")
        self.repository.create_user(user)
        return user

    def login(self, email: str, password: str) -> tuple[str, User]:
        if not isinstance(email, str) or not isinstance(password, str):
            raise BusinessError("Credenciais invalidas.", "invalid_credentials", 401)
        user = self.repository.get_user_by_email(email.strip().lower())
        if user is None or not self._verify_password(password, user.password_hash):
            raise BusinessError("Credenciais invalidas.", "invalid_credentials", 401)
        token = secrets.token_urlsafe(32)
        expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        self.repository.create_session(hashlib.sha256(token.encode()).hexdigest(), user.id, expires)
        return token, user

    def current_user(self, token: str) -> User:
        if not token:
            raise BusinessError("Autenticacao necessaria.", "unauthorized", 401)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        user_id = self.repository.get_session_user_id(token_hash, datetime.now(timezone.utc).isoformat())
        user = self.repository.get_user(user_id) if user_id else None
        if user is None:
            raise BusinessError("Sessao invalida ou expirada.", "unauthorized", 401)
        return user

    def create_group(self, actor_id: str, name: str, category: str = "Outros") -> Group:
        self._require_user(actor_id)
        name = self._required_text(name, "Nome do grupo", 100)
        category = self._required_text(category, "Categoria", 30)
        group = Group(str(uuid4()), name, category, actor_id, secrets.token_urlsafe(9))
        self.repository.create_group(group)
        return group

    def join_group(self, actor_id: str, invite_code: str) -> Group:
        self._require_user(actor_id)
        code = self._required_text(invite_code, "Codigo de convite", 100)
        group = self.repository.get_group_by_invite_code(code)
        if group is None:
            raise BusinessError("Convite nao encontrado.", "not_found", 404)
        self.repository.add_group_member(group.id, actor_id)
        return group

    def list_groups(self, actor_id: str) -> list[Group]:
        self._require_user(actor_id)
        return self.repository.list_groups_for_user(actor_id)

    def get_group(self, actor_id: str, group_id: str) -> tuple[Group, list[User]]:
        group = self._require_member(actor_id, group_id)
        return group, self.repository.list_members(group_id)

    def create_expense(self, actor_id: str, group_id: str, description: str,
                       amount: str, paid_by: str, participant_ids: list[str],
                       category: str = "Outros", occurred_on: str | None = None) -> tuple[Expense, list[Split]]:
        self._require_member(actor_id, group_id)
        description = self._required_text(description, "Descricao", 200)
        category = self._required_text(category, "Categoria", 30)
        cents = money_to_cents(amount)
        if not isinstance(participant_ids, list) or not all(isinstance(x, str) for x in participant_ids):
            raise BusinessError("Participantes devem ser uma lista de IDs.")
        member_ids = {user.id for user in self.repository.list_members(group_id)}
        if not isinstance(paid_by, str) or paid_by not in member_ids or not set(participant_ids).issubset(member_ids):
            raise BusinessError("Pagador e participantes devem pertencer ao grupo.")
        allocations = split_equally(cents, participant_ids)
        if occurred_on is None:
            occurred_on = date.today().isoformat()
        if not isinstance(occurred_on, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", occurred_on):
            raise BusinessError("Data deve estar no formato AAAA-MM-DD.")
        try:
            date.fromisoformat(occurred_on)
        except (TypeError, ValueError) as exc:
            raise BusinessError("Data deve estar no formato AAAA-MM-DD.") from exc
        expense = Expense(str(uuid4()), group_id, description, cents, paid_by, category, occurred_on)
        splits = [Split(expense.id, user_id, share) for user_id, share in allocations.items()]
        self.repository.create_expense(expense, splits)
        return expense, splits

    def list_expenses(self, actor_id: str, group_id: str) -> list[tuple[Expense, list[Split]]]:
        self._require_member(actor_id, group_id)
        return [(expense, self.repository.list_splits(expense.id))
                for expense in self.repository.list_expenses(group_id)]

    def balances(self, actor_id: str, group_id: str) -> list[dict]:
        self._require_member(actor_id, group_id)
        members = self.repository.list_members(group_id)
        totals = {member.id: 0 for member in members}
        for expense in self.repository.list_expenses(group_id):
            totals[expense.paid_by] += expense.amount_cents
            for split in self.repository.list_splits(expense.id):
                totals[split.user_id] -= split.amount_cents
        return [{"user_id": member.id, "name": member.name, "balance_cents": totals[member.id]}
                for member in members]

    def _require_user(self, user_id: str) -> None:
        if self.repository.get_user(user_id) is None:
            raise BusinessError("Usuario nao encontrado.", "not_found", 404)

    def _require_member(self, actor_id: str, group_id: str) -> Group:
        group = self.repository.get_group(group_id)
        if group is None:
            raise BusinessError("Grupo nao encontrado.", "not_found", 404)
        if actor_id not in {user.id for user in self.repository.list_members(group_id)}:
            raise BusinessError("Acesso ao grupo negado.", "forbidden", 403)
        return group

    @staticmethod
    def _required_text(value: str, label: str, max_length: int) -> str:
        if not isinstance(value, str) or not value.strip() or len(value.strip()) > max_length:
            raise BusinessError(f"{label} deve ter entre 1 e {max_length} caracteres.")
        return value.strip()

    @staticmethod
    def _verify_password(password: str, stored: str) -> bool:
        try:
            salt_hex, digest_hex = stored.split(":")
            digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 600_000)
            return hmac.compare_digest(digest, bytes.fromhex(digest_hex))
        except ValueError:
            return False
