"""Interface layer: minimal entry point and composition root.

Run:  py -B -m interface.cli
"""
from application.dtos import SubmitVehicleBorrowRequestCommand
from application.reserve_vehicles_handler import ReserveVehiclesOnRequestSubmitted
from application.submit_vehicle_borrow_request import SubmitVehicleBorrowRequestService
from domain.driver import Driver
from domain.events import VehicleBorrowRequestSubmitted
from domain.vehicle_category import VehicleCategory
from domain.vehicle_pool import VehiclePool
from infrastructure.in_memory_repositories import (
    InMemoryBorrowRequestRepository,
    InMemoryDriverDirectory,
    InMemoryVehiclePoolRepository,
)
from infrastructure.in_process_event_bus import InProcessEventBus


def build_service() -> SubmitVehicleBorrowRequestService:
    pools = InMemoryVehiclePoolRepository()
    requests = InMemoryBorrowRequestRepository()
    drivers = InMemoryDriverDirectory(
        [Driver("D1", frozenset({VehicleCategory.CAR, VehicleCategory.TRUCK}))]
    )
    bus = InProcessEventBus()
    bus.subscribe(
        VehicleBorrowRequestSubmitted, ReserveVehiclesOnRequestSubmitted(pools, requests)
    )
    pools.save(
        VehiclePool("POOL-1", {"CAR-01": VehicleCategory.CAR, "TRUCK-01": VehicleCategory.TRUCK})
    )
    return SubmitVehicleBorrowRequestService(pools, requests, drivers, bus)


def main() -> None:
    service = build_service()
    print(service.execute(
        SubmitVehicleBorrowRequestCommand("R1", "D1", "POOL-1", ("TRUCK-01",), 3)))
    print(service.execute(  # TRUCK-01 is taken, so the pool rejects both vehicles
        SubmitVehicleBorrowRequestCommand("R2", "D1", "POOL-1", ("CAR-01", "TRUCK-01"), 2)))


if __name__ == "__main__":
    main()
