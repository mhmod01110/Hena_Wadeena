"""SQLAlchemy repository for admin domain."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import AdminUser, Announcement, AuditLog, FeatureFlag, ModerationQueue


class SqlAlchemyAdminRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def list_moderation_items(
        self,
        *,
        page: int,
        page_size: int,
        status_filter: Optional[str],
        resource_type: Optional[str],
    ) -> tuple[list[ModerationQueue], int]:
        query = select(ModerationQueue)
        if status_filter:
            query = query.where(ModerationQueue.status == status_filter)
        if resource_type:
            query = query.where(ModerationQueue.resource_type == resource_type)

        count_query = select(func.count()).select_from(query.subquery())
        total = int((await self._session.execute(count_query)).scalar_one() or 0)

        result = await self._session.execute(
            query.order_by(ModerationQueue.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_moderation_item(self, queue_id: str) -> Optional[ModerationQueue]:
        result = await self._session.execute(select(ModerationQueue).where(ModerationQueue.id == queue_id))
        return result.scalar_one_or_none()

    async def create_moderation_item(self, item: ModerationQueue) -> ModerationQueue:
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def update_moderation_item(self, item: ModerationQueue) -> ModerationQueue:
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def list_users(
        self,
        *,
        page: int,
        page_size: int,
        role: Optional[str],
        search: Optional[str],
    ) -> tuple[list[AdminUser], int]:
        query = select(AdminUser)
        if role:
            query = query.where(AdminUser.role == role)
        if search:
            like = f"%{search}%"
            query = query.where(
                (AdminUser.id.ilike(like))
                | (AdminUser.display_name.ilike(like))
                | (AdminUser.email.ilike(like))
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = int((await self._session.execute(count_query)).scalar_one() or 0)

        result = await self._session.execute(
            query.order_by(AdminUser.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_user(self, user_id: str) -> Optional[AdminUser]:
        result = await self._session.execute(select(AdminUser).where(AdminUser.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, user: AdminUser) -> AdminUser:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update_user(self, user: AdminUser) -> AdminUser:
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def list_flags(self) -> list[FeatureFlag]:
        result = await self._session.execute(select(FeatureFlag).order_by(FeatureFlag.key.asc()))
        return list(result.scalars().all())

    async def get_flag_by_key(self, flag_key: str) -> Optional[FeatureFlag]:
        result = await self._session.execute(select(FeatureFlag).where(FeatureFlag.key == flag_key))
        return result.scalar_one_or_none()

    async def create_flag(self, flag: FeatureFlag) -> FeatureFlag:
        self._session.add(flag)
        await self._session.flush()
        await self._session.refresh(flag)
        return flag

    async def update_flag(self, flag: FeatureFlag) -> FeatureFlag:
        await self._session.flush()
        await self._session.refresh(flag)
        return flag

    async def list_audit_logs(
        self,
        *,
        page: int,
        page_size: int,
        action: Optional[str],
    ) -> tuple[list[AuditLog], int]:
        query = select(AuditLog)
        if action:
            query = query.where(AuditLog.action == action)

        count_query = select(func.count()).select_from(query.subquery())
        total = int((await self._session.execute(count_query)).scalar_one() or 0)

        result = await self._session.execute(
            query.order_by(AuditLog.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create_audit_log(self, log: AuditLog) -> AuditLog:
        self._session.add(log)
        await self._session.flush()
        await self._session.refresh(log)
        return log

    async def list_announcements(
        self,
        *,
        page: int,
        page_size: int,
        active_only: bool,
    ) -> tuple[list[Announcement], int]:
        query = select(Announcement)
        now = datetime.now(timezone.utc)
        if active_only:
            query = query.where(Announcement.status == "active")
            query = query.where((Announcement.starts_at.is_(None)) | (Announcement.starts_at <= now))
            query = query.where((Announcement.ends_at.is_(None)) | (Announcement.ends_at >= now))

        count_query = select(func.count()).select_from(query.subquery())
        total = int((await self._session.execute(count_query)).scalar_one() or 0)

        result = await self._session.execute(
            query.order_by(Announcement.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def get_announcement(self, announcement_id: str) -> Optional[Announcement]:
        result = await self._session.execute(select(Announcement).where(Announcement.id == announcement_id))
        return result.scalar_one_or_none()

    async def create_announcement(self, announcement: Announcement) -> Announcement:
        self._session.add(announcement)
        await self._session.flush()
        await self._session.refresh(announcement)
        return announcement

    async def update_announcement(self, announcement: Announcement) -> Announcement:
        await self._session.flush()
        await self._session.refresh(announcement)
        return announcement

    async def delete_announcement(self, announcement: Announcement) -> None:
        await self._session.delete(announcement)
        await self._session.flush()
