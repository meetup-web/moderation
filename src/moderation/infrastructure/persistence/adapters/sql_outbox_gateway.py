from sqlalchemy import CursorResult, select
from sqlalchemy.ext.asyncio import AsyncConnection

from moderation.infrastructure.outbox.outbox_gateway import OutboxGateway
from moderation.infrastructure.outbox.outbox_message import OutboxMessage
from moderation.infrastructure.persistence.sql_tables import OUTBOX_TABLE


class SqlOutboxGateway(OutboxGateway):
    def __init__(self, connection: AsyncConnection) -> None:
        self._connection = connection

    async def select(self) -> list[OutboxMessage]:
        statement = select(
            OUTBOX_TABLE.c.data.label("data"),
            OUTBOX_TABLE.c.message_id.label("message_id"),
            OUTBOX_TABLE.c.event_type.label("event_type"),
        )
        cursor_result = await self._connection.execute(statement)
        return self._load(cursor_result)

    async def insert(self, message: OutboxMessage) -> None:
        statement = OUTBOX_TABLE.insert().values(
            data=message.data,
            message_id=message.message_id,
            event_type=message.event_type,
        )
        await self._connection.execute(statement)

    async def delete(self, message: OutboxMessage) -> None:
        statement = OUTBOX_TABLE.delete().where(
            OUTBOX_TABLE.c.message_id == message.message_id
        )
        await self._connection.execute(statement)

    def _load(self, cursor_result: CursorResult) -> list[OutboxMessage]:
        return [
            OutboxMessage(
                data=cursor_row.data,
                message_id=cursor_row.message_id,
                event_type=cursor_row.event_type,
            )
            for cursor_row in cursor_result
        ]
