"""Business logic for NotificationMessage."""

from typing import Optional

from interfaces.notification_message_repository import INotificationMessageRepository
from models import NotificationMessage


def _to_csv(values: list[str] | None) -> str:
    return ",".join(v.strip() for v in (values or []) if v and v.strip())


class NotificationMessageService:

    def __init__(self, repository: INotificationMessageRepository):
        self._repository = repository

    @staticmethod
    def _apply_payload(entity: NotificationMessage, payload: dict) -> None:
        entity_kind = "preference" if payload.get("type") == "preference" else "notification"
        entity.entity_kind = entity_kind
        entity.user_id = payload.get("user_id", entity.user_id)

        if entity_kind == "preference":
            if payload.get("notify_push") is not None:
                entity.notify_push = bool(payload["notify_push"])
            if payload.get("notify_email") is not None:
                entity.notify_email = bool(payload["notify_email"])
            if payload.get("notify_sms") is not None:
                entity.notify_sms = bool(payload["notify_sms"])
        else:
            entity.notif_type = payload.get("type", entity.notif_type)
            entity.notif_title = payload.get("title", entity.notif_title)
            entity.notif_body = payload.get("body", entity.notif_body)
            if "channel" in payload:
                entity.channel_csv = _to_csv(payload.get("channel") or ["in_app"])
            if "read_at" in payload:
                entity.read_at = payload.get("read_at")

    async def create_entity(
        self,
        title: str,
        description: Optional[str],
        status: str,
        data: dict,
    ) -> NotificationMessage:
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Title cannot be empty")

        existing = await self._repository.get_by_title(normalized_title)
        if existing:
            raise ValueError("Entity with this title already exists")

        entity = NotificationMessage(
            title=normalized_title,
            description=description,
            status=status,
            user_id=data.get("user_id", "unknown"),
            entity_kind="preference" if data.get("type") == "preference" else "notification",
        )
        self._apply_payload(entity, data)
        return await self._repository.create(entity)

    async def list_entities(self, status_filter: Optional[str] = None) -> list[NotificationMessage]:
        return await self._repository.list(status_filter=status_filter)

    async def get_entity(self, entity_id: str) -> Optional[NotificationMessage]:
        return await self._repository.get_by_id(entity_id)

    async def update_entity(self, entity_id: str, **fields) -> Optional[NotificationMessage]:
        entity = await self._repository.get_by_id(entity_id)
        if not entity:
            return None

        title = fields.get("title")
        if title is not None:
            normalized_title = title.strip()
            if not normalized_title:
                raise ValueError("Title cannot be empty")

            existing = await self._repository.get_by_title(normalized_title)
            if existing and str(existing.id) != str(entity.id):
                raise ValueError("Entity with this title already exists")
            entity.title = normalized_title

        for key in ("description", "status"):
            if key in fields and fields[key] is not None:
                setattr(entity, key, fields[key])

        if "data" in fields and fields["data"] is not None:
            self._apply_payload(entity, fields["data"])

        return await self._repository.update(entity)