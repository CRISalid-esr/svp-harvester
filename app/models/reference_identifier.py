from pydantic import BaseModel, ConfigDict, field_validator

from app.db.models.reference_identifier import (
    ReferenceIdentifier as DbReferenceIdentifier,
)


class ReferenceIdentifier(BaseModel):
    """
    Pydantic model matching PublicationIdentifier sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    type: str
    value: str

    @field_validator("value")
    @classmethod
    def _normalize_doi(cls, v, info):
        if info.data.get("type") == DbReferenceIdentifier.IdentifierType.DOI.value:
            prefixes = ["urn:doi:", "https://doi.org/"]
            for prefix in prefixes:
                if v.lower().startswith(prefix):
                    return v[len(prefix) :]
        return v
