from dataclasses import dataclass


@dataclass(frozen=True)
class VehicleBorrowRequestSubmitted:
    """Raised once when a draft request is submitted (BR2). Triggers BR5."""

    request_id: str
    pool_id: str
    driver_id: str
    vehicle_ids: tuple
    duration_days: int
