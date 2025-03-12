from dataclasses import dataclass
from datetime import datetime

from moderation.domain.shared.user_id import UserId
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ContentRef, ModerationDecision


@dataclass(frozen=True)
class ModerationTaskReadModel:
    task_id: TaskID
    assigned_admin: UserId
    created_at: datetime
    expiration: datetime
    content_ref: ContentRef
    decision: ModerationDecision
