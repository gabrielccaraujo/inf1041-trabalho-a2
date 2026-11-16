import pytest

from domain.models import Group, User
from domain.rules import BusinessError
from use_cases.service import RachaiService


class FakeRepository:
    def __init__(self):
        self.users = {
            "a": User("a", "Ana", "ana@example.com", ""),
            "b": User("b", "Bruno", "bruno@example.com", ""),
        }
        self.group = Group("g", "Viagem", "Viagem", "a", "invite")
        self.created = None

    def get_user_by_email(self, email):
        return next((user for user in self.users.values() if user.email == email), None)

    def create_user(self, user):
        self.created = user

    def get_group(self, group_id):
        return self.group if group_id == "g" else None

    def list_members(self, group_id):
        return list(self.users.values()) if group_id == "g" else []

    def create_expense(self, expense, splits):
        self.created = (expense, splits)


def test_registration_use_case_hashes_password_without_flask_or_database():
    repository = FakeRepository()
    user = RachaiService(repository).register_user(" Carla ", "CARLA@example.com", "senhaforte1")
    assert user.name == "Carla"
    assert user.email == "carla@example.com"
    assert "senhaforte1" not in user.password_hash
    assert repository.created == user


def test_expense_use_case_checks_members_and_persists_exact_split():
    repository = FakeRepository()
    expense, returned_splits = RachaiService(repository).create_expense(
        "a", "g", "Almoco", "10.01", "a", ["a", "b"], occurred_on="2026-11-16")
    saved, splits = repository.created
    assert saved == expense
    assert returned_splits == splits
    assert sum(split.amount_cents for split in splits) == 1001
    assert {split.user_id: split.amount_cents for split in splits} == {"a": 501, "b": 500}


def test_expense_use_case_rejects_non_member_participant():
    repository = FakeRepository()
    with pytest.raises(BusinessError):
        RachaiService(repository).create_expense(
            "a", "g", "Almoco", "10.00", "a", ["a", "intruso"])
    assert repository.created is None
