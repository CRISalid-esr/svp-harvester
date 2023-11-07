from pydantic import ConfigDict

from app.models.literal_fields import LiteralField


class Abstract(LiteralField):
    """
    Pydantic model matching Abstract sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)
