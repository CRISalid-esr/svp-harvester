import asyncio

from loguru import logger
from starlette.datastructures import State

from app.amqp.amqp_interface import AMQPInterface
from app.config import get_app_settings
from app.db.models.reference import Reference
from app.harvesters.hal.hal_custom_metadata_schema import HalCustomMetadataSchema
from app.http.aio_http_client_manager import AioHttpClientManager


async def main():
    """
    Main function to run the standalone AMQP listener service.
    :return:
    """
    logger.info("Starting standalone AMQP listener service")

    settings = get_app_settings()
    Reference.register_custom_metadata_schema("HAL", HalCustomMetadataSchema)
    app_state = State()
    amqp_interface = AMQPInterface(settings, app_state)

    try:
        await amqp_interface.connect()
        logger.info("Connected to RabbitMQ. Starting listener loop.")
        await amqp_interface.listen()
    except asyncio.CancelledError:
        logger.info("Received cancellation signal, shutting down.")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # here
        logger.exception(f"Unhandled exception in listener: {exc}")
    finally:
        await AioHttpClientManager.close()
        try:
            await amqp_interface.stop_listening()
        except asyncio.TimeoutError:
            logger.warning("Timeout while stopping listener")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.exception(f"Error during shutdown: {e}")
        else:
            logger.info("Graceful shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received — exiting.")
