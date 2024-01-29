from pydantic import BaseModel, ConfigDict, Field

from app.models.contributor import Contributor


class Contribution(BaseModel):
    """
    Pydantic model matching Contribution sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(exclude=True)

    rank: int | None  # TODO: does it need to be excluded?

    contributor: Contributor

    role: str
