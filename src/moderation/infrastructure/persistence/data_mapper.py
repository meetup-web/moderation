from abc import ABC, abstractmethod

from moderation.domain.shared.entity import Entity


class DataMapper[T: Entity](ABC):
    @abstractmethod
    async def insert(self, entity: T) -> None: ...
    @abstractmethod
    async def update(self, entity: T) -> None: ...
    @abstractmethod
    async def delete(self, entity: T) -> None: ...
