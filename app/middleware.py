from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

logger = logging.getLogger("uvicorn")

class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers = dict(request.headers)
        params = dict(request.query_params)
        logger.info(f"Headers: {headers}")
        logger.info(f"Params: {params}")
        response = await call_next(request)
        return response