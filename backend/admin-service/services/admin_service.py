"""Admin business logic service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from models import AdminUser, Announcement, AuditLog, FeatureFlag, ModerationQueue
from repositories.admin_repository import SqlAlchemyAdminRepository


class AdminService:

    def __init__(self, repository: SqlAlchemyAdminRepository):
        self._repository = repository

    async def ensure_actor(self, actor_id: str, actor_role: str) -> AdminUser:
        user = await self._repository.get_user(actor_id)
        if user:
            if user.role != actor_role:
                user.role = actor_role
                user = await self._repository.update_user(user)
            return user

        user = AdminUser(
            id=actor_id,
            display_name=f"User {actor_id[:8]}",
            email=f"{actor_id[:8]}@hena.local",
            role=actor_role,
            is_suspended=False,
            is_verified=actor_role in {"admin", "super_admin", "reviewer"},
        )
        return await self._repository.create_user(user)

    async def _log(
        self,
        *,
        action: str,
        actor_id: str,
        target_type: str,
        target_id: str,
        detail_status: Optional[str] = None,
        detail_reason: Optional[str] = None,
        detail_note: Optional[str] = None,
        detail_queue_id: Optional[str] = None,
    ) -> AuditLog:
        log = AuditLog(
            action=action,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            detail_status=detail_status,
            detail_reason=detail_reason,
            detail_note=detail_note,
            detail_queue_id=detail_queue_id,
        )
        return await self._repository.create_audit_log(log)

    async def list_moderation_items(
        self,
        *,
        page: int,
        page_size: int,
        status_filter: Optional[str],
        resource_type: Optional[str],
    ) -> tuple[list[ModerationQueue], int]:
        return await self._repository.list_moderation_items(
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            resource_type=resource_type,
        )

    async def get_moderation_item(self, queue_id: str) -> Optional[ModerationQueue]:
        return await self._repository.get_moderation_item(queue_id)

    async def review_moderation_item(
        self,
        *,
        queue_id: str,
        reviewer_id: str,
        status: str,
        note: Optional[str],
    ) -> Optional[ModerationQueue]:
        item = await self._repository.get_moderation_item(queue_id)
        if not item:
            return None

        item.status = status
        item.reviewer_id = reviewer_id
        item.review_note = note
        item.reviewed_at = datetime.now(timezone.utc)
        updated = await self._repository.update_moderation_item(item)

        await self._log(
            action="moderation.reviewed",
            actor_id=reviewer_id,
            target_type="moderation",
            target_id=queue_id,
            detail_status=status,
            detail_note=note,
        )
        return updated

    async def submit_report(
        self,
        *,
        reporter_id: str,
        resource_type: str,
        resource_id: str,
        reason: str,
        subject_title: Optional[str],
        subject_category: Optional[str],
        source_service: Optional[str],
    ) -> ModerationQueue:
        item = ModerationQueue(
            resource_type=resource_type,
            resource_id=resource_id,
            submitted_by=reporter_id,
            reason=reason,
            status="pending",
            subject_title=subject_title,
            subject_category=subject_category,
            source_service=source_service,
        )
        item = await self._repository.create_moderation_item(item)

        await self._log(
            action="content.reported",
            actor_id=reporter_id,
            target_type=resource_type,
            target_id=resource_id,
            detail_reason=reason,
            detail_queue_id=item.id,
        )
        return item

    async def list_users(
        self,
        *,
        page: int,
        page_size: int,
        role: Optional[str],
        search: Optional[str],
    ) -> tuple[list[AdminUser], int]:
        return await self._repository.list_users(
            page=page,
            page_size=page_size,
            role=role,
            search=search,
        )

    async def get_user(self, user_id: str) -> Optional[AdminUser]:
        return await self._repository.get_user(user_id)

    async def suspend_user(
        self,
        *,
        user_id: str,
        actor_id: str,
        reason: Optional[str],
    ) -> AdminUser:
        user = await self._repository.get_user(user_id)
        if not user:
            user = AdminUser(id=user_id, role="tourist", is_suspended=False, is_verified=False)
            user = await self._repository.create_user(user)

        user.is_suspended = True
        user.suspended_reason = reason
        user.suspended_by = actor_id
        user.suspended_at = datetime.now(timezone.utc)
        updated = await self._repository.update_user(user)

        await self._log(
            action="user.suspended",
            actor_id=actor_id,
            target_type="user",
            target_id=user_id,
            detail_reason=reason,
        )
        return updated

    async def unsuspend_user(self, *, user_id: str, actor_id: str) -> Optional[AdminUser]:
        user = await self._repository.get_user(user_id)
        if not user:
            return None

        user.is_suspended = False
        user.unsuspended_by = actor_id
        user.unsuspended_at = datetime.now(timezone.utc)
        updated = await self._repository.update_user(user)

        await self._log(
            action="user.unsuspended",
            actor_id=actor_id,
            target_type="user",
            target_id=user_id,
        )
        return updated

    async def verify_user(self, *, user_id: str, actor_id: str) -> AdminUser:
        user = await self._repository.get_user(user_id)
        if not user:
            user = AdminUser(id=user_id, role="tourist", is_suspended=False, is_verified=False)
            user = await self._repository.create_user(user)

        user.is_verified = True
        user.verified_by = actor_id
        user.verified_at = datetime.now(timezone.utc)
        updated = await self._repository.update_user(user)

        await self._log(
            action="user.verified",
            actor_id=actor_id,
            target_type="user",
            target_id=user_id,
        )
        return updated

    async def list_flags(self) -> list[FeatureFlag]:
        return await self._repository.list_flags()

    async def upsert_flag(
        self,
        *,
        flag_key: str,
        enabled: bool,
        actor_id: str,
        description: Optional[str],
        rollout_percentage: int,
        owner_group: Optional[str],
    ) -> FeatureFlag:
        normalized_key = flag_key.strip().lower().replace(" ", "_")
        flag = await self._repository.get_flag_by_key(normalized_key)
        state = "active" if enabled else "inactive"

        if not flag:
            flag = FeatureFlag(
                key=normalized_key,
                description=description,
                status=state,
                rollout_percentage=rollout_percentage,
                owner_group=owner_group,
            )
            flag = await self._repository.create_flag(flag)
        else:
            flag.status = state
            flag.rollout_percentage = rollout_percentage
            if description is not None:
                flag.description = description
            if owner_group is not None:
                flag.owner_group = owner_group
            flag = await self._repository.update_flag(flag)

        await self._log(
            action="flag.updated",
            actor_id=actor_id,
            target_type="feature_flag",
            target_id=normalized_key,
            detail_status=state,
            detail_note=f"rollout={rollout_percentage}",
        )
        return flag

    async def list_audit_logs(
        self,
        *,
        page: int,
        page_size: int,
        action: Optional[str],
    ) -> tuple[list[AuditLog], int]:
        return await self._repository.list_audit_logs(page=page, page_size=page_size, action=action)

    async def list_announcements(
        self,
        *,
        page: int,
        page_size: int,
        active_only: bool,
    ) -> tuple[list[Announcement], int]:
        return await self._repository.list_announcements(
            page=page,
            page_size=page_size,
            active_only=active_only,
        )

    async def create_announcement(
        self,
        *,
        title: str,
        body: str,
        audience: str,
        status: str,
        priority: str,
        created_by: str,
        starts_at: Optional[datetime],
        ends_at: Optional[datetime],
    ) -> Announcement:
        announcement = Announcement(
            title=title,
            body=body,
            audience=audience,
            status=status,
            priority=priority,
            created_by=created_by,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        announcement = await self._repository.create_announcement(announcement)

        await self._log(
            action="announcement.created",
            actor_id=created_by,
            target_type="announcement",
            target_id=announcement.id,
            detail_note=f"{title} ({audience})",
            detail_status=status,
        )
        return announcement

    async def update_announcement(
        self,
        *,
        announcement_id: str,
        actor_id: str,
        title: Optional[str],
        body: Optional[str],
        audience: Optional[str],
        status: Optional[str],
        priority: Optional[str],
        starts_at: Optional[datetime],
        ends_at: Optional[datetime],
    ) -> Optional[Announcement]:
        announcement = await self._repository.get_announcement(announcement_id)
        if not announcement:
            return None

        if title is not None:
            announcement.title = title
        if body is not None:
            announcement.body = body
        if audience is not None:
            announcement.audience = audience
        if status is not None:
            announcement.status = status
        if priority is not None:
            announcement.priority = priority
        if starts_at is not None:
            announcement.starts_at = starts_at
        if ends_at is not None:
            announcement.ends_at = ends_at

        announcement = await self._repository.update_announcement(announcement)

        await self._log(
            action="announcement.updated",
            actor_id=actor_id,
            target_type="announcement",
            target_id=announcement_id,
            detail_status=announcement.status,
        )
        return announcement

    async def delete_announcement(self, *, announcement_id: str, actor_id: str) -> bool:
        announcement = await self._repository.get_announcement(announcement_id)
        if not announcement:
            return False

        await self._repository.delete_announcement(announcement)

        await self._log(
            action="announcement.deleted",
            actor_id=actor_id,
            target_type="announcement",
            target_id=announcement_id,
        )
        return True
