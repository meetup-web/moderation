from abc import ABC, abstractmethod
from collections.abc import Iterable

from moderation.domain.shared.user_id import UserId
from moderation.domain.tasks.task import ModerationTask
from moderation.domain.tasks.task_id import TaskID


class ModerationTaskRepository(ABC):
    @abstractmethod
    def add(self, task: ModerationTask) -> None: ...
    @abstractmethod
    def delete(self, task: ModerationTask) -> None: ...
    @abstractmethod
    async def with_task_id(self, task_id: TaskID) -> ModerationTask | None: ...
    @abstractmethod
    async def with_assigned_admin(self, admin_id: UserId) -> Iterable[ModerationTask]: ...
