from dataclasses import dataclass
from datetime import datetime

from moderation.domain.shared.events import DomainEvent
from moderation.domain.shared.user_id import UserId
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ContentRef, ModerationDecision


@dataclass(frozen=True)
class ModerationStarted(DomainEvent):
    task_id: TaskID
    assigned_admin: UserId
    expiration: datetime
    content_ref: ContentRef


@dataclass(frozen=True)
class ModerationDecisionAdded(DomainEvent):
    task_id: TaskID
    decision: ModerationDecision
    content_ref: ContentRef


@dataclass(frozen=True)
class AdminReassigned(DomainEvent):
    task_id: TaskID
    assigned_admin: UserId
