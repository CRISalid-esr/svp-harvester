from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from uuid import uuid4


async def log_middleware(request: Request, call_next):
    log_id = str(uuid4())
    with logger.contextualize(log_id=log_id):
        logger.info('Request to access ' +
                    request.url.path)
        try:
            response = await call_next(request)
        except Exception as ex:
            logger.error(f"Request to {request.url.path} failed: {ex}")
            response = JSONResponse(content={"success": False}, status_code=500)
        finally:
            logger.info('Successfully accessed ' + request.url.path)
        return response
