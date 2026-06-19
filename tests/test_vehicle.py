import pytest

from src.vehicle import Car, Motorcycle, Truck, BusRapidTransit
from src.exceptions import RegistrationError


@pytest.fixture
def car():
    return Car("KJA-245XY", "Toyota", "Corolla", 2019, engine_capacity_cc=1800)


# ── Construction (valid and invalid) ────────────────────────────────────


def test_valid_car_construction(car):
    assert car.plate_number == "KJA-245XY"
    assert car.vehicle_class == "CAR"


def test_invalid_plate_format_raises():
    with pytest.raises(RegistrationError) as exc_info:
        Car("INVALID", "Toyota", "Corolla", 2019, engine_capacity_cc=1800)
    assert exc_info.value.field == "plate_number"


def test_lowercase_plate_rejected():
    with pytest.raises(RegistrationError):
        Car("kja-245xy", "Toyota", "Corolla", 2019, engine_capacity_cc=1800)


def test_negative_engine_capacity_raises():
    with pytest.raises(RegistrationError):
        Car("KJA-246XY", "Toyota", "Corolla", 2019, engine_capacity_cc=-100)


def test_truck_invalid_load_raises():
    with pytest.raises(RegistrationError):
        Truck("ABJ-331TR", "MAN", "TGS", 2017, max_load_tonnes=0)


def test_brt_invalid_capacity_raises():
    with pytest.raises(RegistrationError):
        BusRapidTransit(
            "LAG-011BR", "Higer", "Bus", 2020, seating_capacity=0, route_code="BRT-Apapa"
        )


# ── Tax calculation (one per concrete subclass) ─────────────────────────


def test_car_road_tax(car):
    # 1800cc -> 800cc above 1000 at NGN5/cc => 15000 + 4000 = 19000
    assert car.annual_road_tax() == pytest.approx(19_000.0)


def test_motorcycle_flat_tax():
    bike = Motorcycle("LAG-101OK", "Bajaj", "Boxer", 2021, engine_capacity_cc=150)
    assert bike.annual_road_tax() == pytest.approx(3_000.0)


def test_truck_tax_scales_with_load():
    truck = Truck("ABJ-330TR", "MAN", "TGS", 2017, max_load_tonnes=10.0)
    assert truck.annual_road_tax() == pytest.approx(25_000.0 + 10 * 5_000.0)


def test_brt_tax_scales_with_seats():
    brt = BusRapidTransit(
        "LAG-009BR", "Higer", "Bus", 2020, seating_capacity=60, route_code="BRT-Ikorodu"
    )
    assert brt.annual_road_tax() == pytest.approx(40_000.0 + 60 * 200.0)


# ── Polymorphism: same call, four different implementations ────────────


@pytest.mark.parametrize(
    "cls,kwargs",
    [
        (
            Car,
            dict(
                plate_number="KJA-250XY",
                make="Kia",
                model="Rio",
                year=2020,
                engine_capacity_cc=1400,
            ),
        ),
        (
            Motorcycle,
            dict(
                plate_number="LAG-102OK",
                make="TVS",
                model="Star",
                year=2022,
                engine_capacity_cc=125,
            ),
        ),
        (
            Truck,
            dict(
                plate_number="ABJ-332TR",
                make="Scania",
                model="P360",
                year=2018,
                max_load_tonnes=8.0,
            ),
        ),
        (
            BusRapidTransit,
            dict(
                plate_number="LAG-010BR",
                make="Yutong",
                model="ZK6120",
                year=2021,
                seating_capacity=55,
                route_code="BRT-Oshodi",
            ),
        ),
    ],
)
def test_polymorphic_road_tax_is_positive_float(cls, kwargs):
    vehicle = cls(**kwargs)
    tax = vehicle.annual_road_tax()
    assert isinstance(tax, float)
    assert tax > 0


# ── __str__ / __repr__ ──────────────────────────────────────────────────


def test_vehicle_str_and_repr(car):
    assert car.plate_number in str(car)
    assert "Car(" in repr(car)
