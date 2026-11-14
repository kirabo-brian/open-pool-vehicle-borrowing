from dataclasses import dataclass

from domain.errors import DriverNotQualified
from domain.identifiers import clean_id
from domain.vehicle_category import VehicleCategory


@dataclass(frozen=True)
class Driver:
    """A driver and the vehicle categories they are qualified for."""

    driver_id: str
    qualifications: frozenset

    def __post_init__(self) -> None:
        object.__setattr__(self, "driver_id", clean_id(self.driver_id, "Driver ID"))
        quals = frozenset(self.qualifications)
        if not all(isinstance(q, VehicleCategory) for q in quals):
            raise TypeError("Qualifications must be VehicleCategory values")
        object.__setattr__(self, "qualifications", quals)


class DriverEligibilityService:
    """BR4: the driver must be qualified for every requested vehicle category."""

    @staticmethod
    def check(driver: Driver, requested_categories) -> None:
        missing = set(requested_categories) - driver.qualifications
        if missing:
            names = ", ".join(sorted(c.value for c in missing))
            raise DriverNotQualified(f"{driver.driver_id} not qualified for {names}")
