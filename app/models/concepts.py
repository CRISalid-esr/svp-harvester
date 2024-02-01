from typing import List

from pydantic import BaseModel, ConfigDict, computed_field, Field

from app.models.labels import Label


class Concept(BaseModel):
    """
    Pydantic model matching Concept sql_alchemy model
    """

    model_config = ConfigDict(from_attributes=True)

    uri: str | None

    labels: list[Label] = Field(exclude=True, default=[])

    @computed_field
    @property
    def pref_labels(self) -> List[Label]:
        """
        Computed field for SKOS preferred labels

        :return:  List of SKOS preferred labels

        """
        # pylint: disable=not-an-iterable
        return [label for label in self.labels if label.preferred]

    @computed_field
    @property
    def alt_labels(self) -> List[Label]:
        """
        Computed field for SKOS alternative labels
        :return:  List of SKOS alternative labels
        """
        # pylint: disable=not-an-iterable
        return [label for label in self.labels if not label.preferred]
