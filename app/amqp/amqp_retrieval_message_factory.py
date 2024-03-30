from typing import Any

from app.amqp.abstract_amqp_message_factory import AbstractAMQPMessageFactory
from app.db.daos.retrieval_dao import RetrievalDAO
from app.db.models.retrieval import Retrieval as DbRetrieval
from app.db.session import async_session
from app.models.retrieval import Retrieval as RetrievalModel


class AMQPRetrievalMessageFactory(AbstractAMQPMessageFactory):
    """Factory for building AMQP messages related to harvesting states."""

    def _build_routing_key(self) -> str:
        if "error" in self.content:
            return "event.references.retrieval.error"
        return self.settings.amqp_retrieval_event_routing_key

    async def _build_payload(self) -> dict[str, Any]:
        if "error" in self.content:
            return {
                "type": self.content.get("type"),
                "parameters": self.content.get("parameters"),
                "message": self.content.get("message"),
            }
        assert "id" in self.content, "Retrieval id is required"
        async with async_session() as session:
            retrieval: DbRetrieval = await RetrievalDAO(
                session
            ).get_retrieval_display_info_by_id(self.content.get("id"))
            retrieval_representation: RetrievalModel = RetrievalModel.model_validate(
                retrieval
            )
        return retrieval_representation.model_dump(exclude={"id": True})
