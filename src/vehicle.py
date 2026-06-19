"""Vehicle class hierarchy.

Defines the abstract :class:`Vehicle` base class and four concrete vehicle
types used throughout the system: :class:`Car`, :class:`Motorcycle`,
:class:`Truck` and :class:`BusRapidTransit`. Each subclass implements
``vehicle_class`` and ``annual_road_tax()`` according to its own
type-specific rules. This is the system's clearest demonstration of
polymorphism: calling ``vehicle.annual_road_tax()`` on a heterogeneous list
of vehicles returns the correct amount for each concrete type without any
``isinstance()`` checks at the call site (see ``main.py``).
"""

import re
from abc import ABC, abstractmethod

from .exceptions import RegistrationError

PLATE_PATTERN = re.compile(r"^[A-Z]{3}-\d{3}[A-Z]{2}$")


class Vehicle(ABC):
    """Abstract base class for every vehicle registered in the system.

    Attributes:
        plate_number: Validated Nigerian-style plate, e.g. ``KJA-245XY``.
        make: Manufacturer name, e.g. ``Toyota``.
        model: Model name, e.g. ``Corolla``.
        year: Manufacture year.
    """

    def __init__(self, plate_number: str, make: str, model: str, year: int):
        self.plate_number = plate_number  # goes through the validated setter
        self._make = make
        self._model = model
        self._year = year

    # ---- plate_number: validated @property --------------------------
    @property
    def plate_number(self) -> str:
        return self._plate_number

    @plate_number.setter
    def plate_number(self, value: str) -> None:
        if not isinstance(value, str) or not PLATE_PATTERN.match(value):
            raise RegistrationError(
                f"Plate number {value!r} does not match the required "
                f"format AAA-999AA (e.g. KJA-245XY).",
                field="plate_number",
                value=value,
            )
        self._plate_number = value

    @property
    def make(self) -> str:
        return self._make

    @property
    def model(self) -> str:
        return self._model

    @property
    def year(self) -> int:
        return self._year

    # ---- abstract contract --------------------------------------------
    @property
    @abstractmethod
    def vehicle_class(self) -> str:
        """Short classification code, e.g. ``'CAR'``, ``'MC'``, ``'TRK'``."""
        raise NotImplementedError

    @abstractmethod
    def annual_road_tax(self) -> float:
        """Return the annual road tax in NGN for this vehicle."""
        raise NotImplementedError

    def __str__(self) -> str:
        return (
            f"{self.vehicle_class} {self.plate_number} "
            f"({self.year} {self.make} {self.model})"
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(plate_number={self.plate_number!r}, "
            f"make={self.make!r}, model={self.model!r}, year={self.year!r})"
        )


class Car(Vehicle):
    """A private or commercial car. Taxed on a base rate plus a surcharge
    for engine displacement above 1000cc."""

    BASE_TAX_NGN = 15_000.0
    CC_RATE_NGN = 5.0  # per cc above 1000cc

    def __init__(
        self, plate_number: str, make: str, model: str, year: int, engine_capacity_cc: int
    ):
        super().__init__(plate_number, make, model, year)
        if engine_capacity_cc <= 0:
            raise RegistrationError(
                "engine_capacity_cc must be positive.",
                field="engine_capacity_cc",
                value=engine_capacity_cc,
            )
        self._engine_capacity_cc = engine_capacity_cc

    @property
    def engine_capacity_cc(self) -> int:
        return self._engine_capacity_cc

    @property
    def vehicle_class(self) -> str:
        return "CAR"

    def annual_road_tax(self) -> float:
        extra_cc = max(0, self._engine_capacity_cc - 1000)
        return self.BASE_TAX_NGN + extra_cc * self.CC_RATE_NGN


class Motorcycle(Vehicle):
    """A motorcycle ('okada'). Flat annual tax regardless of engine size."""

    BASE_TAX_NGN = 3_000.0

    def __init__(
        self, plate_number: str, make: str, model: str, year: int, engine_capacity_cc: int
    ):
        super().__init__(plate_number, make, model, year)
        if engine_capacity_cc <= 0:
            raise RegistrationError(
                "engine_capacity_cc must be positive.",
                field="engine_capacity_cc",
                value=engine_capacity_cc,
            )
        self._engine_capacity_cc = engine_capacity_cc

    @property
    def engine_capacity_cc(self) -> int:
        return self._engine_capacity_cc

    @property
    def vehicle_class(self) -> str:
        return "MC"

    def annual_road_tax(self) -> float:
        return self.BASE_TAX_NGN


class Truck(Vehicle):
    """A goods truck, taxed by maximum load capacity."""

    BASE_TAX_NGN = 25_000.0
    TONNE_RATE_NGN = 5_000.0

    def __init__(
        self, plate_number: str, make: str, model: str, year: int, max_load_tonnes: float
    ):
        super().__init__(plate_number, make, model, year)
        if max_load_tonnes <= 0:
            raise RegistrationError(
                "max_load_tonnes must be positive.",
                field="max_load_tonnes",
                value=max_load_tonnes,
            )
        self._max_load_tonnes = max_load_tonnes

    @property
    def max_load_tonnes(self) -> float:
        return self._max_load_tonnes

    @property
    def vehicle_class(self) -> str:
        return "TRK"

    def annual_road_tax(self) -> float:
        return self.BASE_TAX_NGN + self._max_load_tonnes * self.TONNE_RATE_NGN


class BusRapidTransit(Vehicle):
    """A BRT bus operating on a designated mass-transit corridor."""

    BASE_TAX_NGN = 40_000.0
    SEAT_RATE_NGN = 200.0

    def __init__(
        self,
        plate_number: str,
        make: str,
        model: str,
        year: int,
        seating_capacity: int,
        route_code: str,
    ):
        super().__init__(plate_number, make, model, year)
        if seating_capacity <= 0:
            raise RegistrationError(
                "seating_capacity must be positive.",
                field="seating_capacity",
                value=seating_capacity,
            )
        self._seating_capacity = seating_capacity
        self._route_code = route_code

    @property
    def seating_capacity(self) -> int:
        return self._seating_capacity

    @property
    def route_code(self) -> str:
        return self._route_code

    @property
    def vehicle_class(self) -> str:
        return "BRT"

    def annual_road_tax(self) -> float:
        return self.BASE_TAX_NGN + self._seating_capacity * self.SEAT_RATE_NGN
