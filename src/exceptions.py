"""Custom exception hierarchy for the Traffic Violation Detection and Fine
Management System (Group 3 Capstone, CPE 310).

Every system-specific exception inherits from :class:`TrafficSystemError` so
calling code can catch every domain error with a single except clause while
still being able to discriminate on the more specific subclasses when it
matters. Each exception carries structured diagnostic fields rather than a
single opaque message string, which makes the exceptions useful both to a
human reading a traceback and to calling code that wants to react
programmatically (log a field name, display a value to a user, etc).
"""

from datetime import datetime


class TrafficSystemError(Exception):
    """Base class for every exception raised by this system.

    Attributes:
        detail: Human readable explanation of what went wrong.
        timestamp: When the error was constructed.
    """

    def __init__(self, detail: str):
        self.detail = detail
        self.timestamp = datetime.now()
        super().__init__(detail)


class ViolationError(TrafficSystemError, ValueError):
    """Raised when a violation cannot be recorded as requested (e.g. the
    driver is currently suspended, or the offence code does not exist).

    Attributes:
        driver_id: Licence number of the driver involved, if known.
        offence_code: The offence code that triggered the error, if any.
    """

    def __init__(
        self, detail: str, driver_id: str | None = None, offence_code: str | None = None
    ):
        self.driver_id = driver_id
        self.offence_code = offence_code
        super().__init__(detail)


class PaymentError(TrafficSystemError):
    """Raised for invalid payment attempts: overpayment, underpayment, or
    an attempt to re-pay an already-settled violation.

    Attributes:
        violation_id: The violation the payment was attempted against.
        amount_ngn: The amount that was rejected.
    """

    def __init__(
        self, detail: str, violation_id: str | None = None, amount_ngn: float | None = None
    ):
        self.violation_id = violation_id
        self.amount_ngn = amount_ngn
        super().__init__(detail)


class RegistrationError(TrafficSystemError, ValueError):
    """Raised when a registration field (plate number, licence number,
    badge number, camera id, fine amount, etc.) fails format or range
    validation.

    Attributes:
        field: Name of the offending field.
        value: The rejected value.
    """

    def __init__(self, detail: str, field: str | None = None, value=None):
        self.field = field
        self.value = value
        super().__init__(detail)
