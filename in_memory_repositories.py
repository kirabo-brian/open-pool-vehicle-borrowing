from identifiers import clean_id
from repository_ports import VehicleBorrowRequestRepository, VehiclePoolRepository
from vehicle_borrow_request import VehicleBorrowRequest
from vehicle_pool import VehiclePool


class InMemoryVehicleBorrowRequestRepository(VehicleBorrowRequestRepository):
    def __init__(self) -> None:
        self._requests: dict[str, VehicleBorrowRequest] = {}

    def get(self, request_id: str) -> VehicleBorrowRequest | None:
        return self._requests.get(clean_id(request_id, "Request ID"))

    def save(self, request: VehicleBorrowRequest) -> None:
        self._requests[request.request_id] = request


class InMemoryVehiclePoolRepository(VehiclePoolRepository):
    def __init__(self) -> None:
        self._pools: dict[str, VehiclePool] = {}

    def get(self, pool_id: str) -> VehiclePool | None:
        return self._pools.get(clean_id(pool_id, "Pool ID"))

    def save(self, pool: VehiclePool) -> None:
        self._pools[pool.pool_id] = pool
