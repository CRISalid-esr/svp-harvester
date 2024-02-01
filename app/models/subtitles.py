from pydantic import ConfigDict

from app.models.literal_fields import ReferenceLiteralField


class Subtitle(ReferenceLiteralField):
    """
    Pydantic model matching Subtitle sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)
