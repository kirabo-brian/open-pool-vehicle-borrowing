from dataclasses import dataclass


@dataclass(frozen=True)
class SubmitVehicleBorrowRequestCommand:
    """Input DTO."""

    request_id: str
    driver_id: str
    pool_id: str
    vehicle_ids: tuple
    duration_days: int


@dataclass(frozen=True)
class SubmitVehicleBorrowRequestResult:
    """Output DTO."""

    request_id: str
    status: str
    vehicle_ids: tuple
    message: str
