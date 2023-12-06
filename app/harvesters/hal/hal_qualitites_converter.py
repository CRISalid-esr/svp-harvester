class HalQualitiesConverter:
    """
    Use mapping table ton convert hal role values to loc roles values
    through a static method
    """

    ROLES_MAPPING = {
        "aut": "aut",
        "scientific_editor": "edc",
    }

    @staticmethod
    def convert(quality: str) -> str:
        """
        Convert hal role value to loc role value
        :param quality: hal role value
        :return: loc role value
        """
        return HalQualitiesConverter.ROLES_MAPPING.get(quality, "aut")
