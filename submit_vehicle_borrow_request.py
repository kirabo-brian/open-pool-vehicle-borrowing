
from repository_ports import VehicleBorrowRequestRepository
from vehicle_borrow_request import VehicleBorrowRequest
from repository_ports import VehiclePoolRepository
from vehicle_pool import VehiclePool
from driver import Driver
from reservation_handler import handle_reservation
from vehicle_borrow_request import RequestStatus, VehicleBorrowRequest
from dataclasses import dataclass

@dataclass(frozen=True)
class BorrowRequestResult:
    request_id: str
    status: RequestStatus

class SubmitVehicleBorrowRequest:
    def __init__(
        self,
        requests: VehicleBorrowRequestRepository,
        pools: VehiclePoolRepository,
        driver: Driver,
    ) -> None:
        self._requests = requests
        self._pools = pools
        self._driver = driver

    def _load_request(self, request_id: str) -> VehicleBorrowRequest:
        request = self._requests.get(request_id)
        if request is None:
            raise LookupError(f"Request {request_id} not found")
        return request

    def _load_pool(self, request: VehicleBorrowRequest) -> VehiclePool:
        pool = self._pools.get(request.pool_id)
        if pool is None:
            raise LookupError(f"Pool {request.pool_id} not found")
        return pool

    def execute(self, request_id: str) -> BorrowRequestResult:
        request = self._load_request(request_id)
        pool = self._load_pool(request)
        request.submit(self._driver, pool)

        for event in request.pull_events():
            handle_reservation(event, request, pool)

        if request.status is RequestStatus.CONFIRMED:
            self._pools.save(pool)

        self._requests.save(request)
        return BorrowRequestResult(request.request_id, request.status)