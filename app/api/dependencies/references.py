"""References dependencies."""
from app.models.identifiers import IdentifierTypeEnum
from app.models.people import Person


def build_person_from_fields(
    first_name: str | None = None,
    last_name: str | None = None,
    # pylint: disable=unused-argument
    idref: str | None = None,
    orcid: str | None = None,
    id_hal: str | None = None,
) -> Person:
    """

    :param first_name: first name
    :param last_name: last name
    :param idref: IdRef identifier
    :param orcid: ORCID identifier
    :param id_hal: HAL identifier
    :return: person
    """
    parameters = dict(locals())
    return Person.model_validate(
        {
            "first_name": first_name,
            "last_name": last_name,
            "identifiers": [
                {"type": id.value, "value": parameters[id.value]}
                for id in IdentifierTypeEnum
                if parameters[id.value] is not None
            ],
        }
    )
