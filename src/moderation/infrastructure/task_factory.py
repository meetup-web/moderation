from datetime import timedelta
from uuid import UUID

from moderation.application.ports.id_generator import IdGenerator
from moderation.application.ports.time_provider import TimeProvider
from moderation.domain.shared.events import DomainEventAdder
from moderation.domain.shared.unit_of_work import UnitOfWork
from moderation.domain.shared.user_id import UserId
from moderation.domain.tasks.events import ModerationStarted
from moderation.domain.tasks.factory import ModerationTaskFactory
from moderation.domain.tasks.task import ModerationTask
from moderation.domain.tasks.value_objects import ContentRef


class ModerationTaskFactoryImpl(ModerationTaskFactory):
    _DEFAULT_EXPIRATION = timedelta(days=1)

    def __init__(
        self,
        event_adder: DomainEventAdder,
        unit_of_work: UnitOfWork,
        time_provider: TimeProvider,
        id_generator: IdGenerator,
    ) -> None:
        self._event_adder = event_adder
        self._unit_of_work = unit_of_work
        self._time_provider = time_provider
        self._id_generator = id_generator

    async def create(self, content_ref: ContentRef) -> ModerationTask:
        assigned_admin = UserId(UUID("067c3205-d896-7404-8000-3c25a05b74cf"))

        moderation_task = ModerationTask(
            entity_id=self._id_generator.generate_request_id(),
            event_adder=self._event_adder,
            unit_of_work=self._unit_of_work,
            assigned_admin=assigned_admin,
            created_at=self._time_provider.provide_current(),
            expiration=self._time_provider.provide_current() + self._DEFAULT_EXPIRATION,
            content_ref=content_ref,
        )

        event = ModerationStarted(
            task_id=moderation_task.entity_id,
            assigned_admin=moderation_task.assigned_admin,
            expiration=moderation_task.expiration,
            content_ref=moderation_task.content_ref,
            event_date=moderation_task.created_at,
        )

        moderation_task.add_event(event=event)

        return moderation_task
