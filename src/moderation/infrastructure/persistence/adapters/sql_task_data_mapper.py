from sqlalchemy.ext.asyncio import AsyncConnection

from moderation.domain.tasks.task import ModerationTask
from moderation.infrastructure.persistence.data_mapper import DataMapper
from moderation.infrastructure.persistence.sql_tables import MODERATION_TASKS_TABLE


class SqlModerationTaskDataMapper(DataMapper[ModerationTask]):
    def __init__(self, connection: AsyncConnection) -> None:
        self._connection = connection

    async def insert(self, entity: ModerationTask) -> None:
        stmt = MODERATION_TASKS_TABLE.insert().values(
            task_id=entity.entity_id,
            assigned_admin=entity.assigned_admin,
            created_at=entity.created_at,
            expiration=entity.expiration,
            content_type=entity.content_ref.content_type,
            content_id=entity.content_ref.contnet_id,
            decision=entity.decision,
        )

        await self._connection.execute(stmt)

    async def update(self, entity: ModerationTask) -> None:
        stmt = (
            MODERATION_TASKS_TABLE.update()
            .where(MODERATION_TASKS_TABLE.c.task_id == entity.entity_id)
            .values(assigned_admin=entity.assigned_admin, decision=entity.decision)
        )

        await self._connection.execute(stmt)
