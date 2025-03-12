from collections.abc import Iterable
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from moderation.application.common.markers.query import Query
from moderation.application.models.moderation_task import ModerationTaskReadModel
from moderation.application.models.pagination import Pagination
from moderation.application.ports.context.identity_provider import (
    IdentityProvider,
)
from moderation.application.ports.task_gateway import ModerationTaskGateway


@dataclass(frozen=True)
class LoadMyTasks(Query[Iterable[ModerationTaskReadModel]]):
    pagintation: Pagination


class LoadMyTasksHandler(RequestHandler[LoadMyTasks, Iterable[ModerationTaskReadModel]]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        task_gateway: ModerationTaskGateway,
    ) -> None:
        self._identity_provider = identity_provider
        self._task_gateway = task_gateway

    async def handle(self, request: LoadMyTasks) -> Iterable[ModerationTaskReadModel]:
        user_id = await self._identity_provider.current_user_id()
        tasks = await self._task_gateway.load_admin_tasks(user_id, request.pagintation)

        return tasks
