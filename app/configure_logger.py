import sys

from loguru import logger

from app.config import get_app_settings


def configure_logger():
    """
    Configure the logger
    :return:
    """
    settings = get_app_settings()
    logger.remove()
    logger.add(
        settings.logger_sink,
        level=settings.loguru_level,
        **({"rotation": "100 MB"} if settings.logger_sink != sys.stderr else {}),
    )
    logger.info("Starting standalone AMQP listener service")
