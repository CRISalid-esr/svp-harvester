from pydantic import ConfigDict

from app.models.literal_fields import ReferenceLiteralField


class Abstract(ReferenceLiteralField):
    """
    Pydantic model matching Abstract sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)
