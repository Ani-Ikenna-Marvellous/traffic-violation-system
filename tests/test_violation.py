from datetime import datetime, timedelta

import pytest

from src.violation import ViolationRecord
from src.vehicle import Car
from src.driver import Driver


@pytest.fixture
def driver():
    return Driver("ABC12345678", "Chidi Okafor")


@pytest.fixture
def vehicle():
    return Car("KJA-245XY", "Toyota", "Corolla", 2019, engine_capacity_cc=1800)


def test_violation_construction(driver, vehicle):
    v = ViolationRecord(driver, vehicle, "NO_SEATBELT", 5_000.0, 1)
    assert v.offence_code == "NO_SEATBELT"
    assert v.paid is False
    assert len(v.violation_id) == 36  # canonical UUID4 string length


def test_mark_paid_flips_flag(driver, vehicle):
    v = ViolationRecord(driver, vehicle, "NO_SEATBELT", 5_000.0, 1)
    v.mark_paid()
    assert v.paid is True


def test_equality_by_violation_id_not_by_fields(driver, vehicle):
    v1 = ViolationRecord(driver, vehicle, "NO_SEATBELT", 5_000.0, 1)
    v2 = ViolationRecord(driver, vehicle, "NO_SEATBELT", 5_000.0, 1)
    assert v1 != v2  # different UUIDs even with identical other fields
    assert v1 == v1


def test_ordering_by_timestamp(driver, vehicle):
    t0 = datetime(2026, 1, 1, 8, 0)
    earlier = ViolationRecord(driver, vehicle, "NO_SEATBELT", 5_000.0, 1, timestamp=t0)
    later = ViolationRecord(
        driver, vehicle, "NO_SEATBELT", 5_000.0, 1, timestamp=t0 + timedelta(minutes=5)
    )
    assert earlier < later
    assert sorted([later, earlier]) == [earlier, later]


def test_hash_consistent_with_equality(driver, vehicle):
    v = ViolationRecord(driver, vehicle, "NO_SEATBELT", 5_000.0, 1)
    assert hash(v) == hash(v.violation_id)
    assert v in {v}


def test_str_and_repr(driver, vehicle):
    v = ViolationRecord(driver, vehicle, "NO_SEATBELT", 5_000.0, 1)
    assert "NO_SEATBELT" in str(v)
    assert "ViolationRecord(" in repr(v)
