from collections.abc import Iterable

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncConnection

from moderation.application.models.moderation_task import ModerationTaskReadModel
from moderation.application.models.pagination import Pagination
from moderation.application.ports.task_gateway import ModerationTaskGateway
from moderation.domain.shared.user_id import UserId
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ContentRef
from moderation.infrastructure.persistence.sql_tables import MODERATION_TASKS_TABLE


class SqlModerationTaskGateway(ModerationTaskGateway):
    def __init__(self, connection: AsyncConnection) -> None:
        self._connection = connection
        self._identity_map: dict[TaskID, ModerationTaskReadModel] = {}

    async def load_admin_tasks(
        self, admin_id: UserId, pagination: Pagination
    ) -> Iterable[ModerationTaskReadModel]:
        statement = (
            select(
                MODERATION_TASKS_TABLE.c.task_id.label("task_id"),
                MODERATION_TASKS_TABLE.c.assigned_admin.label("assigned_admin"),
                MODERATION_TASKS_TABLE.c.created_at.label("created_at"),
                MODERATION_TASKS_TABLE.c.expiration.label("expiration"),
                MODERATION_TASKS_TABLE.c.content_type.label("content_type"),
                MODERATION_TASKS_TABLE.c.content_id.label("content_id"),
                MODERATION_TASKS_TABLE.c.decision.label("decision"),
            )
            .where(MODERATION_TASKS_TABLE.c.assigned_admin == admin_id)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        cursor_result = await self._connection.execute(statement)

        moderation_tasks: list[ModerationTaskReadModel] = []
        for cursor_row in cursor_result:
            moderation_tasks.append(moderation_task := self._load(cursor_row))
            self._identity_map[moderation_task.task_id] = moderation_task

        return moderation_tasks

    def _load(self, cursor_row: Row) -> ModerationTaskReadModel:
        moderation_task = ModerationTaskReadModel(
            task_id=TaskID(cursor_row.task_id),
            assigned_admin=UserId(cursor_row.assigned_admin),
            created_at=cursor_row.created_at,
            expiration=cursor_row.expiration,
            content_ref=ContentRef(
                content_type=cursor_row.content_type,
                contnet_id=cursor_row.content_id,
            ),
            decision=cursor_row.decision,
        )

        return moderation_task
