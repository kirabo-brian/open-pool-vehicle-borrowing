from typing import Callable

from application.event_publisher import EventPublisher


class InProcessEventBus(EventPublisher):
    def __init__(self) -> None:
        self._handlers: dict = {}

    def subscribe(self, event_type: type, handler: Callable) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: object) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)
