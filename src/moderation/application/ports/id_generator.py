from abc import ABC, abstractmethod

from moderation.domain.shared.event_id import EventId
from moderation.domain.tasks.task_id import TaskID


class IdGenerator(ABC):
    @abstractmethod
    def generate_event_id(self) -> EventId: ...
    @abstractmethod
    def generate_request_id(self) -> TaskID: ...
