from dataclasses import dataclass


@dataclass(frozen=True)
class VehicleBorrowRequest:
    vehicle_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(set(self.vehicle_ids)) != len(self.vehicle_ids):
            raise ValueError("Duplicate vehicle ID")
