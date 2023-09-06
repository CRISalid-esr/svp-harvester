from pydantic import BaseModel


class RetrievalService:
    """Main harvesters orchestration service"""

    def __init__(self, entity: BaseModel):
        """Init RetrievalService class"""
        self.entity = entity

    def retrieve(self):
        return True
