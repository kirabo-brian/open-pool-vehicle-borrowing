from typing import Protocol

from vehicle_borrow_request import VehicleBorrowRequest
from vehicle_pool import VehiclePool


class VehicleBorrowRequestRepository(Protocol):
    def get(self, request_id: str) -> VehicleBorrowRequest | None: ...

    def save(self, request: VehicleBorrowRequest) -> None: ...


class VehiclePoolRepository(Protocol):
    def get(self, pool_id: str) -> VehiclePool | None: ...

    def save(self, pool: VehiclePool) -> None: ...
