import pytest

from src.payment import PaymentRecord, PaymentChannel
from src.violation import ViolationRecord
from src.vehicle import Car
from src.driver import Driver


@pytest.fixture
def violation():
    driver = Driver("ABC12345678", "Chidi Okafor")
    vehicle = Car("KJA-245XY", "Toyota", "Corolla", 2019, engine_capacity_cc=1800)
    return ViolationRecord(driver, vehicle, "NO_SEATBELT", 5_000.0, 1)


def test_payment_construction(violation):
    p = PaymentRecord(violation, 5_000.0, PaymentChannel.POS)
    assert p.amount_paid_ngn == 5_000.0
    assert p.channel == PaymentChannel.POS


def test_payment_str_contains_channel(violation):
    p = PaymentRecord(violation, 5_000.0, PaymentChannel.USSD)
    assert "USSD" in str(p)


def test_payment_accepts_string_channel(violation):
    p = PaymentRecord(violation, 5_000.0, "BANK")
    assert p.channel == PaymentChannel.BANK


def test_payment_rejects_unknown_channel(violation):
    with pytest.raises(ValueError):
        PaymentRecord(violation, 5_000.0, "CRYPTO")


def test_payment_repr_includes_violation_id(violation):
    p = PaymentRecord(violation, 5_000.0, PaymentChannel.ONLINE)
    assert violation.violation_id in repr(p)
