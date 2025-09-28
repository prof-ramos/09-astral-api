"""
Performance monitoring middleware for Astrologer API
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track API performance metrics"""

    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)

        # Log slow requests
        if process_time > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} - "
                f"Time: {process_time:.3f}s - Status: {response.status_code}"
            )

        # Log all requests with timing
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Time: {process_time:.3f}s - Status: {response.status_code}"
        )

        return response

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request payload size"""

    def __init__(self, app, max_size: int = 1024 * 1024):  # 1MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_length = request.headers.get("content-length")

        if content_length and int(content_length) > self.max_size:
            return JSONResponse(
                status_code=413,
                content={
                    "status": "ERROR",
                    "message": f"Request payload too large. Maximum size: {self.max_size} bytes"
                }
            )

        return await call_next(request)