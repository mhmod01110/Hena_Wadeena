"""Admin service database setup."""

import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.config import settings
from shared.core.database import Base, create_db_engine, create_session_factory, ensure_database_exists

engine = create_db_engine(settings.ADMIN_DATABASE_URL, echo=settings.DEBUG)
SessionFactory = create_session_factory(engine)


async def get_session() -> AsyncSession:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    await ensure_database_exists(settings.ADMIN_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_seed_data)


def _seed_data(sync_conn) -> None:
    from models import AdminUser, Announcement, AuditLog, FeatureFlag, ModerationQueue

    session = Session(bind=sync_conn)
    try:
        if session.query(AdminUser).count() > 0:
            return

        users = [
            AdminUser(
                id="00000000-0000-0000-0000-000000000001",
                display_name="Platform Admin",
                email="admin@hena.local",
                role="admin",
                is_suspended=False,
                is_verified=True,
                verified_by="system",
            ),
            AdminUser(
                id="00000000-0000-0000-0000-000000000010",
                display_name="Operations Admin",
                email="ops.admin@hena.local",
                role="admin",
                is_suspended=False,
                is_verified=True,
                verified_by="system",
            ),
            AdminUser(
                id="00000000-0000-0000-0000-000000000002",
                display_name="Content Reviewer",
                email="reviewer@hena.local",
                role="reviewer",
                is_suspended=False,
                is_verified=True,
                verified_by="system",
            ),
            AdminUser(
                id="00000000-0000-0000-0000-000000000011",
                display_name="Senior Reviewer",
                email="senior.reviewer@hena.local",
                role="reviewer",
                is_suspended=False,
                is_verified=True,
                verified_by="system",
            ),
            AdminUser(
                id="00000000-0000-0000-0000-000000000005",
                display_name="Demo Investor",
                email="investor@hena.local",
                role="investor",
                is_suspended=False,
                is_verified=True,
                verified_by="00000000-0000-0000-0000-000000000001",
            ),
            AdminUser(
                id="00000000-0000-0000-0000-000000000006",
                display_name="Demo Merchant",
                email="merchant@hena.local",
                role="merchant",
                is_suspended=False,
                is_verified=True,
                verified_by="00000000-0000-0000-0000-000000000001",
            ),
            AdminUser(
                id="00000000-0000-0000-0000-000000000004",
                display_name="Demo Tourist",
                email="tourist@hena.local",
                role="tourist",
                is_suspended=False,
                is_verified=True,
                verified_by="00000000-0000-0000-0000-000000000001",
            ),
        ]

        flags = [
            FeatureFlag(
                key="admin_dashboard_enabled",
                description="Enable admin dashboard pages",
                status="active",
                rollout_percentage=100,
                owner_group="platform",
            ),
            FeatureFlag(
                key="reviewer_queue_enabled",
                description="Enable reviewer moderation queue",
                status="active",
                rollout_percentage=100,
                owner_group="operations",
            ),
            FeatureFlag(
                key="experimental_ai_recommendations",
                description="Gate AI recommendation experiments",
                status="inactive",
                rollout_percentage=10,
                owner_group="ai-team",
            ),
        ]

        moderation_items = [
            ModerationQueue(
                resource_type="listing",
                resource_id="seed-listing-1",
                submitted_by="00000000-0000-0000-0000-000000000006",
                reason="Please verify business documents for listing activation.",
                status="pending",
                subject_title="Green Valley Farms",
                subject_category="supplier",
                source_service="market-service",
            ),
            ModerationQueue(
                resource_type="guide_profile",
                resource_id="seed-guide-2",
                submitted_by="00000000-0000-0000-0000-000000000003",
                reason="Guide profile pending manual verification.",
                status="pending",
                subject_title="Fatma Hassan",
                subject_category="guide",
                source_service="guide-service",
            ),
            ModerationQueue(
                resource_type="opportunity",
                resource_id="seed-opportunity-3",
                submitted_by="00000000-0000-0000-0000-000000000005",
                reason="Investment feasibility requires reviewer approval.",
                status="approved",
                reviewer_id="00000000-0000-0000-0000-000000000002",
                review_note="Financial assumptions validated with projected ROI range.",
                subject_title="Solar Farm Phase 1",
                subject_category="investment",
                source_service="investment-service",
            ),
        ]

        announcements = [
            Announcement(
                title="Welcome to Hena Wadeena",
                body="Platform services are now live across tourism, logistics, and investment domains.",
                audience="all",
                status="active",
                priority="normal",
                created_by="00000000-0000-0000-0000-000000000001",
            ),
            Announcement(
                title="Reviewer Workflow Update",
                body="Reviewers can now approve or reject moderation items directly from dashboard.",
                audience="admin_reviewers",
                status="active",
                priority="high",
                created_by="00000000-0000-0000-0000-000000000001",
            ),
        ]

        logs = [
            AuditLog(
                action="seed.initialized",
                actor_id="00000000-0000-0000-0000-000000000001",
                target_type="system",
                target_id="admin-service",
                detail_note="Initial admin seed data loaded",
            ),
            AuditLog(
                action="moderation.created",
                actor_id="00000000-0000-0000-0000-000000000006",
                target_type="listing",
                target_id="seed-listing-1",
                detail_status="pending",
                detail_queue_id="seed-listing-1",
            ),
        ]

        session.add_all(users + flags + moderation_items + announcements + logs)
        session.commit()
    finally:
        session.close()
