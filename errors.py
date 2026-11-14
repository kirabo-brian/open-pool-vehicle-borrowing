"""Domain errors for Open Pool Vehicle Borrowing."""


class DomainError(Exception):
    """Base class for every business-rule violation."""


class InvalidDuration(DomainError, ValueError):
    """BR1: duration is not 1 to 7 whole days."""


class InvalidRequest(DomainError, ValueError):
    """BR3: empty vehicle list, duplicate vehicle ID or blank ID."""


class RequestAlreadySubmitted(DomainError):
    """BR2: only a draft request can be submitted."""


class InvalidTransition(DomainError):
    """Status change not allowed from the current status."""


class DriverMismatch(DomainError):
    """The driver supplied is not the driver on the request."""


class DriverNotQualified(DomainError):
    """BR4: driver lacks a qualification for a requested category."""


class PoolMismatch(DomainError):
    """The pool supplied is not the pool on the request."""


class VehicleNotInPool(DomainError):
    """BR6: a requested vehicle is not in the selected pool."""


class VehicleAlreadyReserved(DomainError):
    """BR5: a requested vehicle has an active reservation for another request."""
