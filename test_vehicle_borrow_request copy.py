import unittest

from domain.borrowing_duration import BorrowingDuration
from domain.vehicle_borrow_request import VehicleBorrowRequest


class VehicleBorrowRequestTests(unittest.TestCase):
    def test_t3_rejects_duplicate_vehicle_ids(self):
        with self.assertRaisesRegex(ValueError, "Duplicate vehicle ID"):
            VehicleBorrowRequest(
                "R1", "D1", "POOL-1",
                ("CAR-01", "TRUCK-01", "CAR-01"),
                BorrowingDuration(3),
            )
