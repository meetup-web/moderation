from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from moderation.domain.shared.user_id import UserId


@dataclass(frozen=True)
class Location:
    address: str
    city: str
    country: str


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    finish_date: datetime


@dataclass(frozen=True)
class MeetupCreated:
    meetup_id: UUID
    creator: UserId
    time: TimeSlot
    location: Location
    title: str
    description: str


@dataclass(frozen=True)
class ReviewAdded:
    review_id: UUID
    reviewer_id: UserId
    meetup_id: UUID
    rating: int
    comment: str
