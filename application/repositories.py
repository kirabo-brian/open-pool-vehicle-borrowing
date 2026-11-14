from abc import ABC, abstractmethod
from typing import Optional

from domain.driver import Driver
from domain.vehicle_borrow_request import VehicleBorrowRequest
from domain.vehicle_pool import VehiclePool


class VehiclePoolRepository(ABC):
    @abstractmethod
    def get(self, pool_id: str) -> Optional[VehiclePool]: ...

    @abstractmethod
    def save(self, pool: VehiclePool) -> None: ...


class BorrowRequestRepository(ABC):
    @abstractmethod
    def get(self, request_id: str) -> Optional[VehicleBorrowRequest]: ...

    @abstractmethod
    def save(self, request: VehicleBorrowRequest) -> None: ...


class DriverDirectory(ABC):
    """Read-only lookup of driver records. Driver is reference data, not an
    aggregate root, so this is a lookup port rather than a repository."""

    @abstractmethod
    def get(self, driver_id: str) -> Optional[Driver]: ...
