from datetime import datetime

from moderation.domain.shared.entity import Entity
from moderation.domain.shared.events import DomainEventAdder
from moderation.domain.shared.unit_of_work import UnitOfWork
from moderation.domain.shared.user_id import UserId
from moderation.domain.tasks.events import AdminReassigned, ModerationDecisionAdded
from moderation.domain.tasks.exceptions import ModerationTaskIsReadyError
from moderation.domain.tasks.task_id import TaskID
from moderation.domain.tasks.value_objects import ContentRef, ModerationDecision


class ModerationTask(Entity[TaskID]):
    def __init__(
        self,
        entity_id: TaskID,
        event_adder: DomainEventAdder,
        unit_of_work: UnitOfWork,
        *,
        assigned_admin: UserId,
        created_at: datetime,
        expiration: datetime,
        content_ref: ContentRef,
        decision: ModerationDecision = ModerationDecision.PENDING,
    ) -> None:
        Entity.__init__(self, entity_id, event_adder, unit_of_work)

        self._assigned_admin = assigned_admin
        self._created_at = created_at
        self._expiration = expiration
        self._content_ref = content_ref
        self._decision = decision

    @property
    def assigned_admin(self) -> UserId:
        return self._assigned_admin

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def expiration(self) -> datetime:
        return self._expiration

    @property
    def content_ref(self) -> ContentRef:
        return self._content_ref

    @property
    def decision(self) -> ModerationDecision:
        return self._decision

    def provide_decision(
        self, decision: ModerationDecision, current_date: datetime
    ) -> None:
        self._ensure_is_pending()

        if self._decision == decision:
            return

        self._decision = decision
        event = ModerationDecisionAdded(
            task_id=self._entity_id,
            decision=decision,
            event_date=current_date,
            content_ref=self._content_ref,
        )

        self.mark_dirty()
        self.add_event(event=event)

    def reassgin_admin(self, admin_id: UserId, current_date: datetime) -> None:
        self._ensure_is_pending()

        self._assigned_admin = admin_id
        event = AdminReassigned(
            task_id=self._entity_id,
            assigned_admin=admin_id,
            event_date=current_date,
        )

        self.mark_dirty()
        self.add_event(event=event)

    def _ensure_is_pending(self) -> None:
        if self._decision != ModerationDecision.PENDING:
            raise ModerationTaskIsReadyError
