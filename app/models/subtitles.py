from pydantic import ConfigDict

from app.models.literal_fields import LiteralField


class Subtitle(LiteralField):
    """
    Pydantic model matching Subtitle sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)
