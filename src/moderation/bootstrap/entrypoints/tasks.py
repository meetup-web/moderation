from dishka.integrations.taskiq import (
    setup_dishka as add_container_to_taskiq,
)
from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
)
from taskiq import TaskiqEvents, TaskiqState
from taskiq_aio_pika import AioPikaBroker

from moderation.bootstrap.config import get_database_config, get_rabbitmq_config
from moderation.bootstrap.container import bootstrap_worker_container
from moderation.infrastructure.outbox.adapters.rabbitmq_outbox_publisher import (
    ExchangeName,
)
from moderation.infrastructure.outbox.process_outbox_cron_task import (
    process_outbox,
)


def add_tasks_to_taskiq(broker: AioPikaBroker) -> None:
    broker.register_task(
        process_outbox, "process_outbox", schedule=[{"cron": "*/1 * * * *"}]
    )


async def start_broker(state: TaskiqState) -> None:
    await state.faststream_broker.start()


async def bind_exchange(state: TaskiqState) -> None:
    await state.faststream_broker.declare_exchange(
        RabbitExchange(
            name=ExchangeName.MODERATION, durable=True, type=ExchangeType.TOPIC
        )
    )


def add_event_handlers(broker: AioPikaBroker) -> None:
    broker.add_event_handler(
        TaskiqEvents.WORKER_STARTUP,
        start_broker,
    )
    broker.add_event_handler(
        TaskiqEvents.WORKER_STARTUP,
        bind_exchange,
    )


def bootstrap_broker() -> AioPikaBroker:
    rabbitmq_config = get_rabbitmq_config()
    database_config = get_database_config()
    taskiq_broker = AioPikaBroker(
        rabbitmq_config.uri,
        taskiq_return_missed_task=True,
        prefetch_count=1,
    )

    faststream_rabbitmq_broker = RabbitBroker(rabbitmq_config.uri)
    taskiq_broker.state.faststream_broker = faststream_rabbitmq_broker
    container = bootstrap_worker_container(
        rabbitmq_config,
        database_config,
        faststream_rabbitmq_broker,
    )

    add_tasks_to_taskiq(taskiq_broker)
    add_event_handlers(taskiq_broker)
    add_container_to_taskiq(container, taskiq_broker)

    return taskiq_broker
