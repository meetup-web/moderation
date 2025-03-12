from collections.abc import Iterable

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncConnection

from moderation.domain.shared.events import DomainEventAdder
from moderation.domain.shared.unit_of_work import UnitOfWork
from moderation.domain.shared.user_id import UserId
from moderation.domain.tasks.repository import ModerationTaskRepository
from moderation.domain.tasks.task import ModerationTask
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ContentRef
from moderation.infrastructure.persistence.sql_tables import MODERATION_TASKS_TABLE


class SqlModerationTaskRepository(ModerationTaskRepository):
    def __init__(
        self,
        connection: AsyncConnection,
        event_adder: DomainEventAdder,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._connection = connection
        self._unit_of_work = unit_of_work
        self._event_adder = event_adder
        self._identity_map: dict[TaskID, ModerationTask] = {}

    async def with_task_id(self, task_id: TaskID) -> ModerationTask | None:
        if task_id in self._identity_map:
            return self._identity_map[task_id]

        statement = select(
            MODERATION_TASKS_TABLE.c.task_id.label("task_id"),
            MODERATION_TASKS_TABLE.c.assigned_admin.label("assigned_admin"),
            MODERATION_TASKS_TABLE.c.created_at.label("created_at"),
            MODERATION_TASKS_TABLE.c.expiration.label("expiration"),
            MODERATION_TASKS_TABLE.c.content_type.label("content_type"),
            MODERATION_TASKS_TABLE.c.content_id.label("content_id"),
            MODERATION_TASKS_TABLE.c.decision.label("decision"),
        ).where(MODERATION_TASKS_TABLE.c.task_id == task_id)
        cursor_result = await self._connection.execute(statement)
        cursor_row: Row | None = cursor_result.scalar_one_or_none()

        if not cursor_row:
            return None

        return self._load(cursor_row)

    async def with_assigned_admin(self, admin_id: UserId) -> Iterable[ModerationTask]:
        statement = select(
            MODERATION_TASKS_TABLE.c.task_id.label("task_id"),
            MODERATION_TASKS_TABLE.c.assigned_admin.label("assigned_admin"),
            MODERATION_TASKS_TABLE.c.created_at.label("created_at"),
            MODERATION_TASKS_TABLE.c.expiration.label("expiration"),
            MODERATION_TASKS_TABLE.c.content_type.label("content_type"),
            MODERATION_TASKS_TABLE.c.content_id.label("content_id"),
            MODERATION_TASKS_TABLE.c.decision.label("decision"),
        ).where(MODERATION_TASKS_TABLE.c.assigned_admin == admin_id)
        cursor_result = await self._connection.execute(statement)

        moderation_tasks: list[ModerationTask] = []
        for cursor_row in cursor_result:
            moderation_tasks.append(moderation_task := self._load(cursor_row))
            self._identity_map[moderation_task.entity_id] = moderation_task

        return moderation_tasks

    def _load(self, cursor_row: Row) -> ModerationTask:
        moderation_task = ModerationTask(
            entity_id=TaskID(cursor_row.task_id),
            unit_of_work=self._unit_of_work,
            event_adder=self._event_adder,
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
