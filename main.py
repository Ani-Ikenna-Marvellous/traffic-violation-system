"""Entry point: demonstrates the full Traffic Violation Detection and Fine
Management System workflow end-to-end.

Run with:  python main.py
"""

from datetime import datetime, timedelta

from src.vehicle import Car, Motorcycle, Truck, BusRapidTransit
from src.driver import Driver
from src.penalty import PenaltySchedule
from src.enforcement import EnforcementOfficer, AutomaticCamera
from src.dashboard import ViolationDashboard
from src.payment import PaymentChannel
from src.exceptions import ViolationError, PaymentError


def main() -> None:
    schedule = PenaltySchedule.default()
    dashboard = ViolationDashboard()

    # ---- register vehicles -------------------------------------------
    car = Car("KJA-245XY", "Toyota", "Corolla", 2019, engine_capacity_cc=1800)
    bike = Motorcycle("LAG-101OK", "Bajaj", "Boxer", 2021, engine_capacity_cc=150)
    truck = Truck("ABJ-330TR", "MAN", "TGS", 2017, max_load_tonnes=12.0)
    brt = BusRapidTransit(
        "LAG-009BR", "Higer", "Bus", 2020, seating_capacity=60, route_code="BRT-Ikorodu"
    )

    # ---- register drivers ----------------------------------------------
    israel = Driver("ANJ20231031", "Anjoorin Israel Ayomide")
    chiedoziem = Driver("ANU20231032", "Anugwara Chiedoziem Chinonyerem")
    dashboard.register_driver(israel)
    dashboard.register_driver(chiedoziem)

    # ---- register enforcers ---------------------------------------------
    officer1 = EnforcementOfficer("OFF-1001", "Insp. Bello", "Ikeja Zone")
    officer2 = EnforcementOfficer("OFF-1002", "Insp. Adeyemi", "Lekki Zone")
    camera1 = AutomaticCamera("CAM-5001", "Third Mainland Bridge", speed_limit_kmh=80)
    dashboard.register_officer(officer1)
    dashboard.register_officer(officer2)
    dashboard.register_camera(camera1)

    now = datetime(2026, 6, 1, 8, 0)

    print("=" * 60)
    print("1. MANUAL VIOLATIONS RECORDED BY OFFICERS")
    print("=" * 60)
    v1 = officer1.record_violation(israel, car, "NO_SEATBELT", schedule, now)
    dashboard.log_violation(v1)
    print(" ", v1)

    v2 = officer1.record_violation(
        israel, car, "PHONE_WHILE_DRIVING", schedule, now + timedelta(minutes=10)
    )
    dashboard.log_violation(v2)
    print(" ", v2)

    v3 = officer2.record_violation(
        chiedoziem, bike, "EXPIRED_LICENCE", schedule, now + timedelta(minutes=20)
    )
    dashboard.log_violation(v3)
    print(" ", v3)

    print("\n" + "=" * 60)
    print("2. AUTOMATIC CAMERA SPEED DETECTION")
    print("=" * 60)
    for speed in (95, 130, 75):  # 15 over (minor), 50 over (major), within limit
        v = camera1.detect_and_record(
            chiedoziem, bike, speed, schedule, now + timedelta(minutes=30)
        )
        if v:
            dashboard.log_violation(v)
            print(f"   Detected {speed} km/h -> {v}")
        else:
            print(f"   Detected {speed} km/h -> within limit, no violation.")

    print("\n" + "=" * 60)
    print("3. PUSHING ISRAEL TOWARDS LICENCE SUSPENSION (>= 12 demerit pts)")
    print("=" * 60)
    for code in ("OVERLOADING", "RUNNING_RED_LIGHT", "WRONG_WAY"):
        try:
            v = officer1.record_violation(israel, car, code, schedule, now + timedelta(hours=1))
            dashboard.log_violation(v)
            print(
                f"   {code}: total {israel.demerit_points} pts, "
                f"suspended={israel.is_suspended}"
            )
        except ViolationError as exc:
            print(f"   {code}: BLOCKED -- {exc}")

    print("\n" + "=" * 60)
    print("4. PAYMENT PROCESSING")
    print("=" * 60)
    payment = dashboard.record_payment(v1, v1.fine_ngn, PaymentChannel.POS)
    print(" ", payment)

    try:
        dashboard.record_payment(v1, v1.fine_ngn, PaymentChannel.ONLINE)
    except PaymentError as exc:
        print(f"   Repayment correctly blocked: {exc}")

    try:
        dashboard.record_payment(v2, v2.fine_ngn + 5_000, PaymentChannel.BANK)
    except PaymentError as exc:
        print(f"   Overpayment correctly blocked: {exc}")

    print("\n" + "=" * 60)
    print("5. SHIFT HANDOVER (officer1 + officer2, chronological merge)")
    print("=" * 60)
    for v in officer1 + officer2:
        print(" ", v)

    print("\n" + dashboard.dashboard_report())

    print("\n" + "=" * 60)
    print("6. POLYMORPHIC ANNUAL ROAD TAX (same call, four implementations)")
    print("=" * 60)
    for vehicle in (car, bike, truck, brt):
        print(f"  {vehicle}: NGN {vehicle.annual_road_tax():,.2f}")


if __name__ == "__main__":
    main()
