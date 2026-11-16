from decimal import Decimal, InvalidOperation
import re


class BusinessError(Exception):
    def __init__(self, message: str, code: str = "invalid_request", status: int = 400):
        super().__init__(message)
        self.code = code
        self.status = status


def money_to_cents(value: str) -> int:
    if not isinstance(value, str):
        raise BusinessError("Valor deve ser uma string decimal, como '12.50'.")
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", value):
        raise BusinessError("Valor monetario invalido.")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise BusinessError("Valor monetario invalido.") from exc
    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        raise BusinessError("Valor deve ser positivo e ter no maximo duas casas decimais.")
    return int(amount * 100)


def cents_to_money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}" if cents >= 0 else f"-{abs(cents) // 100}.{abs(cents) % 100:02d}"


def split_equally(amount_cents: int, participant_ids: list[str]) -> dict[str, int]:
    if amount_cents <= 0 or not participant_ids or len(set(participant_ids)) != len(participant_ids):
        raise BusinessError("A despesa exige valor positivo e participantes distintos.")
    ids = sorted(participant_ids)
    share, remainder = divmod(amount_cents, len(ids))
    return {user_id: share + (index < remainder) for index, user_id in enumerate(ids)}
