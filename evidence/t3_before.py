from dataclasses import dataclass


@dataclass(frozen=True)
class VehicleBorrowRequest:
    vehicle_ids: tuple[str, ...]
