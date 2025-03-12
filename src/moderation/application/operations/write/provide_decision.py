from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from moderation.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from moderation.application.common.markers.command import Command
from moderation.application.ports.context.identity_provider import IdentityProvider
from moderation.application.ports.context.user_role import UserRole
from moderation.application.ports.time_provider import TimeProvider
from moderation.domain.tasks.repository import ModerationTaskRepository
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ModerationDecision


@dataclass(frozen=True)
class ProvideDecision(Command[None]):
    task_id: TaskID
    decision: ModerationDecision


class ProvideDecisionHandler(RequestHandler[ProvideDecision, None]):
    def __init__(
        self,
        task_repository: ModerationTaskRepository,
        identity_provider: IdentityProvider,
        time_provider: TimeProvider,
    ) -> None:
        self._task_repository = task_repository
        self._identity_provider = identity_provider
        self._time_provider = time_provider

    async def handle(self, request: ProvideDecision) -> None:
        user_id = await self._identity_provider.current_user_id()
        user_role = await self._identity_provider.current_user_role()

        if user_role != UserRole.ADMIN:
            raise ApplicationError(
                message="Only admin can provide decision",
                error_type=ErrorType.PERMISSION_ERROR,
            )

        task = await self._task_repository.with_task_id(request.task_id)

        if not task:
            raise ApplicationError(
                message="Task not found", error_type=ErrorType.NOT_FOUND
            )

        if task.assigned_admin != user_id:
            raise ApplicationError(
                message="Task is not assigned to current user",
                error_type=ErrorType.PERMISSION_ERROR,
            )

        task.provide_decision(
            decision=request.decision,
            current_date=self._time_provider.provide_current(),
        )
