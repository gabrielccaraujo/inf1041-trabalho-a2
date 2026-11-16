from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str
    password_hash: str


@dataclass(frozen=True)
class Group:
    id: str
    name: str
    category: str
    owner_id: str
    invite_code: str


@dataclass(frozen=True)
class Expense:
    id: str
    group_id: str
    description: str
    amount_cents: int
    paid_by: str
    category: str
    occurred_on: str


@dataclass(frozen=True)
class Split:
    expense_id: str
    user_id: str
    amount_cents: int
