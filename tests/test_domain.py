import pytest

from domain.rules import BusinessError, cents_to_money, money_to_cents, split_equally


def test_money_and_equal_split_preserve_every_cent():
    assert money_to_cents("10.01") == 1001
    assert split_equally(1001, ["c", "b", "a"]) == {"a": 334, "b": 334, "c": 333}
    assert cents_to_money(-333) == "-3.33"


@pytest.mark.parametrize("value", ["0", "-1", "1.001", "NaN", 12.5])
def test_invalid_money_is_rejected(value):
    with pytest.raises(BusinessError):
        money_to_cents(value)


def test_duplicate_participants_are_rejected():
    with pytest.raises(BusinessError):
        split_equally(100, ["a", "a"])
