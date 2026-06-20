"""PaymentRecord: tracks settlement of a ViolationRecord's fine."""

from datetime import datetime
from enum import Enum


class PaymentChannel(str, Enum):
    """The channel through which a fine was settled."""

    BANK = "BANK"
    POS = "POS"
    ONLINE = "ONLINE"
    USSD = "USSD"


class PaymentRecord:
    """An immutable record of a single fine payment.

    Attributes:
        violation: The :class:`~src.violation.ViolationRecord` this payment settles.
        amount_paid_ngn: Amount paid, in NGN.
        payment_date: When the payment was made.
        channel: :class:`PaymentChannel` used.
    """

    def __init__(
        self,
        violation,
        amount_paid_ngn: float,
        channel: PaymentChannel,
        payment_date: datetime | None = None,
    ):
        self._violation = violation
        self._amount_paid_ngn = float(amount_paid_ngn)
        self._channel = PaymentChannel(channel)
        self._payment_date = payment_date or datetime.now()

    @property
    def violation(self):
        return self._violation

    @property
    def amount_paid_ngn(self) -> float:
        return self._amount_paid_ngn

    @property
    def channel(self) -> PaymentChannel:
        return self._channel

    @property
    def payment_date(self) -> datetime:
        return self._payment_date

    def __str__(self) -> str:
        return (
            f"Payment of NGN {self._amount_paid_ngn:,.2f} via "
            f"{self._channel.value} for "
            f"{self._violation.violation_id[:8]}... "
            f"on {self._payment_date:%Y-%m-%d %H:%M}"
        )

    def __repr__(self) -> str:
        return (
            f"PaymentRecord(violation_id={self._violation.violation_id!r}, "
            f"amount_paid_ngn={self._amount_paid_ngn!r}, "
            f"channel={self._channel.value!r})"
        )
