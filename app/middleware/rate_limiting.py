"""
Rate limiting middleware for Astrologer API
"""

import time
import asyncio
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
import hashlib

class InMemoryRateLimiter:
    """Simple in-memory rate limiter with sliding window"""

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_windows: Dict[str, list] = defaultdict(list)
        self.hour_windows: Dict[str, list] = defaultdict(list)
        self._last_cleanup = time.time()

    def _cleanup_old_requests(self):
        """Clean up old request timestamps"""
        current_time = time.time()

        # Only cleanup every 60 seconds
        if current_time - self._last_cleanup < 60:
            return

        cutoff_minute = current_time - 60
        cutoff_hour = current_time - 3600

        for client_id in list(self.minute_windows.keys()):
            self.minute_windows[client_id] = [
                req_time for req_time in self.minute_windows[client_id]
                if req_time > cutoff_minute
            ]
            if not self.minute_windows[client_id]:
                del self.minute_windows[client_id]

        for client_id in list(self.hour_windows.keys()):
            self.hour_windows[client_id] = [
                req_time for req_time in self.hour_windows[client_id]
                if req_time > cutoff_hour
            ]
            if not self.hour_windows[client_id]:
                del self.hour_windows[client_id]

        self._last_cleanup = current_time

    def is_allowed(self, client_id: str) -> tuple[bool, Optional[str]]:
        """Check if request is allowed for client"""
        current_time = time.time()
        self._cleanup_old_requests()

        # Check minute window
        minute_window = self.minute_windows[client_id]
        minute_requests = len([req for req in minute_window if req > current_time - 60])

        if minute_requests >= self.requests_per_minute:
            return False, "Rate limit exceeded: too many requests per minute"

        # Check hour window
        hour_window = self.hour_windows[client_id]
        hour_requests = len([req for req in hour_window if req > current_time - 3600])

        if hour_requests >= self.requests_per_hour:
            return False, "Rate limit exceeded: too many requests per hour"

        # Record the request
        self.minute_windows[client_id].append(current_time)
        self.hour_windows[client_id].append(current_time)

        return True, None

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        excluded_paths: list | None = None
    ):
        super().__init__(app)
        self.rate_limiter = InMemoryRateLimiter(requests_per_minute, requests_per_hour)
        self.excluded_paths = excluded_paths or ["/api/v4/health", "/"]

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get API key from headers first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return hashlib.sha256(api_key.encode()).hexdigest()[:16]

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        return client_ip

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        client_id = self._get_client_id(request)
        is_allowed, error_message = self.rate_limiter.is_allowed(client_id)

        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "ERROR",
                    "message": error_message
                },
                headers={
                    "Retry-After": "60"
                }
            )

        return await call_next(request)