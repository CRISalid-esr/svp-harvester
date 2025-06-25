import asyncio
from functools import wraps

import aiohttp


class DereferencingError(Exception):
    """
    Exception raised when a concept solver fails to dereference a concept
    URI due to an external endpoint failure.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)


def handle_concept_dereferencing_error(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiohttp.ClientResponseError as e:
            raise DereferencingError(
                f"HTTP error {e.status} while dereferencing "
                f"{kwargs.get('concept_informations') or args[1]}"
            ) from e
        except aiohttp.ClientConnectionError as e:
            raise DereferencingError(
                "Connection error while accessing "
                f"{kwargs.get('concept_informations') or args[1]}"
            ) from e
        except aiohttp.ClientPayloadError as e:
            raise DereferencingError(
                "Invalid response payload from "
                f"{kwargs.get('concept_informations') or args[1]}"
            ) from e
        except asyncio.TimeoutError as e:
            raise DereferencingError(
                "Timeout while trying to dereference "
                f"{kwargs.get('concept_informations') or args[1]}"
            ) from e
        except aiohttp.ClientError as e:
            raise DereferencingError(
                "Unexpected aiohttp error while accessing "
                f"{kwargs.get('concept_informations') or args[1]}: {str(e)}"
            ) from e
        except Exception as e:
            raise DereferencingError(
                f"Unexpected error while dereferencing "
                f"{kwargs.get('concept_informations') or args[1]}: {str(e)}"
            ) from e

    return wrapper


def handle_organization_dereferencing_error(platform: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            org_info = kwargs.get("organization_information") or args[1]
            try:
                return await func(*args, **kwargs)
            except aiohttp.ClientResponseError as e:
                raise DereferencingError(
                    f"HTTP error {e.status} while dereferencing organization identifier "
                    f"from {platform}: {org_info}"
                ) from e
            except aiohttp.ClientConnectionError as e:
                raise DereferencingError(
                    "Connection error while accessing organization identifier "
                    f"from {platform}: {org_info}"
                ) from e
            except aiohttp.ClientPayloadError as e:
                raise DereferencingError(
                    "Invalid response payload from organization identifier "
                    f"from {platform}: {org_info}"
                ) from e
            except asyncio.TimeoutError as e:
                raise DereferencingError(
                    "Timeout while dereferencing organization identifier "
                    f"from {platform}: {org_info}"
                ) from e
            except aiohttp.ClientError as e:
                raise DereferencingError(
                    "Unexpected aiohttp error while accessing organization identifier "
                    f"from {platform}: {org_info}: {str(e)}"
                ) from e
            except Exception as e:
                raise DereferencingError(
                    "Unexpected error while dereferencing organization identifier "
                    f"from {platform}: {org_info}: {str(e)}"
                ) from e

        return wrapper

    return decorator
