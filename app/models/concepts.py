from pydantic import BaseModel, ConfigDict

from app.models.literal_fields import LiteralField


class Concept(BaseModel):
    """
    Pydantic model matching Concept sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    uri: str | None

    labels: list[LiteralField] = []
