from enum import Enum

from borrowing_duration import BorrowingDuration
from driver import DriverEligibilityService
from errors import (
    DriverMismatch,
    InvalidRequest,
    InvalidTransition,
    PoolMismatch,
    RequestAlreadySubmitted,
    VehicleNotInPool,
)
from events import VehicleBorrowRequestSubmitted
from identifiers import clean_id


class RequestStatus(Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    CONFIRMED = "CONFIRMED"
    RESERVATION_REJECTED = "RESERVATION_REJECTED"


class VehicleBorrowRequest:
    """Aggregate root. Owns request status and requested vehicle IDs (BR2, BR3)."""

    def __init__(self, request_id, driver_id, pool_id, vehicle_ids, duration) -> None:
        ids = tuple(clean_id(v, "Vehicle ID") for v in vehicle_ids)
        if not ids:
            raise InvalidRequest("Request must contain at least one vehicle")  # BR3
        if len(set(ids)) != len(ids):
            raise InvalidRequest("Duplicate vehicle ID")  # BR3
        if not isinstance(duration, BorrowingDuration):
            raise TypeError("duration must be a BorrowingDuration")  # BR1
        self._request_id = clean_id(request_id, "Request ID")
        self._driver_id = clean_id(driver_id, "Driver ID")
        self._pool_id = clean_id(pool_id, "Pool ID")
        self._vehicle_ids = ids
        self._duration = duration
        self._status = RequestStatus.DRAFT
        self._events = []

    @property
    def request_id(self):
        return self._request_id

    @property
    def driver_id(self):
        return self._driver_id

    @property
    def pool_id(self):
        return self._pool_id

    @property
    def vehicle_ids(self):
        return self._vehicle_ids

    @property
    def duration(self):
        return self._duration

    @property
    def status(self):
        return self._status

    def submit(self, driver, pool) -> None:
        """Move DRAFT to SUBMITTED and record one event. Any failure leaves DRAFT."""
        if self._status is not RequestStatus.DRAFT:
            raise RequestAlreadySubmitted(self._request_id)  # BR2
        if driver.driver_id != self._driver_id:
            raise DriverMismatch(f"{driver.driver_id} is not {self._driver_id}")
        if pool.pool_id != self._pool_id:
            raise PoolMismatch(f"{pool.pool_id} is not {self._pool_id}")
        missing = [v for v in self._vehicle_ids if not pool.contains_all((v,))]
        if missing:
            raise VehicleNotInPool(", ".join(missing))  # BR6
        DriverEligibilityService.check(driver, pool.categories_of(self._vehicle_ids))  # BR4

        self._status = RequestStatus.SUBMITTED
        self._events.append(
            VehicleBorrowRequestSubmitted(
                self._request_id,
                self._pool_id,
                self._driver_id,
                self._vehicle_ids,
                self._duration.days,
            )
        )

    def confirm(self) -> None:
        self._require_submitted("confirm")
        self._status = RequestStatus.CONFIRMED

    def reject_reservation(self) -> None:
        self._require_submitted("reject")
        self._status = RequestStatus.RESERVATION_REJECTED

    def pull_events(self):
        """Return recorded events and clear them so each is published once."""
        events, self._events = self._events, []
        return events

    def _require_submitted(self, action) -> None:
        if self._status is not RequestStatus.SUBMITTED:
            raise InvalidTransition(f"Cannot {action} from {self._status.value}")
