from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    MetaData,
    Table,
    Text,
)

from moderation.domain.tasks.value_objects import ContentType, ModerationDecision

METADATA = MetaData()

MODERATION_TASKS_TABLE = Table(
    "moderation_tasks",
    METADATA,
    Column("task_id", UUID, primary_key=True),
    Column("assigned_admin", UUID, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("expiration", DateTime(timezone=True), nullable=False),
    Column("content_type", Enum(ContentType), nullable=False),
    Column("content_id", UUID, nullable=False),
    Column(
        "decision",
        Enum(ModerationDecision),
        nullable=False,
        default=ModerationDecision.PENDING,
    ),
)


OUTBOX_TABLE = Table(
    "outbox",
    METADATA,
    Column("message_id", UUID, primary_key=True),
    Column("data", Text, nullable=False),
    Column("event_type", Text, nullable=False, default=False),
)
