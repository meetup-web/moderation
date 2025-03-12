from collections.abc import Iterable
from typing import Annotated

from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Depends
from starlette.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from moderation.application.common.application_error import ApplicationError
from moderation.application.models.moderation_task import ModerationTaskReadModel
from moderation.application.models.pagination import Pagination
from moderation.application.operations.read.get_my_tasks import LoadMyTasks
from moderation.application.operations.write.provide_decision import (
    ProvideDecision,
)
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ModerationDecision
from moderation.presentation.api.response_models import (
    ErrorResponse,
    SuccessResponse,
)

MODERATION_TASKS_ROUTER = APIRouter(prefix="/moderation-tasks", tags=["moderation-tasks"])


@MODERATION_TASKS_ROUTER.put(
    path="/{task_id}",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[None]},
        HTTP_403_FORBIDDEN: {"model": ErrorResponse[ApplicationError]},
        HTTP_404_NOT_FOUND: {"model": ErrorResponse[ApplicationError]},
        HTTP_409_CONFLICT: {"model": ErrorResponse[ApplicationError]},
    },
    status_code=HTTP_200_OK,
)
@inject
async def provide_decision(
    task_id: TaskID,
    decision: Annotated[ModerationDecision, Body()],
    *,
    sender: FromDishka[Sender],
) -> SuccessResponse[None]:
    await sender.send(ProvideDecision(task_id=task_id, decision=decision))
    return SuccessResponse(status=HTTP_200_OK)


@MODERATION_TASKS_ROUTER.get(
    path="/my-tasks",
    responses={
        HTTP_200_OK: {"model": SuccessResponse[Iterable[ModerationTaskReadModel]]},
    },
    status_code=HTTP_200_OK,
)
@inject
async def load_my_tasks(
    pagination: Annotated[Pagination, Depends()],
    *,
    sender: FromDishka[Sender],
) -> SuccessResponse[Iterable[ModerationTaskReadModel]]:
    tasks = await sender.send(LoadMyTasks(pagintation=pagination))
    return SuccessResponse(status=HTTP_200_OK, result=tasks)
