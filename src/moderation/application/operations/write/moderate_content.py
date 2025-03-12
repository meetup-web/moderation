from dataclasses import dataclass
from uuid import UUID

from bazario.asyncio import RequestHandler

from moderation.application.common.markers.command import Command
from moderation.domain.tasks.factory import ModerationTaskFactory
from moderation.domain.tasks.repository import ModerationTaskRepository
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ContentRef, ContentType


@dataclass(frozen=True)
class ModerateContent(Command[TaskID]):
    content_type: ContentType
    content_id: UUID


class ModerateContentHandler(RequestHandler[ModerateContent, TaskID]):
    def __init__(
        self,
        task_factory: ModerationTaskFactory,
        task_repository: ModerationTaskRepository,
    ) -> None:
        self._task_factory = task_factory
        self._task_repository = task_repository

    async def handle(self, request: ModerateContent) -> TaskID:
        task = await self._task_factory.create(
            ContentRef(request.content_type, request.content_id)
        )

        self._task_repository.add(task)

        return task.entity_id
