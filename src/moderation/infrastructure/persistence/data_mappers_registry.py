from abc import ABC, abstractmethod

from moderation.domain.shared.entity import Entity
from moderation.infrastructure.persistence.data_mapper import DataMapper


class DataMappersRegistry(ABC):
    @abstractmethod
    def get_mapper(self, entity: type[Entity]) -> DataMapper: ...
