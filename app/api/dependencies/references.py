"""References dependencies."""
from typing import Annotated

from fastapi import Depends

from app.config import get_app_settings
from app.models.people import Person
from app.settings.app_settings import AppSettings


def build_person_from_fields(
    settings: Annotated[AppSettings, Depends(get_app_settings)],
    first_name: str | None = None,
    last_name: str | None = None,
    # pylint: disable=unused-argument
    idref: str | None = None,
    orcid: str | None = None,
    id_hal_i: str | None = None,
) -> Person:
    """

    :param first_name: first name
    :param last_name: last name
    :param idref: IdRef identifier
    :param orcid: ORCID identifier
    :param id_hal_i: HAL numeric identifier
    :return: person
    """
    parameters = dict(locals())
    return Person.model_validate(
        {
            "first_name": first_name,
            "last_name": last_name,
            "identifiers": [
                {
                    "type": identifier.get("key"),
                    "value": parameters[identifier.get("key")],
                }
                for identifier in settings.identifiers
                if parameters.get(identifier.get("key"), None) is not None
            ],
        }
    )
