""" Main application and routing logic for API """
import asyncio

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles
from loguru import logger
from uuid import uuid4

from app.api.amqp.amqp_connect import AMQPConnexion
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.config import get_app_settings
from app.gui.routes.gui import router as gui_router


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

    application.mount(
        "/static", StaticFiles(directory="./app/static", html=True), name="static"
    )

    application.include_router(gui_router)

    application.add_exception_handler(ValidationError, http422_error_handler)

    logger.add("log/info.log", format="Log: [{extra[log_id]}:{time} - {level} - {message}",
               level="INFO", enqueue=True)

    return application


app = get_application()


@app.on_event("startup")
async def startup() -> None:  # pragma: no cover
    """Init AMQP connexion at boot time"""
    amqp_connexion = AMQPConnexion(get_app_settings())
    asyncio.create_task(amqp_connexion.listen(), name="amqp_listener")


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        logger.info('Request to access ' +
                    request.url.path)
        try:
            response = await call_next(request)
        except Exception as ex:
            logger.error("Request to " + request.url.path + " failed: {ex}")
            response = JSONResponse(content=
                                    {"success": False}, status_code=500)
        finally:
            logger.info('Successfully accessed ' + request.url.path)
        return response


if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(app, host="0.0.0.0", port=8000)
