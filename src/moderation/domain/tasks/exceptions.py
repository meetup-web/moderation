from dataclasses import dataclass

from moderation.domain.shared.exceptions import DomainError


@dataclass(frozen=True)
class ModerationTaskIsReadyError(DomainError):
    message: str = "Task is already ready"
