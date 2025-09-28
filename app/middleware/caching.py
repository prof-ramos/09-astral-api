"""
Caching middleware and utilities for Astrologer API
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict
from functools import wraps
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class InMemoryCache:
    """Simple in-memory cache with TTL support"""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = default_ttl

    def _is_expired(self, cache_entry: Dict) -> bool:
        """Check if cache entry has expired"""
        return time.time() > cache_entry["expires_at"]

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if self._is_expired(entry):
            del self.cache[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
            "created_at": time.time()
        }

    def delete(self, key: str) -> None:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]

    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()

    def cleanup_expired(self) -> None:
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry["expires_at"]
        ]
        for key in expired_keys:
            del self.cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "cache_size_bytes": sum(
                len(str(entry["value"])) for entry in self.cache.values()
            ),
            "oldest_entry": min(
                (entry["created_at"] for entry in self.cache.values()),
                default=None
            )
        }

# Global cache instance
cache = InMemoryCache(default_ttl=300)  # 5 minutes

class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for caching GET requests"""

    def __init__(self, app, cache_ttl: int = 300, excluded_paths: list | None = None):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.excluded_paths = excluded_paths or ["/api/v4/health", "/", "/api/v4/now"]

    def _get_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        # Include method, path, query params, and relevant headers
        key_data = {
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params),
            "api_key": request.headers.get("X-API-Key", "")[:8]  # First 8 chars only
        }
        return hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    async def dispatch(self, request: Request, call_next):
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Skip caching for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)

        cache_key = self._get_cache_key(request)
        cached_response = cache.get(cache_key)

        if cached_response:
            # Return cached response
            response = JSONResponse(
                content=cached_response["content"],
                status_code=cached_response["status_code"]
            )
            response.headers["X-Cache"] = "HIT"
            return response

        # Process request
        response = await call_next(request)

        # Cache successful responses
        if response.status_code == 200 and hasattr(response, 'body'):
            try:
                # Get response content
                if hasattr(response, '_body') and response._body:
                    content = json.loads(response._body.decode())
                    cache.set(
                        cache_key,
                        {
                            "content": content,
                            "status_code": response.status_code
                        },
                        ttl=self.cache_ttl
                    )
                    response.headers["X-Cache"] = "MISS"
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Skip caching if response is not JSON
                pass

        return response

def cache_result(ttl: int = 300):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import asyncio
            # Create cache key from function name and arguments
            key_data = {
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(sorted(kwargs.items()))
            }
            cache_key = hashlib.sha256(
                json.dumps(key_data, sort_keys=True).encode()
            ).hexdigest()

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            return result

        return wrapper
    return decorator