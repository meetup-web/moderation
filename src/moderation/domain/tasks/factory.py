from abc import ABC, abstractmethod

from moderation.domain.tasks.task import ModerationTask
from moderation.domain.tasks.value_objects import ContentRef


class ModerationTaskFactory(ABC):
    @abstractmethod
    async def create(self, content_ref: ContentRef) -> ModerationTask: ...
