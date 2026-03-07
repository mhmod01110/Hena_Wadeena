"""KYC routes — document upload and status."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import KYCUpload, KYCStatus
from services.user_service import add_kyc_document, get_user_kyc

router = APIRouter()


def get_current_user_id(request: Request) -> str:
    """Extract user ID from X-User-Id header."""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    return user_id


@router.post("/me/kyc", response_model=KYCStatus, status_code=201)
async def upload_kyc(
    data: KYCUpload,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Upload a KYC document for verification."""
    user_id = get_current_user_id(request)

    kyc = await add_kyc_document(
        db=db,
        user_id=user_id,
        doc_type=data.doc_type,
        doc_url=data.doc_url,
    )

    return KYCStatus(
        id=str(kyc.id),
        doc_type=kyc.doc_type,
        doc_url=kyc.doc_url,
        status=kyc.status,
        rejection_reason=kyc.rejection_reason,
        created_at=kyc.created_at,
    )


@router.get("/me/kyc", response_model=list[KYCStatus])
async def get_kyc_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Get all KYC documents and their status."""
    user_id = get_current_user_id(request)
    documents = await get_user_kyc(db, user_id)

    return [
        KYCStatus(
            id=str(doc.id),
            doc_type=doc.doc_type,
            doc_url=doc.doc_url,
            status=doc.status,
            rejection_reason=doc.rejection_reason,
            created_at=doc.created_at,
        )
        for doc in documents
    ]
