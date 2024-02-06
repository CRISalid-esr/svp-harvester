from typing import Any, Dict, List
from app.db.abstract_dao import AbstractDAO
from app.models.people import Person
from app.db.session import async_session


async def fetch_summary(
    dao_class: AbstractDAO,
    session: async_session,
    params: dict,
    entity: Person,
    extra_args: Dict[str, Any] = None,
) -> List:
    """
    Fetch summary (retrieval or references) for a given entity
    :param dao_class: dao class to use
    :param session: session to use
    :param params: parameters to fetch
    :param entity: entity to search
    :param extra_args: extra arguments to pass to the dao
    :return: Summary
    """
    dao_instance = dao_class(session)
    method = getattr(
        dao_instance,
        (
            "get_retrievals_summary"
            if dao_class.__name__ == "RetrievalDAO"
            else "get_references_summary"
        ),
    )
    args = {
        "filter_harvester": {
            "event_types": params["events"],
            "nullify": params["nullify"],
            "harvester": params["harvester"],
        },
        "date_interval": (params["date_start"], params["date_end"]),
        "entity": entity,
    }
    if extra_args:
        args.update(extra_args)
    result = await method(**args)
    return result
