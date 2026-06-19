# Design Notes — Group 3: Automated Traffic Violation Detection and Fine Management System

## 1. Why this class breakdown

The domain naturally splits into three layers, which is reflected directly in the
package structure:

- **Static reference data** — `Vehicle` hierarchy, `PenaltySchedule`. These rarely
  change once configured.
- **Mutable entities with state** — `Driver` (demerit points, suspension),
  `ViolationRecord` (paid/unpaid), `EnforcementOfficer` / `AutomaticCamera`
  (their own issued-violation history).
- **Coordination/reporting layer** — `ViolationDashboard`, which is the only class
  that is allowed to see *everything* in the system. Every other class only knows
  about its own immediate collaborators, which keeps the dependency graph shallow
  and each class independently testable (see the 76 unit tests, each of which
  instantiates only the 2-3 classes it actually needs).

## 2. Composition vs. aggregation — the key design call

`ViolationDashboard` holds references to five different kinds of object, but they
are **not** all owned the same way:

- `ViolationDashboard *-- ViolationRecord` (**composition**, filled diamond).
  A `ViolationRecord` is *created by* an `Enforceable` (officer/camera) but its
  authoritative home is the dashboard's ledger — `log_violation()` is the only
  place a record becomes "real" for reporting purposes, and once it's logged its
  lifecycle (payment status, inclusion in reports) is entirely governed by the
  dashboard. If the dashboard object were discarded, the violation ledger would
  go with it. This is why it is modelled as composition rather than aggregation.

- `ViolationDashboard o-- Driver` / `o-- EnforcementOfficer` / `o-- AutomaticCamera`
  (**aggregation**, hollow diamond). Drivers exist (and are issued licences)
  independently of whether they have ever been registered with this particular
  dashboard instance; officers are hired/assigned by the transport authority, not
  created by the dashboard. The dashboard merely *holds references* via
  `register_driver()` / `register_officer()` / `register_camera()` — these
  objects' lifecycles are independent of the dashboard's.

This distinction is enforced in code, not just on paper: `register_*()` methods
accept already-constructed objects (aggregation — the dashboard never calls
`Driver(...)` itself), whereas `log_violation()` is the dashboard's own
bookkeeping of objects that were handed to it for permanent custody.

## 3. Why `Enforceable` is a realised interface, not a regular base class

`Enforceable` has exactly one abstract method and no shared implementation at
all — it exists purely to guarantee that `EnforcementOfficer` and
`AutomaticCamera` both expose `record_violation(...)` with the same signature,
so that calling code (and `ViolationDashboard`, if extended to dispatch
enforcement generically) can treat them interchangeably. Because it carries no
behaviour of its own, it is diagrammed with the `<<interface>>` stereotype and
connected via **realization** (dashed arrow, hollow triangle) rather than
generalization — distinguishing it from `Vehicle`, which *does* carry shared
state and behaviour (`plate_number` validation, `__str__`/`__repr__`) and is
therefore diagrammed as a true abstract base class with **generalization**
arrows to its four concrete subclasses.

## 4. Exception design

All four custom exceptions inherit from `TrafficSystemError`, which itself
carries a `timestamp` set at the moment of construction — useful for audit
logging without any extra plumbing at the call site. Rather than relying on
exception *message text* for callers to branch on, every exception carries
structured fields (`field`/`value` on `RegistrationError`, `driver_id`/
`offence_code` on `ViolationError`, `violation_id`/`amount_ngn` on
`PaymentError`). The test suite asserts against these fields directly
(see `tests/test_vehicle.py::test_invalid_plate_format_raises`) rather than
matching on message wording, which keeps the tests stable even if the
human-readable message copy is improved later.

## 5. Why payment validation rejects both over- and under-payment

The brief calls out overpayment and repeat-payment explicitly. We additionally
reject underpayment for the same reason stated in the brief — *"the full fine
amount must be paid in one transaction"* — partial payment is simply not a
state the model supports; a driver either owes the full fine or has settled it.
This is a deliberate simplification, documented honestly in
`README.md → Known Limitations`, rather than silently allowing partial
settlement.

## 6. Why `ViolationRecord` has no setters except `mark_paid()`

A real traffic violation's facts (who, what, when, where, how much) cannot be
edited after issuance without creating an audit trail problem. Modelling every
field except `paid` as read-only mirrors that real-world constraint directly in
the type system, rather than relying on convention or documentation to prevent
accidental mutation.

## 7. Polymorphism in practice

Two call sites in `main.py` demonstrate genuine polymorphism (not just
inheritance):

- `vehicle.annual_road_tax()` is called identically on `Car`, `Motorcycle`,
  `Truck`, and `BusRapidTransit` instances in a single loop — each returns a
  different value computed by a completely different formula.
- `officer1 + officer2` invokes `EnforcementOfficer.__add__`, returning a
  merged, chronologically sorted list — demonstrating operator overloading
  rather than a named method, which lets `sorted()` and Python's own
  `total_ordering`-style comparisons fall out of `ViolationRecord.__lt__`
  for free.
