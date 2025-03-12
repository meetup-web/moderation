from dataclasses import asdict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from moderation.application.common.application_error import (
    ApplicationError,
    ErrorType,
)
from moderation.domain.shared.exceptions import DomainError
from moderation.domain.tasks.exceptions import ModerationTaskIsReadyError
from moderation.presentation.api.response_models import ErrorData, ErrorResponse

STATUS_MAP = {
    ErrorType.NOT_FOUND: HTTP_404_NOT_FOUND,
    ErrorType.VALIDATION_ERROR: HTTP_422_UNPROCESSABLE_ENTITY,
    ErrorType.APPLICATION_ERROR: HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorType.PERMISSION_ERROR: HTTP_403_FORBIDDEN,
    ModerationTaskIsReadyError: HTTP_409_CONFLICT,
}


async def application_error_handler(_: Request, exception: ApplicationError) -> Response:
    error_data = ErrorData[None](exception.message)
    status_code = STATUS_MAP[exception.error_type]
    response_content = ErrorResponse(status_code, error_data)

    return JSONResponse(asdict(response_content), status_code)


async def domain_error_handler(_: Request, exception: DomainError) -> Response:
    error_data = ErrorData[None](exception.message)
    status_code = STATUS_MAP[type(exception)]
    response_content = ErrorResponse(status_code, error_data)

    return JSONResponse(asdict(response_content), status_code)
