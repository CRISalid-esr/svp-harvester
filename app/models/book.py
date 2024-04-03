from pydantic import BaseModel, ConfigDict


class Book(BaseModel):
    """
    Pydantic
    """

    model_config = ConfigDict(from_attributes=True)

    title: str | None = None
    isbn10: str | None = None
    isbn13: str | None = None
    publisher: str | None = None
