"""ViolationRecord: a single recorded traffic offence."""

import uuid
from datetime import datetime
from functools import total_ordering


@total_ordering
class ViolationRecord:
    """A single recorded traffic violation.

    Every field except ``paid`` is fixed at construction time, modelling
    the real-world fact that a violation's circumstances (who, what,
    where, when) cannot be edited after the fact -- only its payment
    status can change.

    Attributes:
        violation_id: UUID4 string, unique per record.
        driver: The :class:`~src.driver.Driver` who committed the offence.
        vehicle: The :class:`~src.vehicle.Vehicle` involved.
        offence_code: Code referencing a :class:`~src.penalty.PenaltySchedule` entry.
        fine_ngn: Fine amount in NGN at time of issue.
        demerit_pts: Demerit points charged for this offence.
        timestamp: When the violation occurred.
        paid: Whether the fine has been fully settled.
    """

    def __init__(
        self,
        driver,
        vehicle,
        offence_code: str,
        fine_ngn: float,
        demerit_pts: int,
        timestamp: datetime | None = None,
        enforcer_id: str | None = None,
    ):
        self._violation_id = str(uuid.uuid4())
        self._driver = driver
        self._vehicle = vehicle
        self._offence_code = offence_code
        self._fine_ngn = float(fine_ngn)
        self._demerit_pts = int(demerit_pts)
        self._timestamp = timestamp or datetime.now()
        self._enforcer_id = enforcer_id
        self._paid = False

    @property
    def violation_id(self) -> str:
        return self._violation_id

    @property
    def driver(self):
        return self._driver

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def offence_code(self) -> str:
        return self._offence_code

    @property
    def fine_ngn(self) -> float:
        return self._fine_ngn

    @property
    def demerit_pts(self) -> int:
        return self._demerit_pts

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def enforcer_id(self) -> str | None:
        return self._enforcer_id

    @property
    def paid(self) -> bool:
        return self._paid

    def mark_paid(self) -> None:
        """Flip the paid flag. Invoked only by
        :meth:`~src.dashboard.ViolationDashboard.record_payment` after it
        has validated the payment, keeping a single source of truth for
        settlement state."""
        self._paid = True

    def __eq__(self, other) -> bool:
        if not isinstance(other, ViolationRecord):
            return NotImplemented
        return self._violation_id == other._violation_id

    def __lt__(self, other) -> bool:
        if not isinstance(other, ViolationRecord):
            return NotImplemented
        return self._timestamp < other._timestamp

    def __hash__(self) -> int:
        return hash(self._violation_id)

    def __str__(self) -> str:
        status = "PAID" if self._paid else "UNPAID"
        return (
            f"[{self._timestamp:%Y-%m-%d %H:%M}] {self._offence_code} — "
            f"{self._driver.full_name} ({self._vehicle.plate_number}) "
            f"NGN {self._fine_ngn:,.2f} [{status}]"
        )

    def __repr__(self) -> str:
        return (
            f"ViolationRecord(violation_id={self._violation_id!r}, "
            f"offence_code={self._offence_code!r}, fine_ngn={self._fine_ngn!r})"
        )
