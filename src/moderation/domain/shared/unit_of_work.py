from abc import ABC, abstractmethod

from moderation.domain.shared.entity import Entity


class UnitOfWork(ABC):
    @abstractmethod
    def register_new(self, entity: Entity) -> None: ...
    @abstractmethod
    def register_dirty(self, entity: Entity) -> None: ...
    @abstractmethod
    def register_deleted(self, entity: Entity) -> None: ...
