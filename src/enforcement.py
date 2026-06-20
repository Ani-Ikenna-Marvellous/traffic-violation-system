"""Enforceable interface and its two concrete realisations:
:class:`EnforcementOfficer` (a human officer) and :class:`AutomaticCamera`
(an unmanned speed-detection camera node).
"""

import re
from abc import ABC, abstractmethod
from datetime import datetime

from .exceptions import RegistrationError, ViolationError
from .violation import ViolationRecord

BADGE_PATTERN = re.compile(r"^OFF-\d{4,6}$")
CAMERA_PATTERN = re.compile(r"^CAM-\d{4,6}$")

SPEEDING_MINOR_MAX_OVER_KMH = 20  # upper bound of the "minor" band


class Enforceable(ABC):
    """Interface implemented by every entity capable of issuing a
    :class:`~src.violation.ViolationRecord` against a driver/vehicle pair.

    Modelled as a pure-abstract interface (every method is abstract, no
    shared implementation) so that :class:`EnforcementOfficer` and
    :class:`AutomaticCamera` *realise* it rather than simply inheriting
    from it -- see ``uml/class_diagram.png`` for the realization arrows.
    """

    @abstractmethod
    def record_violation(
        self,
        driver,
        vehicle,
        offence_code: str,
        penalty_schedule,
        timestamp: datetime | None = None,
    ) -> ViolationRecord:
        """Look up the offence in ``penalty_schedule``, charge the
        driver's demerit points, and return a new ViolationRecord."""
        raise NotImplementedError


def _charge_driver(driver, offence) -> None:
    """Shared enforcement rule: a suspended driver cannot be charged with
    a new violation until manually reinstated (functional requirement
    #53). Used by both concrete Enforceable implementations below."""
    if driver.is_suspended:
        raise ViolationError(
            f"Driver {driver.licence_no} is currently suspended; cannot "
            f"record a new violation until reinstated.",
            driver_id=driver.licence_no,
            offence_code=offence.code,
        )
    driver.accumulate_points(offence.demerit_pts)


class EnforcementOfficer(Enforceable):
    """A human traffic enforcement officer assigned to a patrol zone."""

    def __init__(self, badge_no: str, name: str, zone: str):
        self.badge_no = badge_no  # goes through the validated setter
        self._name = name
        self._zone = zone
        self._violations_issued: list = []

    @property
    def badge_no(self) -> str:
        return self._badge_no

    @badge_no.setter
    def badge_no(self, value: str) -> None:
        if not isinstance(value, str) or not BADGE_PATTERN.match(value):
            raise RegistrationError(
                f"Badge number {value!r} must match the format OFF-9999.",
                field="badge_no",
                value=value,
            )
        self._badge_no = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def zone(self) -> str:
        return self._zone

    @property
    def violations_issued(self) -> list:
        return list(self._violations_issued)

    def record_violation(
        self,
        driver,
        vehicle,
        offence_code: str,
        penalty_schedule,
        timestamp: datetime | None = None,
    ) -> ViolationRecord:
        offence = penalty_schedule.lookup(offence_code)
        _charge_driver(driver, offence)
        record = ViolationRecord(
            driver=driver,
            vehicle=vehicle,
            offence_code=offence.code,
            fine_ngn=offence.fine_ngn,
            demerit_pts=offence.demerit_pts,
            timestamp=timestamp,
            enforcer_id=self.badge_no,
        )
        self._violations_issued.append(record)
        return record

    def __add__(self, other: "EnforcementOfficer") -> list:
        """Merge two officers' issued-violation lists into a single
        chronologically sorted list -- used for shift handover reporting
        (functional requirement #57)."""
        if not isinstance(other, EnforcementOfficer):
            return NotImplemented
        merged = self._violations_issued + other._violations_issued
        return sorted(merged)

    def __str__(self) -> str:
        return f"Officer {self.name} ({self.badge_no}) — Zone {self.zone}"

    def __repr__(self) -> str:
        return f"EnforcementOfficer(badge_no={self.badge_no!r}, name={self.name!r})"


class AutomaticCamera(Enforceable):
    """An unmanned camera node that auto-classifies speeding violations."""

    def __init__(self, camera_id: str, location: str, speed_limit_kmh: float):
        self.camera_id = camera_id  # goes through the validated setter
        self._location = location
        self.speed_limit_kmh = speed_limit_kmh  # goes through the validated setter
        self._violations_issued: list = []

    @property
    def camera_id(self) -> str:
        return self._camera_id

    @camera_id.setter
    def camera_id(self, value: str) -> None:
        if not isinstance(value, str) or not CAMERA_PATTERN.match(value):
            raise RegistrationError(
                f"Camera id {value!r} must match the format CAM-9999.",
                field="camera_id",
                value=value,
            )
        self._camera_id = value

    @property
    def location(self) -> str:
        return self._location

    @property
    def speed_limit_kmh(self) -> float:
        return self._speed_limit_kmh

    @speed_limit_kmh.setter
    def speed_limit_kmh(self, value: float) -> None:
        if value <= 0:
            raise RegistrationError(
                "speed_limit_kmh must be positive.",
                field="speed_limit_kmh",
                value=value,
            )
        self._speed_limit_kmh = float(value)

    @property
    def violations_issued(self) -> list:
        return list(self._violations_issued)

    def classify_speed(self, detected_speed_kmh: float) -> str | None:
        """Return the correct offence code for a detected speed, or
        ``None`` if the vehicle was within the limit (functional
        requirement #54)."""
        over = detected_speed_kmh - self._speed_limit_kmh
        if over <= 0:
            return None
        if over <= SPEEDING_MINOR_MAX_OVER_KMH:
            return "SPEEDING_MINOR"
        return "SPEEDING_MAJOR"

    def detect_and_record(
        self,
        driver,
        vehicle,
        detected_speed_kmh: float,
        penalty_schedule,
        timestamp: datetime | None = None,
    ) -> ViolationRecord | None:
        """Classify a detected speed and, if it constitutes an offence,
        record it. Returns ``None`` for a compliant reading."""
        code = self.classify_speed(detected_speed_kmh)
        if code is None:
            return None
        return self.record_violation(
            driver, vehicle, code, penalty_schedule, timestamp=timestamp
        )

    def record_violation(
        self,
        driver,
        vehicle,
        offence_code: str,
        penalty_schedule,
        timestamp: datetime | None = None,
    ) -> ViolationRecord:
        offence = penalty_schedule.lookup(offence_code)
        _charge_driver(driver, offence)
        record = ViolationRecord(
            driver=driver,
            vehicle=vehicle,
            offence_code=offence.code,
            fine_ngn=offence.fine_ngn,
            demerit_pts=offence.demerit_pts,
            timestamp=timestamp,
            enforcer_id=self.camera_id,
        )
        self._violations_issued.append(record)
        return record

    def __str__(self) -> str:
        return (
            f"Camera {self.camera_id} @ {self.location} "
            f"(limit {self.speed_limit_kmh:.0f} km/h)"
        )

    def __repr__(self) -> str:
        return f"AutomaticCamera(camera_id={self.camera_id!r}, location={self.location!r})"
