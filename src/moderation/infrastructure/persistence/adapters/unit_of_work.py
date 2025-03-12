from moderation.application.ports.committer import Committer
from moderation.domain.shared.entity import Entity
from moderation.domain.shared.unit_of_work import UnitOfWork
from moderation.infrastructure.persistence.data_mappers_registry import (
    DataMappersRegistry,
)
from moderation.infrastructure.persistence.transaction import Transaction


class UnitOfWorkImpl(Committer, UnitOfWork):
    def __init__(
        self,
        transaction: Transaction,
        data_mappers_registry: DataMappersRegistry,
    ) -> None:
        self._transaction = transaction
        self._data_mappers_registry = data_mappers_registry

        self._new_entities: list[Entity] = []
        self._dirty_entities: list[Entity] = []
        self._deleted_entities: list[Entity] = []

    def register_new(self, entity: Entity) -> None:
        self._new_entities.append(entity)

    def register_dirty(self, entity: Entity) -> None:
        self._dirty_entities.append(entity)

    def register_deleted(self, entity: Entity) -> None:
        self._deleted_entities.append(entity)

    async def commit(self) -> None:
        try:
            await self._persist_new()
            await self._persist_dirty()
            await self._persist_deleted()
            await self._transaction.commit()

        except Exception:
            await self._transaction.rollback()
            raise

        finally:
            self._clear()

    def _clear(self) -> None:
        self._new_entities.clear()
        self._dirty_entities.clear()
        self._deleted_entities.clear()

    async def _persist_new(self) -> None:
        for entity in self._new_entities:
            data_mapper = self._data_mappers_registry.get_mapper(
                type(entity),
            )

            await data_mapper.insert(entity)

    async def _persist_dirty(self) -> None:
        for entity in self._dirty_entities:
            data_mapper = self._data_mappers_registry.get_mapper(
                type(entity),
            )

            await data_mapper.update(entity)

    async def _persist_deleted(self) -> None:
        for entity in self._deleted_entities:
            data_mapper = self._data_mappers_registry.get_mapper(
                type(entity),
            )

            await data_mapper.delete(entity)
