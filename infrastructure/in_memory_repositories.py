from typing import Optional

from application.repositories import (
    BorrowRequestRepository,
    DriverDirectory,
    VehiclePoolRepository,
)
from domain.driver import Driver
from domain.vehicle_borrow_request import VehicleBorrowRequest
from domain.vehicle_pool import VehiclePool


class InMemoryVehiclePoolRepository(VehiclePoolRepository):
    def __init__(self) -> None:
        self._store: dict = {}

    def get(self, pool_id: str) -> Optional[VehiclePool]:
        return self._store.get(pool_id)

    def save(self, pool: VehiclePool) -> None:
        self._store[pool.pool_id] = pool


class InMemoryBorrowRequestRepository(BorrowRequestRepository):
    def __init__(self) -> None:
        self._store: dict = {}

    def get(self, request_id: str) -> Optional[VehicleBorrowRequest]:
        return self._store.get(request_id)

    def save(self, request: VehicleBorrowRequest) -> None:
        self._store[request.request_id] = request

    def all(self) -> list:
        return list(self._store.values())


class InMemoryDriverDirectory(DriverDirectory):
    def __init__(self, drivers=()) -> None:
        self._store = {d.driver_id: d for d in drivers}

    def get(self, driver_id: str) -> Optional[Driver]:
        return self._store.get(driver_id)
