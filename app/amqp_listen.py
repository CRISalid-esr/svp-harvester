import asyncio
from loguru import logger
from app.amqp.amqp_interface import AMQPInterface
from app.config import get_app_settings
from starlette.datastructures import State

from app.svp_harvester import SvpHarvester


async def main():
    logger.info("Starting standalone AMQP listener service")

    # Create settings and shared state
    settings = get_app_settings()
    SvpHarvester.register_custom_metadata_schemas()
    app_state = State()
    amqp_interface = AMQPInterface(settings, app_state)

    try:
        await amqp_interface.connect()
        logger.info("Connected to RabbitMQ. Starting listener loop.")
        await amqp_interface.listen()
    except asyncio.CancelledError:
        logger.info("Received cancellation signal, shutting down.")
    except Exception as exc:
        logger.exception(f"Unhandled exception in listener: {exc}")
    finally:
        await amqp_interface.stop_listening()
        logger.info("Graceful shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received — exiting.")
