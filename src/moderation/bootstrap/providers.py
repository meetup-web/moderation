from collections.abc import AsyncIterator

from alembic.config import Config as AlembicConfig
from bazario.asyncio import Dispatcher, Registry
from bazario.asyncio.resolvers.dishka import DishkaResolver
from dishka import (
    Provider,
    Scope,
    WithParents,
    alias,
    from_context,
    provide,
    provide_all,
)
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    create_async_engine,
)
from taskiq_aio_pika.broker import AioPikaBroker
from uvicorn import Config as UvicornConfig
from uvicorn import Server as UvicornServer

from moderation.application.common.behaviors.commition_behavior import (
    CommitionBehavior,
)
from moderation.application.common.behaviors.event_id_generation_behavior import (
    EventIdGenerationBehavior,
)
from moderation.application.common.behaviors.event_publishing_behavior import (
    EventPublishingBehavior,
)
from moderation.application.common.markers.command import Command
from moderation.application.operations.read.get_my_tasks import (
    LoadMyTasks,
    LoadMyTasksHandler,
)
from moderation.application.operations.write.moderate_content import (
    ModerateContent,
    ModerateContentHandler,
)
from moderation.application.operations.write.provide_decision import (
    ProvideDecision,
    ProvideDecisionHandler,
)
from moderation.bootstrap.config import (
    DatabaseConfig,
    RabbitmqConfig,
)
from moderation.domain.shared.events import DomainEvent
from moderation.infrastructure.domain_events import DomainEvents
from moderation.infrastructure.fake_identity_provider import FakeIdentityProvider
from moderation.infrastructure.outbox.adapters.rabbitmq_outbox_publisher import (
    RabbitmqOutboxPublisher,
)
from moderation.infrastructure.outbox.outbox_processor import OutboxProcessor
from moderation.infrastructure.outbox.outbox_publisher import OutboxPublisher
from moderation.infrastructure.outbox.outbox_storing_handler import (
    OutboxStoringHandler,
)
from moderation.infrastructure.persistence.adapters.sql_data_mappers_registry import (
    SqlDataMappersRegistry,
)
from moderation.infrastructure.persistence.adapters.sql_outbox_gateway import (
    SqlOutboxGateway,
)
from moderation.infrastructure.persistence.adapters.sql_task_data_mapper import (
    SqlModerationTaskDataMapper,
)
from moderation.infrastructure.persistence.adapters.sql_task_gateway import (
    SqlModerationTaskGateway,
)
from moderation.infrastructure.persistence.adapters.sql_task_repository import (
    SqlModerationTaskRepository,
)
from moderation.infrastructure.persistence.adapters.unit_of_work import (
    UnitOfWorkImpl,
)
from moderation.infrastructure.persistence.transaction import Transaction
from moderation.infrastructure.task_factory import ModerationTaskFactoryImpl
from moderation.infrastructure.utc_time_provider import UtcTimeProvider
from moderation.infrastructure.uuid7_id_generator import UUID7IdGenerator


class ApiConfigProvider(Provider):
    scope = Scope.APP

    rabbitmq_config = from_context(RabbitmqConfig)
    database_config = from_context(DatabaseConfig)


class PersistenceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def engine(self, postgres_config: DatabaseConfig) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(postgres_config.uri)
        yield engine
        await engine.dispose()

    @provide
    async def connection(self, engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
        async with engine.connect() as connection:
            yield connection


class DomainAdaptersProvider(Provider):
    scope = Scope.REQUEST

    repositories = provide_all(
        WithParents[SqlModerationTaskRepository],  # type: ignore[misc]
    )
    domain_events = provide(WithParents[DomainEvents])  # type: ignore[misc]
    unit_of_work = provide(WithParents[UnitOfWorkImpl])  # type: ignore[misc]
    task_factory = provide(
        WithParents[ModerationTaskFactoryImpl],  # type: ignore[misc]
    )


class ApplicationAdaptersProvider(Provider):
    scope = Scope.REQUEST
    gateways = provide_all(
        WithParents[SqlOutboxGateway],  # type: ignore[misc]
        WithParents[SqlModerationTaskGateway],  # type: ignore[misc]
    )
    id_generator = provide(
        WithParents[UUID7IdGenerator],  # type: ignore[misc]
        scope=Scope.APP,
    )
    time_provider = provide(
        WithParents[UtcTimeProvider],  # type: ignore[misc]
        scope=Scope.APP,
    )
    identity_provider = provide(
        WithParents[FakeIdentityProvider],  # type: ignore[misc]
        scope=Scope.APP,
    )


class InfrastructureAdaptersProvider(Provider):
    scope = Scope.REQUEST

    transaction = alias(AsyncConnection, provides=Transaction)
    data_mappers = provide_all(
        WithParents[SqlModerationTaskDataMapper],  # type: ignore[misc]
    )
    data_mappers_registry = provide(
        WithParents[SqlDataMappersRegistry],  # type: ignore[misc]
    )


class ApplicationHandlersProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        OutboxStoringHandler,
        LoadMyTasksHandler,
        ModerateContentHandler,
        ProvideDecisionHandler,
    )
    behaviors = provide_all(
        CommitionBehavior,
        EventPublishingBehavior,
        EventIdGenerationBehavior,
    )


class BazarioProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def registry(self) -> Registry:
        registry = Registry()

        registry.add_request_handler(LoadMyTasks, LoadMyTasksHandler)
        registry.add_request_handler(ModerateContent, ModerateContentHandler)
        registry.add_request_handler(ProvideDecision, ProvideDecisionHandler)
        registry.add_notification_handlers(DomainEvent, OutboxStoringHandler)
        registry.add_pipeline_behaviors(DomainEvent, EventIdGenerationBehavior)
        registry.add_pipeline_behaviors(
            Command,
            EventPublishingBehavior,
            CommitionBehavior,
        )

        return registry

    resolver = provide(WithParents[DishkaResolver])  # type: ignore[misc]
    dispatcher = provide(WithParents[Dispatcher])  # type: ignore[misc]


class CliConfigProvider(Provider):
    scope = Scope.APP

    alembic_config = from_context(AlembicConfig)
    uvicorn_config = from_context(UvicornConfig)
    uvicorn_server = from_context(UvicornServer)
    taskiq_broker = from_context(AioPikaBroker)


class BrokerProvider(Provider):
    scope = Scope.APP

    faststream_rabbit_broker = from_context(RabbitBroker)


class OutboxProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def outbox_publisher(
        self,
        broker: RabbitBroker,
    ) -> OutboxPublisher:
        return RabbitmqOutboxPublisher(broker=broker)

    @provide
    async def outbox_processor(
        self,
        transaction: Transaction,
        outbox_gateway: SqlOutboxGateway,
        outbox_publisher: OutboxPublisher,
    ) -> OutboxProcessor:
        return OutboxProcessor(
            transaction=transaction,
            outbox_gateway=outbox_gateway,
            outbox_publisher=outbox_publisher,
        )
