"""Abstract interface for KYC repository."""

from abc import ABC, abstractmethod

from models import UserKYC


class IKYCRepository(ABC):

    @abstractmethod
    async def create(self, kyc: UserKYC) -> UserKYC:
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> list[UserKYC]:
        ...
