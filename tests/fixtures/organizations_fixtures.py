from unittest import mock
import pytest
from app.db.models.organization import Organization as DbOrganization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.organizations.hal_organization_solver import HalOrganizationSolver
from app.services.organizations.open_alex_organization_solver import OpenAlexOrganizationSolver


def fake_hal_organization_solver(organization_id: str) -> DbOrganization:
    """
    Fake hal organization solver
    :return: fake Organization
    """
    return DbOrganization(
        source="hal",
        source_identifier="000000",
        name="Organization Test",
        type="laboratory",
        identifiers=[OrganizationIdentifier(type="idref", value="00000000")],
    )


@pytest.fixture(name="mock_hal_organization_solver", autouse=True)
def fixture_mock_hal_organization_solver():
    """
    Mock the hal organization solver with fake organization solver
    """
    with mock.patch.object(HalOrganizationSolver, "solve") as mock_solve:
        mock_solve.side_effect = fake_hal_organization_solver
        yield mock_solve

def fake_openalex_organization_solver(organization_id: str) -> DbOrganization:
    """
    Fake openalex organization solver
    :return: fake Organization
    """
    return DbOrganization(
        source='openalex',
        source_identifier='https://openalex.org/I114027177',
        name='University of North Carolina at Chapel Hill',
        type='funder',
        identifiers=[OrganizationIdentifier(type='openalex',
                                            value='I114027177'),
                     OrganizationIdentifier(type='ror', value='0130frc33')],
    )


@pytest.fixture(name="mock_openalex_organization_solver", autouse=True)
def fixture_mock_openalex_organization_solver():
    """
    Mock the openalex organization solver with fake organization solver
    """
    with mock.patch.object(OpenAlexOrganizationSolver, "solve") as mock_solve:
        mock_solve.side_effect = fake_openalex_organization_solver
        yield mock_solve
