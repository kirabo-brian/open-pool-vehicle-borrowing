from application.dtos import (
    SubmitVehicleBorrowRequestCommand,
    SubmitVehicleBorrowRequestResult,
)
from application.errors import DriverNotFound, PoolNotFound, RequestAlreadyExists
from application.event_publisher import EventPublisher
from application.repositories import (
    BorrowRequestRepository,
    DriverDirectory,
    VehiclePoolRepository,
)
from domain.borrowing_duration import BorrowingDuration
from domain.identifiers import clean_id
from domain.vehicle_borrow_request import RequestStatus, VehicleBorrowRequest

MESSAGES = {
    RequestStatus.CONFIRMED: "Vehicles reserved",
    RequestStatus.RESERVATION_REJECTED: "A requested vehicle is already reserved",
    RequestStatus.SUBMITTED: "Submitted, reservation pending",
    RequestStatus.DRAFT: "Draft",
}


class SubmitVehicleBorrowRequestService:
    """Use case 1. Coordinates only; every business rule lives in the domain.

    Collaborators are supplied from outside (dependency injection).
    """

    def __init__(
        self,
        pools: VehiclePoolRepository,
        requests: BorrowRequestRepository,
        drivers: DriverDirectory,
        publisher: EventPublisher,
    ) -> None:
        self._pools = pools
        self._requests = requests
        self._drivers = drivers
        self._publisher = publisher

    def execute(
        self, command: SubmitVehicleBorrowRequestCommand
    ) -> SubmitVehicleBorrowRequestResult:
        # BR6: retrieve what we need before anything is created or saved.
        pool = self._pools.get(clean_id(command.pool_id, "Pool ID"))
        if pool is None:
            raise PoolNotFound(command.pool_id)
        driver = self._drivers.get(clean_id(command.driver_id, "Driver ID"))
        if driver is None:
            raise DriverNotFound(command.driver_id)
        if self._requests.get(clean_id(command.request_id, "Request ID")) is not None:
            raise RequestAlreadyExists(command.request_id)  # never overwrite a request

        # BR1 and BR3 are enforced by these constructors.
        request = VehicleBorrowRequest(
            command.request_id,
            command.driver_id,
            command.pool_id,
            command.vehicle_ids,
            BorrowingDuration(command.duration_days),
        )
        self._requests.save(request)  # saved as DRAFT

        # BR2, BR4, BR6: the aggregate decides. A failure raises and the
        # saved request stays DRAFT.
        request.submit(driver, pool)
        self._requests.save(request)

        for event in request.pull_events():
            self._publisher.publish(event)  # BR5 follow-up, in-process

        final = self._requests.get(request.request_id)
        return SubmitVehicleBorrowRequestResult(
            request_id=final.request_id,
            status=final.status.value,
            vehicle_ids=final.vehicle_ids,
            message=MESSAGES[final.status],
        )
