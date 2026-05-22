"""Starlette middleware components mounted on the FastAPI app."""

import logging
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("uvicorn")


class LogRequestMiddleware(BaseHTTPMiddleware):
    """Log inbound request headers and query params before delegating to the handler."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Log request metadata and return whatever the downstream handler produces."""
        headers = dict(request.headers)
        params = dict(request.query_params)
        logger.info(f"Headers: {headers}")
        logger.info(f"Params: {params}")
        response = await call_next(request)
        return response
