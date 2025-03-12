from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from bazario import Notification

from moderation.domain.shared.event_id import EventId


@dataclass(frozen=True, kw_only=True)
class DomainEvent(Notification):
    event_date: datetime
    event_id: EventId | None = field(default=None, init=False)

    @property
    def event_type(self) -> str:
        return type(self).__name__

    def set_event_id(self, event_id: EventId) -> None:
        if self.event_id:
            raise ValueError("Identifier already set")

        object.__setattr__(self, "event_id", event_id)


class DomainEventAdder(ABC):
    @abstractmethod
    def add_event(self, event: DomainEvent) -> None: ...
