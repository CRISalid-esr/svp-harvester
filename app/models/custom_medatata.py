from app.db.models.reference import Reference
from app.harvesters.hal.hal_custom_metadata_schema import HalCustomMetadataSchema


def register_custom_metadata_schemas():
    """
    Register custom metadata schemas for HAL.
    :return: None
    """
    Reference.register_custom_metadata_schema("hal", HalCustomMetadataSchema)
