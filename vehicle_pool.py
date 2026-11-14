from errors import InvalidRequest, VehicleAlreadyReserved, VehicleNotInPool
from identifiers import clean_id
from vehicle_category import VehicleCategory


class VehiclePool:
    """Aggregate root. Owns pool membership (BR6) and active reservations (BR5)."""

    def __init__(self, pool_id, vehicles) -> None:
        self._pool_id = clean_id(pool_id, "Pool ID")
        self._vehicles = {}
        for vehicle_id, category in dict(vehicles).items():
            if not isinstance(category, VehicleCategory):
                raise TypeError("Vehicle category must be a VehicleCategory")
            self._vehicles[clean_id(vehicle_id, "Vehicle ID")] = category
        self._reservations = {}  # vehicle_id -> request_id

    @property
    def pool_id(self):
        return self._pool_id

    def contains_all(self, vehicle_ids) -> bool:
        return all(v in self._vehicles for v in vehicle_ids)

    def categories_of(self, vehicle_ids):
        for v in vehicle_ids:
            if v not in self._vehicles:
                raise VehicleNotInPool(v)
        return {self._vehicles[v] for v in vehicle_ids}

    def reserve_all(self, request_id, vehicle_ids) -> None:
        """BR5: reserve every vehicle for the request, or none of them."""
        request_id = clean_id(request_id, "Request ID")
        ids = tuple(clean_id(v, "Vehicle ID") for v in vehicle_ids)
        if not ids:
            raise InvalidRequest("Nothing to reserve")
        if len(set(ids)) != len(ids):
            raise InvalidRequest("Duplicate vehicle ID")

        # Phase 1: check every vehicle, change nothing.
        for v in ids:
            if v not in self._vehicles:
                raise VehicleNotInPool(v)
            holder = self._reservations.get(v)
            if holder is not None and holder != request_id:
                raise VehicleAlreadyReserved(v)

        # Phase 2: commit.
        for v in ids:
            self._reservations[v] = request_id

    def reservation_for(self, vehicle_id):
        """Return the request ID holding the vehicle, or None if it is free."""
        return self._reservations.get(clean_id(vehicle_id, "Vehicle ID"))
