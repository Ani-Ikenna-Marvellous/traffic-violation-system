import pytest

from src.dashboard import ViolationDashboard
from src.penalty import PenaltySchedule
from src.enforcement import EnforcementOfficer
from src.driver import Driver, SUSPENSION_THRESHOLD
from src.vehicle import Car
from src.payment import PaymentChannel
from src.exceptions import PaymentError


@pytest.fixture
def setup():
    schedule = PenaltySchedule.default()
    dashboard = ViolationDashboard()
    officer = EnforcementOfficer("OFF-3001", "Insp. Bello", "Ikeja Zone")
    driver = Driver("ABC12345678", "Chidi Okafor")
    vehicle = Car("KJA-245XY", "Toyota", "Corolla", 2019, engine_capacity_cc=1800)
    dashboard.register_driver(driver)
    dashboard.register_officer(officer)
    return dashboard, schedule, officer, driver, vehicle


def test_log_violation_increases_length_and_contains(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    v = officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)
    dashboard.log_violation(v)
    assert len(dashboard) == 1
    assert v.violation_id in dashboard


def test_total_fines_issued(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    v = officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)
    dashboard.log_violation(v)
    assert dashboard.total_fines_issued() == v.fine_ngn


def test_record_payment_success_updates_revenue(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    v = officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)
    dashboard.log_violation(v)
    dashboard.record_payment(v, v.fine_ngn, PaymentChannel.POS)
    assert dashboard.revenue_collected() == v.fine_ngn
    assert dashboard.outstanding_fines() == 0
    assert v.paid is True


def test_record_payment_rejects_repayment(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    v = officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)
    dashboard.log_violation(v)
    dashboard.record_payment(v, v.fine_ngn, PaymentChannel.POS)
    with pytest.raises(PaymentError):
        dashboard.record_payment(v, v.fine_ngn, PaymentChannel.ONLINE)


def test_record_payment_rejects_overpayment(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    v = officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)
    dashboard.log_violation(v)
    with pytest.raises(PaymentError):
        dashboard.record_payment(v, v.fine_ngn + 1, PaymentChannel.BANK)


def test_record_payment_rejects_underpayment(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    v = officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)
    dashboard.log_violation(v)
    with pytest.raises(PaymentError):
        dashboard.record_payment(v, v.fine_ngn - 1, PaymentChannel.BANK)


def test_top_offences_ranks_by_frequency(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    for code in ("NO_SEATBELT", "NO_SEATBELT", "ILLEGAL_PARKING"):
        v = officer.record_violation(driver, vehicle, code, schedule)
        dashboard.log_violation(v)
    top = dashboard.top_offences(2)
    assert top[0] == ("NO_SEATBELT", 2)


def test_suspended_drivers_lists_only_suspended(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    assert dashboard.suspended_drivers() == []
    driver.accumulate_points(SUSPENSION_THRESHOLD)
    assert driver in dashboard.suspended_drivers()


def test_dashboard_report_contains_key_sections(setup):
    dashboard, schedule, officer, driver, vehicle = setup
    v = officer.record_violation(driver, vehicle, "NO_SEATBELT", schedule)
    dashboard.log_violation(v)
    report = dashboard.dashboard_report()
    assert "Top offences" in report
    assert "Total revenue collected" in report
    assert "Suspended drivers" in report
