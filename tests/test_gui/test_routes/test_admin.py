"""Test the references API."""
import pytest
from fastapi.testclient import TestClient


def test_admin_page(test_client: TestClient):
    """Test the create_retrieval_sync endpoint."""
    response = test_client.get("/admin")
    assert response.status_code == 200


@pytest.mark.current
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
