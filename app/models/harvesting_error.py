from pydantic import BaseModel, ConfigDict


class HarvestingError(BaseModel):
    """
    Pydantic model matching HarvestingError sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    harvesting_id: int

    name: str

    message: str
