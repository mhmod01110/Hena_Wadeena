"""Dependency injection wiring for auth-service."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.token_repository import SqlAlchemyTokenRepository
from repositories.otp_repository import SqlAlchemyOTPRepository
from repositories.event_repository import SqlAlchemyEventRepository
from services.auth_service import AuthService
from services.otp_service import OTPService


# ── Repository providers ─────────────────────────────────────────────────────

def get_token_repo(session: AsyncSession = Depends(get_session)) -> SqlAlchemyTokenRepository:
    return SqlAlchemyTokenRepository(session)


def get_otp_repo(session: AsyncSession = Depends(get_session)) -> SqlAlchemyOTPRepository:
    return SqlAlchemyOTPRepository(session)


def get_event_repo(session: AsyncSession = Depends(get_session)) -> SqlAlchemyEventRepository:
    return SqlAlchemyEventRepository(session)


# ── Service providers ────────────────────────────────────────────────────────

def get_auth_service(
    token_repo: SqlAlchemyTokenRepository = Depends(get_token_repo),
    event_repo: SqlAlchemyEventRepository = Depends(get_event_repo),
) -> AuthService:
    return AuthService(token_repo=token_repo, event_repo=event_repo)


def get_otp_service(
    otp_repo: SqlAlchemyOTPRepository = Depends(get_otp_repo),
) -> OTPService:
    return OTPService(otp_repo=otp_repo)
