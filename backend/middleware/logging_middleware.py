"""
logging_middleware.py
Request/response logging middleware — logs method, path, status, and latency
for every request to aid observability and debugging.
"""

import logging
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        latency_ms = int((time.time() - start) * 1000)

        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} [{latency_ms}ms]"
        )
        response.headers["X-Response-Time-Ms"] = str(latency_ms)
        return response
