from fastapi import status, APIRouter
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


router = APIRouter()


@router.get(
    "/",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def get_health(_request: Request, _response: Response) -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on.

    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")
