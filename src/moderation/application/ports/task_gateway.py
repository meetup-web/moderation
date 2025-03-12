from abc import ABC, abstractmethod
from collections.abc import Iterable

from moderation.application.models.moderation_task import ModerationTaskReadModel
from moderation.application.models.pagination import Pagination
from moderation.domain.shared.user_id import UserId


class ModerationTaskGateway(ABC):
    @abstractmethod
    async def load_admin_tasks(
        self, admin_id: UserId, pagination: Pagination
    ) -> Iterable[ModerationTaskReadModel]: ...
