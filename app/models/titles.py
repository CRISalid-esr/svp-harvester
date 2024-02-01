from pydantic import ConfigDict

from app.models.literal_fields import ReferenceLiteralField


class Title(ReferenceLiteralField):
    """
    Pydantic model matching Title sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)
