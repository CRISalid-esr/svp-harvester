import asyncio

import uvloop
from loguru import logger

from app.amqp.amqp_interface import AMQPInterface
from app.config import get_app_settings
from app.configure_logger import _configure_logger
from app.http.aio_http_client_manager import AioHttpClientManager
from app.models.custom_medatata import register_custom_metadata_schemas


async def main():
    """
    Main function to run the standalone AMQP listener service.
    :return:
    """
    _configure_logger()
    register_custom_metadata_schemas()
    await _listen_to_rabbitmq()


async def _listen_to_rabbitmq(settings):
    settings = get_app_settings()
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


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received — exiting.")
