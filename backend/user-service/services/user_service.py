"""User service business logic."""

from datetime import datetime, timezone
from typing import Optional

from interfaces.user_repository import IUserRepository
from interfaces.kyc_repository import IKYCRepository
from interfaces.preference_repository import IPreferenceRepository
from models import User, UserKYC, UserPreference


class UserService:
    """Application service for user, preference, and KYC operations."""

    def __init__(
        self,
        user_repo: IUserRepository,
        kyc_repo: IKYCRepository,
        pref_repo: IPreferenceRepository,
    ):
        self._user_repo = user_repo
        self._kyc_repo = kyc_repo
        self._pref_repo = pref_repo

    async def create_user(
        self,
        email: Optional[str],
        phone: Optional[str],
        full_name: str,
        password_hash: Optional[str] = None,
        role: str = "tourist",
        city: Optional[str] = None,
        organization: Optional[str] = None,
        documents: Optional[list[dict]] = None,
    ) -> User:
        if await self._user_repo.exists(email, phone):
            raise ValueError("User with this email or phone already exists")

        user = User(
            email=email,
            phone=phone,
            full_name=full_name,
            password_hash=password_hash,
            role=role,
            city=city,
            organization=organization,
        )
        user = await self._user_repo.create(user)

        for document in documents or []:
            doc_type = document.get("doc_type")
            if not doc_type:
                continue

            file_name = str(document.get("file_name") or doc_type).replace(" ", "_")
            await self.add_kyc_document(
                user_id=str(user.id),
                doc_type=doc_type,
                doc_url=f"client-upload://{file_name}",
            )

        return user

    async def get_user(self, user_id: str) -> Optional[User]:
        return await self._user_repo.get_by_id(str(user_id))

    async def lookup_user(self, email: Optional[str] = None, phone: Optional[str] = None) -> Optional[User]:
        if email:
            return await self._user_repo.find_by_email(email)
        if phone:
            return await self._user_repo.find_by_phone(phone)
        return None

    async def update_profile(self, user_id: str, **fields) -> Optional[User]:
        user = await self.get_user(user_id)
        if not user:
            return None

        email = fields.get("email")
        if email and email != user.email:
            existing_user = await self._user_repo.find_by_email(email)
            if existing_user and str(existing_user.id) != str(user.id):
                raise ValueError("User with this email already exists")

        phone = fields.get("phone")
        if phone and phone != user.phone:
            existing_user = await self._user_repo.find_by_phone(phone)
            if existing_user and str(existing_user.id) != str(user.id):
                raise ValueError("User with this phone already exists")

        for key, value in fields.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.now(timezone.utc)
        return await self._user_repo.update(user)

    async def get_preferences(self, user_id: str) -> Optional[UserPreference]:
        return await self._pref_repo.get(str(user_id))

    async def update_preferences(self, user_id: str, **fields) -> UserPreference:
        pref = UserPreference(user_id=str(user_id), **fields)
        return await self._pref_repo.upsert(pref)

    async def add_kyc_document(self, user_id: str, doc_type: str, doc_url: str) -> UserKYC:
        kyc = UserKYC(
            user_id=str(user_id),
            doc_type=doc_type,
            doc_url=doc_url,
        )
        return await self._kyc_repo.create(kyc)

    async def get_kyc_documents(self, user_id: str) -> list[UserKYC]:
        return await self._kyc_repo.get_by_user_id(str(user_id))
