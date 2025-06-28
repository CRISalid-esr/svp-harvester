import asyncio
import sys

import uvloop
from loguru import logger

from app.amqp.amqp_interface import AMQPInterface
from app.config import get_app_settings
from app.http.aio_http_client_manager import AioHttpClientManager
from app.models.custom_medatata import register_custom_metadata_schemas


async def main():
    """
    Main function to run the standalone AMQP listener service.
    :return:
    """
    settings = get_app_settings()
    await _configure_logger(settings)
    register_custom_metadata_schemas()
    await _listen_to_rabbitmq(settings)


async def _listen_to_rabbitmq(settings):
    amqp_interface = AMQPInterface(settings)
    try:
        await amqp_interface.connect()
        logger.info("Connected to RabbitMQ. Starting listener loop.")
        await amqp_interface.listen()
    except asyncio.CancelledError:
        logger.info("Received cancellation signal, shutting down.")
    except Exception as exc:  # pylint: disable=broad-exception-caught
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


async def _configure_logger(settings):
    logger.remove()
    logger.add(
        settings.logger_sink,
        level=settings.loguru_level,
        **({"rotation": "100 MB"} if settings.logger_sink != sys.stderr else {}),
    )
    logger.info("Starting standalone AMQP listener service")


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received — exiting.")
