from collections.abc import Hashable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from moderation.domain.shared.events import DomainEvent, DomainEventAdder
    from moderation.domain.shared.unit_of_work import UnitOfWork


class Entity[TEntityID: Hashable]:
    def __init__(
        self,
        entity_id: TEntityID,
        event_adder: "DomainEventAdder",
        unit_of_work: "UnitOfWork",
    ) -> None:
        self._entity_id = entity_id
        self._event_adder = event_adder
        self._unit_of_work = unit_of_work

    def add_event(self, event: "DomainEvent") -> None:
        self._event_adder.add_event(event)

    def mark_new(self) -> None:
        self._unit_of_work.register_new(self)

    def mark_dirty(self) -> None:
        self._unit_of_work.register_dirty(self)

    def mark_deleted(self) -> None:
        self._unit_of_work.register_deleted(self)

    @property
    def entity_id(self) -> TEntityID:
        return self._entity_id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented

        return bool(other.entity_id == self.entity_id)

    def __hash__(self) -> int:
        return hash(self.entity_id)
