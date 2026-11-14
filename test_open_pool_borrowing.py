"""T1, T2, T4-T8. (T3 lives in test_vehicle_borrow_request.py.)"""
import unittest

from application.dtos import SubmitVehicleBorrowRequestCommand
from application.errors import PoolNotFound, RequestAlreadyExists
from application.reserve_vehicles_handler import ReserveVehiclesOnRequestSubmitted
from application.submit_vehicle_borrow_request import SubmitVehicleBorrowRequestService
from domain.borrowing_duration import BorrowingDuration
from domain.driver import Driver
from domain.errors import (
    DriverNotQualified,
    InvalidDuration,
    InvalidTransition,
    RequestAlreadySubmitted,
    VehicleAlreadyReserved,
    VehicleNotInPool,
)
from domain.events import VehicleBorrowRequestSubmitted
from domain.vehicle_borrow_request import RequestStatus, VehicleBorrowRequest
from domain.vehicle_category import VehicleCategory
from domain.vehicle_pool import VehiclePool
from infrastructure.in_memory_repositories import (
    InMemoryBorrowRequestRepository,
    InMemoryDriverDirectory,
    InMemoryVehiclePoolRepository,
)
from infrastructure.in_process_event_bus import InProcessEventBus

CAR, TRUCK = VehicleCategory.CAR, VehicleCategory.TRUCK


def make_pool():
    return VehiclePool("POOL-1", {"CAR-01": CAR, "CAR-02": CAR, "TRUCK-01": TRUCK})


def make_request(vehicle_ids=("CAR-01",), request_id="R1"):
    return VehicleBorrowRequest(request_id, "D1", "POOL-1", vehicle_ids, BorrowingDuration(3))


def build_app():
    """Dependency injection: implementations are supplied from outside."""
    pools = InMemoryVehiclePoolRepository()
    requests = InMemoryBorrowRequestRepository()
    drivers = InMemoryDriverDirectory([Driver("D1", frozenset({CAR, TRUCK}))])
    bus = InProcessEventBus()
    bus.subscribe(
        VehicleBorrowRequestSubmitted, ReserveVehiclesOnRequestSubmitted(pools, requests)
    )
    pools.save(make_pool())
    service = SubmitVehicleBorrowRequestService(pools, requests, drivers, bus)
    return service, pools, requests


def command(request_id="R1", vehicles=("CAR-01",), pool="POOL-1", driver="D1", days=3):
    return SubmitVehicleBorrowRequestCommand(request_id, driver, pool, tuple(vehicles), days)


class OpenPoolBorrowingTests(unittest.TestCase):
    def test_t1_duration_value_rule(self):
        # boundaries: 1 and 7 whole days are valid
        self.assertEqual(BorrowingDuration(1).days, 1)
        self.assertEqual(BorrowingDuration(7).days, 7)
        # rejections: too short, too long, not whole, boolean
        for bad in (0, 8, 2.5, True):
            with self.subTest(days=bad), self.assertRaises(InvalidDuration):
                BorrowingDuration(bad)

    def test_t2_request_state_rule(self):
        request = make_request()
        driver, pool = Driver("D1", frozenset({CAR})), make_pool()
        request.submit(driver, pool)
        self.assertEqual(request.status, RequestStatus.SUBMITTED)
        with self.assertRaises(RequestAlreadySubmitted):
            request.submit(driver, pool)  # rejection: only a DRAFT can be submitted
        self.assertEqual(len(request.pull_events()), 1)  # exactly one event
        request.confirm()
        with self.assertRaises(InvalidTransition):
            request.confirm()  # rejection: only SUBMITTED can be confirmed

    # test_t3_rejects_duplicate_vehicle_ids is in test_vehicle_borrow_request.py

    def test_t4_driver_must_be_qualified(self):
        request = make_request(("TRUCK-01",))
        car_only = Driver("D1", frozenset({CAR}))
        with self.assertRaises(DriverNotQualified):
            request.submit(car_only, make_pool())
        self.assertEqual(request.status, RequestStatus.DRAFT)
        self.assertEqual(request.pull_events(), [])

    def test_t5_pool_reserves_all_or_none(self):
        pool = make_pool()
        pool.reserve_all("R1", ["CAR-01", "TRUCK-01"])
        self.assertEqual(pool.reservation_for("CAR-01"), "R1")
        self.assertEqual(pool.reservation_for("TRUCK-01"), "R1")
        with self.assertRaises(VehicleAlreadyReserved):
            pool.reserve_all("R2", ["CAR-02", "TRUCK-01"])  # rejection
        self.assertIsNone(pool.reservation_for("CAR-02"))  # nothing was changed
        pool.reserve_all("R1", ["CAR-01"])  # same request may retry

    def test_t6_lookup_rule(self):
        service, _, requests = build_app()
        with self.assertRaises(PoolNotFound):
            service.execute(command(pool="NO-POOL"))
        self.assertIsNone(requests.get("R1"))  # nothing created or saved
        with self.assertRaises(VehicleNotInPool):
            service.execute(command(vehicles=("CAR-01", "BUS-99")))
        self.assertEqual(requests.get("R1").status, RequestStatus.DRAFT)
        # rejection: a request ID that already exists cannot be submitted again
        service, pools, requests = build_app()
        service.execute(command("R2", vehicles=("CAR-01",)))
        with self.assertRaises(RequestAlreadyExists):
            service.execute(command("R2", vehicles=("TRUCK-01",)))
        self.assertEqual(requests.get("R2").vehicle_ids, ("CAR-01",))
        self.assertEqual(requests.get("R2").status, RequestStatus.CONFIRMED)
        self.assertIsNone(pools.get("POOL-1").reservation_for("TRUCK-01"))

    def test_t7_main_use_case_event_handled_and_pool_updated(self):
        service, pools, requests = build_app()
        result = service.execute(command(vehicles=("CAR-01", "TRUCK-01")))
        self.assertEqual(result.status, "CONFIRMED")
        self.assertEqual(result.vehicle_ids, ("CAR-01", "TRUCK-01"))
        self.assertEqual(requests.get("R1").status, RequestStatus.CONFIRMED)
        pool = pools.get("POOL-1")
        self.assertEqual(pool.reservation_for("CAR-01"), "R1")
        self.assertEqual(pool.reservation_for("TRUCK-01"), "R1")

    def test_t8_pool_rejects_follow_up_when_vehicle_taken(self):
        service, pools, requests = build_app()
        first = service.execute(command("R-OLD", vehicles=("TRUCK-01",)))
        second = service.execute(command("R-NEW", vehicles=("CAR-01", "TRUCK-01")))
        self.assertEqual(first.status, "CONFIRMED")
        self.assertEqual(second.status, "RESERVATION_REJECTED")
        self.assertEqual(requests.get("R-NEW").status, RequestStatus.RESERVATION_REJECTED)
        pool = pools.get("POOL-1")
        self.assertEqual(pool.reservation_for("TRUCK-01"), "R-OLD")  # old holder kept
        self.assertIsNone(pool.reservation_for("CAR-01"))  # all or none


if __name__ == "__main__":
    unittest.main()
