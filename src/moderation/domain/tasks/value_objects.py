from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class ContentType(str, Enum):
    MEETUP = "meetup"
    POST = "post"
    MEETUP_REVIEW = "meetup_review"


class ModerationDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ContentRef:
    content_type: ContentType
    contnet_id: UUID
