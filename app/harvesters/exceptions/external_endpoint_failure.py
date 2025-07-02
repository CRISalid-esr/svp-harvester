import inspect
import traceback
from functools import wraps
from typing import Callable
from venv import logger


class ExternalEndpointFailure(Exception):
    """Exception raised when an external API call fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def handle_external_endpoint_failure(source: str):
    """
    Decorator to handle exceptions raised by external API calls in harvesters.
    :param source:
    :return:
    """

    def decorator(fn: Callable):
        if inspect.isasyncgenfunction(fn):

            @wraps(fn)
            async def asyncgen_wrapper(*args, **kwargs):
                try:
                    async for item in fn(*args, **kwargs):
                        yield item
                except Exception as e:
                    raise ExternalEndpointFailure(f"{source} failure") from e

            return asyncgen_wrapper

        @wraps(fn)
        async def asyncfunc_wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                logger.error("{source} failure: %s", e)
                logger.error(traceback.format_exc())
                raise ExternalEndpointFailure(f"{source} failure") from e

        return asyncfunc_wrapper

    return decorator
