import pytest

from src.driver import Driver, SUSPENSION_THRESHOLD
from src.exceptions import RegistrationError


@pytest.fixture
def driver():
    return Driver("ABC12345678", "Chidi Okafor")


def test_valid_driver_construction(driver):
    assert driver.full_name == "Chidi Okafor"
    assert driver.demerit_points == 0
    assert driver.is_suspended is False


def test_invalid_licence_format_raises():
    with pytest.raises(RegistrationError) as exc_info:
        Driver("bad-licence", "Someone")
    assert exc_info.value.field == "licence_no"


def test_empty_name_raises():
    with pytest.raises(RegistrationError):
        Driver("ABC12345678", "   ")


def test_accumulate_points_below_threshold(driver):
    driver.accumulate_points(5)
    assert driver.demerit_points == 5
    assert driver.is_suspended is False


def test_accumulate_points_triggers_suspension_at_boundary(driver):
    driver.accumulate_points(SUSPENSION_THRESHOLD)
    assert driver.demerit_points == SUSPENSION_THRESHOLD
    assert driver.is_suspended is True


def test_accumulate_points_one_below_threshold_not_suspended(driver):
    driver.accumulate_points(SUSPENSION_THRESHOLD - 1)
    assert driver.is_suspended is False


def test_accumulate_points_above_threshold_still_suspended(driver):
    driver.accumulate_points(SUSPENSION_THRESHOLD + 5)
    assert driver.is_suspended is True


def test_negative_points_raises(driver):
    with pytest.raises(ValueError):
        driver.accumulate_points(-1)


def test_reinstate_resets_state(driver):
    driver.accumulate_points(SUSPENSION_THRESHOLD)
    assert driver.is_suspended is True
    driver.reinstate()
    assert driver.is_suspended is False
    assert driver.demerit_points == 0


def test_demerit_points_cannot_be_set_directly(driver):
    with pytest.raises(AttributeError):
        driver.demerit_points = 99  # property has no setter -- enforced read-only


def test_driver_str_contains_status(driver):
    assert "ACTIVE" in str(driver)
    driver.accumulate_points(SUSPENSION_THRESHOLD)
    assert "SUSPENDED" in str(driver)
