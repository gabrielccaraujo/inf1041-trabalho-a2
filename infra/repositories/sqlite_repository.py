from domain.models import Expense, Group, Split, User
from infra.db.sqlite import SqliteDatabase


class SqliteRepository:
    def __init__(self, database: SqliteDatabase):
        self.database = database

    def create_user(self, user: User) -> None:
        with self.database.connection() as db:
            db.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                       (user.id, user.name, user.email, user.password_hash))

    def get_user(self, user_id: str) -> User | None:
        with self.database.connection() as db:
            row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return User(**dict(row)) if row else None

    def get_user_by_email(self, email: str) -> User | None:
        with self.database.connection() as db:
            row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return User(**dict(row)) if row else None

    def create_session(self, token_hash: str, user_id: str, expires_at: str) -> None:
        with self.database.connection() as db:
            db.execute("INSERT INTO sessions VALUES (?, ?, ?)", (token_hash, user_id, expires_at))

    def get_session_user_id(self, token_hash: str, now: str) -> str | None:
        with self.database.connection() as db:
            row = db.execute("SELECT user_id FROM sessions WHERE token_hash = ? AND expires_at > ?",
                             (token_hash, now)).fetchone()
        return row["user_id"] if row else None

    def create_group(self, group: Group) -> None:
        with self.database.connection() as db:
            db.execute("INSERT INTO groups VALUES (?, ?, ?, ?, ?)",
                       (group.id, group.name, group.category, group.owner_id, group.invite_code))
            db.execute("INSERT INTO group_members VALUES (?, ?)", (group.id, group.owner_id))

    def get_group(self, group_id: str) -> Group | None:
        with self.database.connection() as db:
            row = db.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()
        return Group(**dict(row)) if row else None

    def get_group_by_invite_code(self, code: str) -> Group | None:
        with self.database.connection() as db:
            row = db.execute("SELECT * FROM groups WHERE invite_code = ?", (code,)).fetchone()
        return Group(**dict(row)) if row else None

    def list_groups_for_user(self, user_id: str) -> list[Group]:
        with self.database.connection() as db:
            rows = db.execute(
                "SELECT g.* FROM groups g JOIN group_members m ON m.group_id = g.id "
                "WHERE m.user_id = ? ORDER BY g.name", (user_id,)).fetchall()
        return [Group(**dict(row)) for row in rows]

    def add_group_member(self, group_id: str, user_id: str) -> None:
        with self.database.connection() as db:
            db.execute("INSERT OR IGNORE INTO group_members VALUES (?, ?)", (group_id, user_id))

    def list_members(self, group_id: str) -> list[User]:
        with self.database.connection() as db:
            rows = db.execute(
                "SELECT u.* FROM users u JOIN group_members m ON m.user_id = u.id "
                "WHERE m.group_id = ? ORDER BY u.name", (group_id,)).fetchall()
        return [User(**dict(row)) for row in rows]

    def create_expense(self, expense: Expense, splits: list[Split]) -> None:
        with self.database.connection() as db:
            db.execute("INSERT INTO expenses VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (expense.id, expense.group_id, expense.description,
                        expense.amount_cents, expense.paid_by, expense.category,
                        expense.occurred_on))
            db.executemany("INSERT INTO expense_splits VALUES (?, ?, ?)",
                           [(s.expense_id, s.user_id, s.amount_cents) for s in splits])

    def list_expenses(self, group_id: str) -> list[Expense]:
        with self.database.connection() as db:
            rows = db.execute("SELECT * FROM expenses WHERE group_id = ? "
                              "ORDER BY occurred_on DESC, id DESC", (group_id,)).fetchall()
        return [Expense(**dict(row)) for row in rows]

    def list_splits(self, expense_id: str) -> list[Split]:
        with self.database.connection() as db:
            rows = db.execute("SELECT * FROM expense_splits WHERE expense_id = ? "
                              "ORDER BY user_id", (expense_id,)).fetchall()
        return [Split(**dict(row)) for row in rows]
