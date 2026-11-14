from dataclasses import dataclass

from domain.errors import InvalidDuration


@dataclass(frozen=True)
class BorrowingDuration:
    """BR1: a borrowing duration is 1 to 7 whole days, inclusive."""

    days: int

    def __post_init__(self) -> None:
        if not isinstance(self.days, int) or isinstance(self.days, bool):
            raise InvalidDuration("Duration must be whole days")
        if not 1 <= self.days <= 7:
            raise InvalidDuration("Duration must be 1 to 7 days")
