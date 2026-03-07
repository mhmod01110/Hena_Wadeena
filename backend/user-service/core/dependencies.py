"""DI wiring for user-service."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.user_repository import SqlAlchemyUserRepository
from repositories.kyc_repository import SqlAlchemyKYCRepository
from repositories.preference_repository import SqlAlchemyPreferenceRepository
from services.user_service import UserService


def get_user_repo(session: AsyncSession = Depends(get_session)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_kyc_repo(session: AsyncSession = Depends(get_session)) -> SqlAlchemyKYCRepository:
    return SqlAlchemyKYCRepository(session)


def get_pref_repo(session: AsyncSession = Depends(get_session)) -> SqlAlchemyPreferenceRepository:
    return SqlAlchemyPreferenceRepository(session)


def get_user_service(
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repo),
    kyc_repo: SqlAlchemyKYCRepository = Depends(get_kyc_repo),
    pref_repo: SqlAlchemyPreferenceRepository = Depends(get_pref_repo),
) -> UserService:
    return UserService(user_repo=user_repo, kyc_repo=kyc_repo, pref_repo=pref_repo)
