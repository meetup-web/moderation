from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class OutboxMessage:
    data: str | bytes
    event_type: str
    message_id: UUID
