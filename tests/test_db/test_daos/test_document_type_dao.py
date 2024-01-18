import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.daos.document_type_dao import DocumentTypeDAO
from app.db.models.document_type import DocumentType


@pytest.mark.asyncio
async def test_get_document_type_by_uri(
    async_session: AsyncSession,
):
    """
    WHEN a document type is added to the database
    THEN it can be retrieved by its uri
    """
    document_type = DocumentType(uri="test_uri", label="Test Document Type")
    async_session.add(document_type)
    await async_session.commit()
    dao = DocumentTypeDAO(async_session)
    result = await dao.get_document_type_by_uri("test_uri")
    assert result is not None
    assert result.uri == "test_uri"
    assert result.label == "Test Document Type"
