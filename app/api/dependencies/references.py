"""References dependencies."""

from typing import Optional

from fastapi import Depends
from pydantic import create_model

from app.config import get_app_settings
from app.models.people import Person

settings = get_app_settings()
identifier_params = {
    id_.get("key"): (Optional[str], None) for id_ in settings.identifiers
}

identifiers_model = create_model("Query", **identifier_params)


def build_person_from_fields(
    name: str | None = None,
    identifiers: identifiers_model = Depends(),
) -> Person:
    """
    Build a person from the provided fields.

    :param name: name of the entity
    :param identifiers: identifiers of the entity
    :return: person
    """
    parameters = identifiers.dict()
    return Person.model_validate(
        {
            "name": name,
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


def build_person_from_fields_optional(
    name: str | None = None,
    identifiers: identifiers_model = Depends(),
):
    """
    wrapper to make the dependency optional
    """
    if not name and not any(identifiers.dict().values()):
        return None

    return build_person_from_fields(name, identifiers)
