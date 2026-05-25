from pydantic import BaseModel, ConfigDict, model_validator


class Topic(BaseModel):
    """
    Pydantic model for a topic, built from a ReferenceTopic association object.
    source_id, uri and label are flattened from the nested Topic ORM object.
    score comes directly from ReferenceTopic.
    """

    model_config = ConfigDict(from_attributes=True)

    source_id: str
    uri: str
    label: str
    score: float

    @model_validator(mode="before")
    @classmethod
    def _from_reference_topic(cls, data):
        if hasattr(data, "topic"):
            return {
                "source_id": data.topic.source_id,
                "uri": data.topic.uri,
                "label": data.topic.display_name,
                "score": data.score,
            }
        return data
