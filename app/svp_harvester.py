import asyncio
from copy import deepcopy
import sys

from aiormq import AMQPConnectionError
from fastapi import FastAPI
from loguru import logger
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles

from app.amqp.amqp_interface import AMQPInterface
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.config import get_app_settings
from app.gui.routes.gui import router as gui_router


class SvpHarvester(FastAPI):
    """Main application, routing logic, middlewares and startup/shutdown events"""

    # All middlewares have been disabled due to Faspi/Starlette bug
    # https://stackoverflow.com/questions/70043665/fastapi-unvicorn-request-hanging-during-invocation-of-call-next-path-operation
    # https://stackoverflow.com/questions/68830274/blocked-code-while-using-middleware-and-dependency-injections-to-log-requests-in

    def __init__(self):
        super().__init__()

        self.amqp_interface: AMQPInterface | None = None

        settings = get_app_settings()

        self.include_router(
            api_router, prefix=f"{settings.api_prefix}/{settings.api_version}"
        )

        self.mount(
            "/static", StaticFiles(directory="./app/static", html=True), name="static"
        )

        self.include_router(gui_router)

        # Remove default logger and add custom logger
        logger.remove()
        logger.add(
            settings.logger_sink,
            level=settings.loguru_level,
            **({"rotation": "100 MB"} if settings.logger_sink != sys.stderr else {}),
        )
        self.add_exception_handler(ValidationError, http422_error_handler)
        if settings.amqp_enabled:
            self.add_event_handler("startup", self.open_rabbitmq_connexion)
            self.add_event_handler("shutdown", self.close_rabbitmq_connexion)

    @logger.catch
    async def open_rabbitmq_connexion(self) -> None:  # pragma: no cover
        """Init AMQP connexion at boot time"""
        try:
            logger.info("Enabling RabbitMQ connexion")
            self.amqp_interface = AMQPInterface(get_app_settings())
            asyncio.create_task(self.amqp_interface.listen(), name="amqp_listener")
            logger.info("RabbitMQ connexion has been enabled")
            # raise RuntimeError("test")
        except AMQPConnectionError as error:
            raise RuntimeError(
                "Cannot connect to RabbitMQ, please check your configuration"
            ) from error
        except Exception as error:
            raise RuntimeError(
                "Cannot enable RabbitMQ connexion, please check your configuration"
            ) from error

    async def close_rabbitmq_connexion(self) -> None:  # pragma: no cover
        """Handle last tasks before shutdown"""
        logger.info("Closing RabbitMQ connexion")
        await self.amqp_interface.stop_listening()
        logger.info("RabbitMQ connexion has been closed")
