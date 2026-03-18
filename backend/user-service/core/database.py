"""User service database setup."""

import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from shared.core.database import create_db_engine, create_session_factory, Base, ensure_database_exists
from shared.utils.security import hash_password
from core.config import settings

engine = create_db_engine(settings.USER_DATABASE_URL, echo=settings.DEBUG)
SessionFactory = create_session_factory(engine)


async def get_session() -> AsyncSession:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    await ensure_database_exists(settings.USER_DATABASE_URL, echo=settings.DEBUG)
    import models  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_run_runtime_migrations)
        await conn.run_sync(_seed_default_users)


def _run_runtime_migrations(sync_conn) -> None:
    inspector = inspect(sync_conn)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    if "city" not in existing_columns:
        sync_conn.execute(text("ALTER TABLE users ADD COLUMN city VARCHAR(100) NULL"))
    if "organization" not in existing_columns:
        sync_conn.execute(text("ALTER TABLE users ADD COLUMN organization VARCHAR(255) NULL"))


def _seed_default_users(sync_conn) -> None:
    from models import User, UserPreference, UserKYC

    session = Session(bind=sync_conn)
    try:
        if session.query(User).count() > 0:
            return

        now = datetime.now(timezone.utc)
        default_password = "Pass@12345"

        users = [
            User(
                id="00000000-0000-0000-0000-000000000001",
                email="admin@hena.local",
                phone="01000000001",
                full_name="Platform Admin",
                password_hash=hash_password(default_password),
                role="admin",
                city="kharga",
                organization="Hena Wadeena",
                status="active",
                language="ar",
                verified_at=now,
            ),
            User(
                id="00000000-0000-0000-0000-000000000002",
                email="reviewer@hena.local",
                phone="01000000002",
                full_name="Content Reviewer",
                password_hash=hash_password(default_password),
                role="reviewer",
                city="kharga",
                organization="Hena Wadeena",
                status="active",
                language="ar",
                verified_at=now,
            ),
            User(
                id="00000000-0000-0000-0000-000000000010",
                email="ops.admin@hena.local",
                phone="01000000010",
                full_name="Operations Admin",
                password_hash=hash_password(default_password),
                role="admin",
                city="kharga",
                organization="Hena Wadeena",
                status="active",
                language="en",
                verified_at=now,
            ),
            User(
                id="00000000-0000-0000-0000-000000000011",
                email="senior.reviewer@hena.local",
                phone="01000000011",
                full_name="Senior Reviewer",
                password_hash=hash_password(default_password),
                role="reviewer",
                city="dakhla",
                organization="Hena Wadeena",
                status="active",
                language="en",
                verified_at=now,
            ),
            User(
                id="00000000-0000-0000-0000-000000000003",
                email="guide@hena.local",
                phone="01000000003",
                full_name="Valley Guide",
                password_hash=hash_password(default_password),
                role="guide",
                city="dakhla",
                organization="Independent",
                status="active",
                language="ar",
                verified_at=now,
            ),
            User(
                id="00000000-0000-0000-0000-000000000004",
                email="tourist@hena.local",
                phone="01000000004",
                full_name="Demo Tourist",
                password_hash=hash_password(default_password),
                role="tourist",
                city="kharga",
                organization="",
                status="active",
                language="ar",
                verified_at=now,
            ),
            User(
                id="00000000-0000-0000-0000-000000000005",
                email="investor@hena.local",
                phone="01000000005",
                full_name="Demo Investor",
                password_hash=hash_password(default_password),
                role="investor",
                city="kharga",
                organization="Valley Capital",
                status="active",
                language="ar",
                verified_at=now,
            ),
            User(
                id="00000000-0000-0000-0000-000000000006",
                email="merchant@hena.local",
                phone="01000000006",
                full_name="Demo Merchant",
                password_hash=hash_password(default_password),
                role="merchant",
                city="farafra",
                organization="Oasis Supplies",
                status="active",
                language="ar",
                verified_at=now,
            ),
            User(
                id="00000000-0000-0000-0000-000000000007",
                email="citizen@hena.local",
                phone="01000000007",
                full_name="Local Citizen",
                password_hash=hash_password(default_password),
                role="local_citizen",
                city="kharga",
                organization="",
                status="active",
                language="ar",
            ),
        ]

        session.add_all(users)
        session.flush()

        session.add_all(
            [
                UserPreference(user_id=user.id, notify_push=True, notify_email=True, notify_sms=False)
                for user in users
            ]
        )

        session.add_all(
            [
                UserKYC(
                    user_id="00000000-0000-0000-0000-000000000003",
                    doc_type="guide_license",
                    doc_url="seed://guide_license.pdf",
                    status="approved",
                    reviewed_by="00000000-0000-0000-0000-000000000001",
                    reviewed_at=now,
                ),
                UserKYC(
                    user_id="00000000-0000-0000-0000-000000000005",
                    doc_type="national_id",
                    doc_url="seed://investor_id.pdf",
                    status="approved",
                    reviewed_by="00000000-0000-0000-0000-000000000001",
                    reviewed_at=now,
                ),
                UserKYC(
                    user_id="00000000-0000-0000-0000-000000000006",
                    doc_type="commercial_register",
                    doc_url="seed://merchant_register.pdf",
                    status="approved",
                    reviewed_by="00000000-0000-0000-0000-000000000001",
                    reviewed_at=now,
                ),
            ]
        )

        session.commit()
    finally:
        session.close()

