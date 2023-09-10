import asyncio

from fastapi import FastAPI
from pydantic import ValidationError
from starlette.staticfiles import StaticFiles

from app.api.amqp.amqp_connect import AMQPConnexion
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.config import get_app_settings
from app.gui.routes.gui import router as gui_router


class SvpHarvester(FastAPI):
    def __init__(self):
        super().__init__()

        self.amqp_connexion: AMQPConnexion = None

        settings = get_app_settings()

        self.include_router(
            api_router, prefix=f"{settings.api_prefix}/{settings.api_version}"
        )

        self.mount(
            "/static", StaticFiles(directory="./app/static", html=True), name="static"
        )

        self.include_router(gui_router)

        self.add_exception_handler(ValidationError, http422_error_handler)

        self.add_event_handler("startup", self.open_rabbitmq_connexion)
        self.add_event_handler("shutdown", self.close_rabbitmq_connexion)

    async def open_rabbitmq_connexion(self) -> None:  # pragma: no cover
        """Init AMQP connexion at boot time"""
        print("Enabling RabbitMQ connexion")
        self.amqp_connexion = AMQPConnexion(get_app_settings())
        asyncio.create_task(self.amqp_connexion.listen(), name="amqp_listener")

    async def close_rabbitmq_connexion(self) -> None:  # pragma: no cover
        """Handle last tasks before shutdown"""
        print("Shutting down RabbitMQ connexion")
        await self.amqp_connexion.stop_listening()
        print("RabbitMQ connexion has been closed")
