import asyncio

from fastapi import FastAPI
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles
from loguru import logger

from app.api.amqp.amqp_interface import AMQPInterface
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.config import get_app_settings
from app.gui.routes.gui import router as gui_router
from app.logging.logging_middleware import log_middleware


class SvpHarvester(FastAPI):
    """Main application, routing logic, middlewares and startup/shutdown events"""

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

        logger.add(
            "logs/info_{time}.log",
            format="Log : [{extra[log_id]}]:{time} - {level} - {message}",
            level=settings.loguru_level,
            enqueue=True,
            rotation="1 week",
            compression="zip",
        )

        self.add_exception_handler(ValidationError, http422_error_handler)
        self.middleware("http")(log_middleware)
        self.add_event_handler("startup", self.open_rabbitmq_connexion)
        self.add_event_handler("shutdown", self.close_rabbitmq_connexion)

    async def open_rabbitmq_connexion(self) -> None:  # pragma: no cover
        """Init AMQP connexion at boot time"""
        print("Enabling RabbitMQ connexion")
        self.amqp_interface = AMQPInterface(get_app_settings())
        asyncio.create_task(self.amqp_interface.listen(), name="amqp_listener")

    async def close_rabbitmq_connexion(self) -> None:  # pragma: no cover
        """Handle last tasks before shutdown"""
        print("Shutting down RabbitMQ connexion")
        await self.amqp_interface.stop_listening()
        print("RabbitMQ connexion has been closed")