""" Main application and routing logic for API """
import uvicorn
from fastapi import FastAPI
from pydantic import ValidationError

from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.config import get_app_settings


def get_application() -> FastAPI:
    """
    Get the FastAPI application
    :return:
    """
    application = FastAPI()

    settings = get_app_settings()

    application.include_router(
        api_router, prefix=f"{settings.api_prefix}/{settings.api_version}"
    )

    application.add_exception_handler(ValidationError, http422_error_handler)

    return application


app = get_application()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
