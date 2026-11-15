
from borrowing_duration import BorrowingDuration
from driver import Driver
from in_memory_repositories import (
    InMemoryVehicleBorrowRequestRepository,
    InMemoryVehiclePoolRepository,
)
from submit_vehicle_borrow_request import SubmitVehicleBorrowRequest
from vehicle_borrow_request import VehicleBorrowRequest
from vehicle_category import VehicleCategory
from vehicle_pool import VehiclePool


def main() -> None:
    requests = InMemoryVehicleBorrowRequestRepository()
    pools = InMemoryVehiclePoolRepository()

    driver = Driver("D1", {VehicleCategory.CAR, VehicleCategory.TRUCK})
    pool = VehiclePool("POOL-1", {
        "CAR-01": VehicleCategory.CAR,
        "TRUCK-01": VehicleCategory.TRUCK,
    })
    request = VehicleBorrowRequest(
        "R1", "D1", "POOL-1",
        ("CAR-01", "TRUCK-01"),
        BorrowingDuration(3),
    )

    requests.save(request)
    pools.save(pool)

    service = SubmitVehicleBorrowRequest(requests, pools, driver)
    result = service.execute("R1")
    print(f"Request {result.request_id}: {result.status.value}")

    for vehicle_id in request.vehicle_ids:
        print(f"{vehicle_id} reserved for {pool.reservation_for(vehicle_id)}")


if __name__ == "__main__":
    main()