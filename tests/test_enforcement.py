from datetime import datetime, timedelta

import pytest

from src.enforcement import EnforcementOfficer, AutomaticCamera
from src.penalty import PenaltySchedule
from src.driver import Driver, SUSPENSION_THRESHOLD
from src.vehicle import Car
from src.exceptions import ViolationError, RegistrationError


@pytest.fixture
def schedule():
    return PenaltySchedule.default()


@pytest.fixture
def driver():
    return Driver("ABC12345678", "Chidi Okafor")


@pytest.fixture
def vehicle():
    return Car("KJA-245XY", "Toyota", "Corolla", 2019, engine_capacity_cc=1800)


@pytest.fixture
def officer():
    return EnforcementOfficer("OFF-1001", "Insp. Bello", "Ikeja Zone")


# ── EnforcementOfficer ───────────────────────────────────────────────────


def test_invalid_badge_no_raises():
    with pytest.raises(RegistrationError):
        EnforcementOfficer("BADGE", "Insp. Bello", "Ikeja Zone")


def test_officer_records_violation(officer, driver, vehicle, schedule):
    v = officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)
    assert v.offence_code == "NO_SEATBELT"
    assert driver.demerit_points == 1
    assert v in officer.violations_issued


def test_suspended_driver_cannot_be_charged(officer, driver, vehicle, schedule):
    driver.accumulate_points(SUSPENSION_THRESHOLD)
    with pytest.raises(ViolationError):
        officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)


def test_unknown_offence_code_raises(officer, driver, vehicle, schedule):
    with pytest.raises(RegistrationError):
        officer.record_violation(driver, vehicle, "JAYWALKING", schedule)


def test_officer_add_merges_and_sorts_chronologically(driver, vehicle, schedule):
    o1 = EnforcementOfficer("OFF-2001", "Officer A", "Zone A")
    o2 = EnforcementOfficer("OFF-2002", "Officer B", "Zone B")
    t0 = datetime(2026, 1, 1, 8, 0)
    v_late = o1.record_violation(
        driver, vehicle, "NO_SEATBELT", schedule, timestamp=t0 + timedelta(hours=2)
    )
    v_early = o2.record_violation(driver, vehicle, "ILLEGAL_PARKING", schedule, timestamp=t0)
    merged = o1 + o2
    assert merged == [v_early, v_late]


# ── AutomaticCamera ───────────────────────────────────────────────────────


def test_invalid_camera_id_raises():
    with pytest.raises(RegistrationError):
        AutomaticCamera("BADCAM", "Apapa", speed_limit_kmh=60)


def test_invalid_speed_limit_raises():
    with pytest.raises(RegistrationError):
        AutomaticCamera("CAM-9001", "Apapa", speed_limit_kmh=0)


@pytest.mark.parametrize(
    "speed,expected_code",
    [
        (75, None),
        (80, None),  # exactly at the limit -> compliant
        (95, "SPEEDING_MINOR"),  # 15 over
        (100, "SPEEDING_MINOR"),  # 20 over -- still in the minor band
        (130, "SPEEDING_MAJOR"),  # 50 over
    ],
)
def test_camera_classifies_speed_correctly(speed, expected_code):
    camera = AutomaticCamera("CAM-5001", "3rd Mainland Bridge", speed_limit_kmh=80)
    assert camera.classify_speed(speed) == expected_code


def test_camera_detect_and_record_within_limit_returns_none(driver, vehicle, schedule):
    camera = AutomaticCamera("CAM-5002", "Apapa", speed_limit_kmh=80)
    assert camera.detect_and_record(driver, vehicle, 60, schedule) is None


def test_camera_detect_and_record_issues_violation(driver, vehicle, schedule):
    camera = AutomaticCamera("CAM-5003", "Apapa", speed_limit_kmh=80)
    v = camera.detect_and_record(driver, vehicle, 95, schedule)
    assert v.offence_code == "SPEEDING_MINOR"
    assert v in camera.violations_issued
