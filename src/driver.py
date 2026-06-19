"""Driver: holds licence information and demerit point accumulation."""

import re

from .exceptions import RegistrationError

LICENCE_PATTERN = re.compile(r"^[A-Z]{3}\d{8}$")  # e.g. ABC12345678
SUSPENSION_THRESHOLD = 12


class Driver:
    """A licensed driver tracked by the traffic authority.

    Attributes:
        licence_no: Validated licence number, format ``AAA99999999``.
        full_name: Driver's full name.
        demerit_points: Read-only computed property backed by a strictly
            private accumulator.
        is_suspended: True once ``demerit_points`` reaches
            :data:`SUSPENSION_THRESHOLD` (12).
    """

    def __init__(self, licence_no: str, full_name: str):
        self.licence_no = licence_no  # goes through the validated setter
        if not full_name or not full_name.strip():
            raise RegistrationError(
                "full_name must not be empty.",
                field="full_name",
                value=full_name,
            )
        self._full_name = full_name.strip()
        self.__demerit_points = 0  # strictly private backing attribute
        self._suspended = False

    @property
    def licence_no(self) -> str:
        return self._licence_no

    @licence_no.setter
    def licence_no(self, value: str) -> None:
        if not isinstance(value, str) or not LICENCE_PATTERN.match(value):
            raise RegistrationError(
                f"Licence number {value!r} must match the format "
                f"AAA99999999 (3 letters, 8 digits).",
                field="licence_no",
                value=value,
            )
        self._licence_no = value

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def demerit_points(self) -> int:
        return self.__demerit_points

    @property
    def is_suspended(self) -> bool:
        return self._suspended

    def accumulate_points(self, n: int) -> None:
        """Add ``n`` demerit points to the driver's running total.

        Suspends the licence the moment the running total reaches
        :data:`SUSPENSION_THRESHOLD`. Once suspended, calling code (see
        ``src/enforcement.py``) must refuse to record further violations
        until :meth:`reinstate` is called.
        """
        if n < 0:
            raise ValueError("Demerit points to add must be non-negative.")
        self.__demerit_points += n
        if self.__demerit_points >= SUSPENSION_THRESHOLD:
            self._suspended = True

    def reinstate(self) -> None:
        """Manually reinstate a suspended licence (e.g. after a hearing or
        a remedial driving course) and reset the demerit count to zero."""
        self._suspended = False
        self.__demerit_points = 0

    def __str__(self) -> str:
        status = "SUSPENDED" if self._suspended else "ACTIVE"
        return (
            f"{self.full_name} ({self.licence_no}) — {status}, " f"{self.demerit_points} pts"
        )

    def __repr__(self) -> str:
        return f"Driver(licence_no={self.licence_no!r}, " f"full_name={self.full_name!r})"
