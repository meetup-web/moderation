from enum import StrEnum

from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.rabbit import ExchangeType, RabbitExchange, RabbitQueue
from faststream.rabbit.router import RabbitRouter

from moderation.application.operations.write.moderate_content import (
    ModerateContent,
)
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ContentType
from moderation.presentation.stream.request_models import (
    MeetupCreated,
)


class ExchangeName(StrEnum):
    MEETUPS = "meetups_exchange"


MEETUPS_ROUTER = RabbitRouter()


@MEETUPS_ROUTER.subscriber(
    queue=RabbitQueue(name="created_meetups", durable=True, routing_key="MeetupCreated"),
    exchange=RabbitExchange(
        name=ExchangeName.MEETUPS, type=ExchangeType.DIRECT, durable=True
    ),
)
@inject
async def start_meetup_moderation(
    event: MeetupCreated, *, sender: FromDishka[Sender]
) -> TaskID:
    taski_id = await sender.send(
        request=ModerateContent(
            content_type=ContentType.MEETUP, content_id=event.meetup_id
        )
    )

    return taski_id
