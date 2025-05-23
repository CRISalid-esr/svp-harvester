from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class HalCustomMetadataSchema(BaseModel):
    """
    Custom metadata schema for HAL references.
    """

    hal_collection_codes: List[str] = []
    hal_submit_type: Optional["HalCustomMetadataSchema.HalSubmitType"] = None

    class HalSubmitType(str, Enum):
        """
        Possible values for the hal_submit_type field
        """

        NOTICE = "notice"
        FILE = "file"
        ANNEX = "annex"
