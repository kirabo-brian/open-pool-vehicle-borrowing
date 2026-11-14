from application.repositories import BorrowRequestRepository, VehiclePoolRepository
from domain.errors import VehicleAlreadyReserved
from domain.events import VehicleBorrowRequestSubmitted


class ReserveVehiclesOnRequestSubmitted:
    """Use case 2 / BR5 handler: asks Aggregate B (VehiclePool) to reserve.

    The pool enforces its own rule. The handler only reports the outcome
    back onto the request (confirm or reject_reservation).
    """

    def __init__(
        self, pools: VehiclePoolRepository, requests: BorrowRequestRepository
    ) -> None:
        self._pools = pools
        self._requests = requests

    def __call__(self, event: VehicleBorrowRequestSubmitted) -> None:
        request = self._requests.get(event.request_id)
        pool = self._pools.get(event.pool_id)
        try:
            pool.reserve_all(event.request_id, event.vehicle_ids)
        except VehicleAlreadyReserved:
            request.reject_reservation()
        else:
            self._pools.save(pool)
            request.confirm()
        self._requests.save(request)
