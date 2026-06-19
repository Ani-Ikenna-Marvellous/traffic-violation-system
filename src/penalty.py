"""PenaltySchedule: maps offence codes to (description, fine_ngn, demerit_pts)."""

from dataclasses import dataclass

from .exceptions import RegistrationError


@dataclass(frozen=True)
class Offence:
    """Immutable description of a single offence type."""

    code: str
    description: str
    fine_ngn: float
    demerit_pts: int


# The 10 mandatory offence codes required by the project brief.
DEFAULT_OFFENCES = {
    "SPEEDING_MINOR": ("Exceeding the speed limit by 1-20 km/h", 15_000.0, 2),
    "SPEEDING_MAJOR": ("Exceeding the speed limit by more than 20 km/h", 50_000.0, 6),
    "NO_SEATBELT": ("Driving without a fastened seatbelt", 5_000.0, 1),
    "WRONG_WAY": ("Driving against traffic / one-way violation", 30_000.0, 5),
    "EXPIRED_LICENCE": ("Driving with an expired licence", 20_000.0, 3),
    "OVERLOADING": ("Carrying passengers or cargo above rated capacity", 25_000.0, 4),
    "RUNNING_RED_LIGHT": ("Failure to stop at a red traffic light", 20_000.0, 4),
    "NO_INSURANCE": ("Operating a vehicle without valid insurance", 40_000.0, 4),
    "PHONE_WHILE_DRIVING": ("Use of a handheld phone while driving", 10_000.0, 3),
    "ILLEGAL_PARKING": ("Parking in a restricted or obstructive zone", 7_500.0, 1),
}


class PenaltySchedule:
    """A configurable table of ``offence_code -> Offence``.

    Kept as its own class (rather than a bare dict) so the fine schedule
    can be validated once at construction time and swapped out per
    jurisdiction without touching any other class in the system.
    """

    def __init__(self, offences: dict | None = None):
        self._offences: dict = offences or {}

    @classmethod
    def from_dict(cls, config: dict) -> "PenaltySchedule":
        """Build a PenaltySchedule from a plain dict of
        ``code -> (description, fine_ngn, demerit_pts)`` tuples."""
        offences = {}
        for code, (description, fine_ngn, demerit_pts) in config.items():
            if fine_ngn <= 0:
                raise RegistrationError(
                    f"fine_ngn for {code} must be positive.",
                    field="fine_ngn",
                    value=fine_ngn,
                )
            if demerit_pts < 0:
                raise RegistrationError(
                    f"demerit_pts for {code} must be non-negative.",
                    field="demerit_pts",
                    value=demerit_pts,
                )
            offences[code] = Offence(code, description, float(fine_ngn), int(demerit_pts))
        return cls(offences)

    @classmethod
    def default(cls) -> "PenaltySchedule":
        """Return a schedule pre-populated with the 10 mandatory offence
        codes from the project brief."""
        return cls.from_dict(DEFAULT_OFFENCES)

    def lookup(self, offence_code: str) -> Offence:
        try:
            return self._offences[offence_code]
        except KeyError as exc:
            raise RegistrationError(
                f"Unknown offence code {offence_code!r}.",
                field="offence_code",
                value=offence_code,
            ) from exc

    def __contains__(self, offence_code: str) -> bool:
        return offence_code in self._offences

    def __len__(self) -> int:
        return len(self._offences)

    def __iter__(self):
        return iter(self._offences.values())

    def __str__(self) -> str:
        return f"PenaltySchedule({len(self)} offences)"

    def __repr__(self) -> str:
        return f"PenaltySchedule(codes={list(self._offences)!r})"
