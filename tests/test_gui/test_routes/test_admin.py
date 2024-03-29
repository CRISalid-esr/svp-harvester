"""Test the references API."""
import pytest
from fastapi.testclient import TestClient

from app.config import get_app_settings


def test_admin_page(test_client: TestClient):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.get("/admin")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "page",
    [
        "",
        "/retrieve",
        "/history",
    ],
)
def test_admin_page_contains_api_info_in_hidden_inputs(
    test_client: TestClient, page: str
):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.get(f"/admin{page}")
    assert response.status_code == 200
    assert (
        '<input type="hidden" id="api-host" value="http://localhost:8000">'
        in response.text
    )
    assert '<input type="hidden" id="api-path" value="/api/v1">' in response.text


@pytest.mark.parametrize(
    "page",
    [
        "",
        "/retrieve",
        "/history",
    ],
)
def test_admin_pages_contain_institution_name_in_title(
    test_client: TestClient, page: str
):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.get(f"/admin{page}")
    assert response.status_code == 200
    institution_name = get_app_settings().institution_name
    assert institution_name in response.text
