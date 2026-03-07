"""OTP service — pure business logic for OTP generation and verification."""

import random
from datetime import datetime, timedelta, timezone

from shared.utils.security import hash_token

from interfaces.otp_repository import IOTPRepository
from models import OTPCode
from core.config import settings


class OTPService:
    """
    OTP business logic. Depends on IOTPRepository (DIP).
    SMS sending is abstracted — currently mocked.
    """

    def __init__(self, otp_repo: IOTPRepository):
        self._otp_repo = otp_repo

    @staticmethod
    def _generate_code(length: int = 6) -> str:
        return "".join(str(random.randint(0, 9)) for _ in range(length))

    async def request_otp(self, target: str, purpose: str) -> str:
        """Generate, store, and 'send' an OTP. Returns the plain code."""
        code = self._generate_code(settings.OTP_LENGTH)

        otp_record = OTPCode(
            target=target,
            purpose=purpose,
            code_hash=hash_token(code),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )
        await self._otp_repo.store(otp_record)

        # TODO: inject an ISMSGateway for real SMS delivery
        print(f"📱 [OTP] Code for {target}: {code} (purpose: {purpose})")

        return code

    async def verify_otp(self, target: str, code: str, purpose: str) -> bool:
        """Verify an OTP code against stored records."""
        code_hash = hash_token(code)
        record = await self._otp_repo.find_valid(target, purpose, code_hash)

        if record is None:
            await self._otp_repo.increment_attempts(target, purpose)
            return False

        await self._otp_repo.mark_used(record)
        return True
