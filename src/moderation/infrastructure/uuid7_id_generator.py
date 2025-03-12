from uuid_extensions import uuid7  # type: ignore

from moderation.application.ports.id_generator import IdGenerator
from moderation.domain.shared.event_id import EventId
from moderation.domain.tasks.task_id import TaskID


class UUID7IdGenerator(IdGenerator):
    def generate_event_id(self) -> EventId:
        return EventId(uuid7())

    def generate_request_id(self) -> TaskID:
        return TaskID(uuid7())
