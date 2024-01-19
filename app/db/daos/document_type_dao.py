from sqlalchemy import select

from app.db.abstract_dao import AbstractDAO
from app.db.models.document_type import DocumentType


class DocumentTypeDAO(AbstractDAO):
    """
    Data Access Object for document type
    """

    async def get_document_type_by_uri(self, uri: str) -> DocumentType | None:
        """
        Get a document type by its uri

        :param uri: uri of the document type
        :return: the document type or None if not found
        """
        query = select(DocumentType).where(DocumentType.uri == uri)

        return await self.db_session.scalar(query)
