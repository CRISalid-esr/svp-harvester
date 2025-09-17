from unittest import mock
import pytest
from app.db.models.organization import Organization as DbOrganization
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.organizations.hal_organization_solver import HalOrganizationSolver
from app.services.organizations.idref_organization_solver import IdrefOrganizationSolver
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
                                            value='https://openalex.org/I114027177'),
                     OrganizationIdentifier(type='ror', value='https://ror.org/0130frc33')],
    )


@pytest.fixture(name="mock_openalex_organization_solver", autouse=True)
def fixture_mock_openalex_organization_solver():
    """
    Mock the openalex organization solver with fake organization solver
    """
    with mock.patch.object(OpenAlexOrganizationSolver, "solve") as mock_solve:
        mock_solve.side_effect = fake_openalex_organization_solver
        yield mock_solve

def fake_idref_organization_with_name_solver() -> DbOrganization:
    """
    Fake idref organization solver
    :return: fake Organization
    """
    return DbOrganization(
        source='scanr',
        source_identifier='scanr_idref_190915757',
        name='Université de Lyon',
        identifiers=[OrganizationIdentifier(type='idref',
                                            value='190915757'),
                     OrganizationIdentifier(type='ror', value='01rk35k63')],
    )

def fake_idref_organization_no_name_solver() -> DbOrganization:
    """
    Fake idref organization solver
    :return: fake Organization
    """
    return DbOrganization(
        source='scanr',
        source_identifier='scanr_idref_190915757',
        name='No ScanR organization name',
        identifiers=[OrganizationIdentifier(type='idref',
                                            value='190915757'),
                     OrganizationIdentifier(type='ror', value='01rk35k63')],
    )

@pytest.fixture(name="mock_idref_organization_solver", autouse=True)
def fixture_mock_idref_organization_solver():
    """
    Autouse fixture that mocks IdrefOrganizationSolver.solve
    with behavior depending on the OrganizationInformations.identifier.
    """
    async def side_effect(organization_information):
        if organization_information.identifier == "scanr_idref_190915757":
            return fake_idref_organization_with_name_solver()
        return fake_idref_organization_no_name_solver()

    with mock.patch.object(IdrefOrganizationSolver, "solve", side_effect=side_effect) as mock_solve:
        yield mock_solve
