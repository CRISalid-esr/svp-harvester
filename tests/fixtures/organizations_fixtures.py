from unittest import mock
import pytest
from app.db.models.organization import Organization as DbOrganzation
from app.db.models.organization_identifier import OrganizationIdentifier
from app.services.organizations.hal_organization_solver import HalOrganizationSolver


def fake_hal_organization_solver(organization_id: str) -> DbOrganzation:
    """
    Fake hal organization solver
    :return: fake Organization
    """
    return DbOrganzation(
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
