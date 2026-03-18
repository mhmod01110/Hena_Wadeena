"""Service dependency providers."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from repositories.search_document_repository import SqlAlchemySearchDocumentRepository
from services.search_document_service import SearchDocumentService


def get_search_document_service(
    session: AsyncSession = Depends(get_session),
) -> SearchDocumentService:
    repository = SqlAlchemySearchDocumentRepository(session)
    return SearchDocumentService(repository)
