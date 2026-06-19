import pytest

from src.penalty import PenaltySchedule
from src.exceptions import RegistrationError

REQUIRED_CODES = [
    "SPEEDING_MINOR",
    "SPEEDING_MAJOR",
    "NO_SEATBELT",
    "WRONG_WAY",
    "EXPIRED_LICENCE",
    "OVERLOADING",
    "RUNNING_RED_LIGHT",
    "NO_INSURANCE",
    "PHONE_WHILE_DRIVING",
    "ILLEGAL_PARKING",
]


def test_default_schedule_has_at_least_ten_codes():
    schedule = PenaltySchedule.default()
    assert len(schedule) >= 10


@pytest.mark.parametrize("code", REQUIRED_CODES)
def test_default_schedule_contains_required_code(code):
    schedule = PenaltySchedule.default()
    assert code in schedule
    offence = schedule.lookup(code)
    assert offence.fine_ngn > 0
    assert offence.demerit_pts >= 0


def test_lookup_unknown_code_raises():
    schedule = PenaltySchedule.default()
    with pytest.raises(RegistrationError) as exc_info:
        schedule.lookup("NOT_A_REAL_CODE")
    assert exc_info.value.field == "offence_code"


def test_from_dict_rejects_non_positive_fine():
    with pytest.raises(RegistrationError):
        PenaltySchedule.from_dict({"X": ("desc", 0, 1)})


def test_from_dict_rejects_negative_demerit_points():
    with pytest.raises(RegistrationError):
        PenaltySchedule.from_dict({"X": ("desc", 1000.0, -1)})


def test_schedule_is_iterable_and_len_matches():
    schedule = PenaltySchedule.default()
    offences = list(schedule)
    assert len(offences) == len(schedule)


def test_schedule_str_and_repr():
    schedule = PenaltySchedule.default()
    assert "PenaltySchedule" in str(schedule)
    assert "SPEEDING_MINOR" in repr(schedule)
