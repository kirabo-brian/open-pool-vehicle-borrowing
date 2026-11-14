
from errors import VehicleAlreadyReserved
from events import VehicleBorrowRequestSubmitted
from vehicle_borrow_request import VehicleBorrowRequest
from vehicle_pool import VehiclePool


def handle_reservation(
    event: VehicleBorrowRequestSubmitted,
    request: VehicleBorrowRequest,
    pool: VehiclePool,
) -> None:
    try:
        pool.reserve_all(event.request_id, event.vehicle_ids)
    except VehicleAlreadyReserved:
        request.reject_reservation()
    else:
        request.confirm()