from moderation.domain.shared.entity import Entity
from moderation.domain.tasks.task import ModerationTask
from moderation.infrastructure.persistence.adapters.sql_task_data_mapper import (
    SqlModerationTaskDataMapper,
)
from moderation.infrastructure.persistence.data_mapper import DataMapper
from moderation.infrastructure.persistence.data_mappers_registry import (
    DataMappersRegistry,
)


class SqlDataMappersRegistry(DataMappersRegistry):
    def __init__(self, moderation_task_data_mapper: SqlModerationTaskDataMapper) -> None:
        self._data_mappers_map: dict[type[Entity], DataMapper] = {
            ModerationTask: moderation_task_data_mapper
        }

    def get_mapper[EntityT: Entity](self, entity: type[EntityT]) -> DataMapper[EntityT]:
        mapper = self._data_mappers_map.get(entity)

        if not mapper:
            raise KeyError(f"DataMapper for {entity.__name__!r} not registered")

        return mapper
