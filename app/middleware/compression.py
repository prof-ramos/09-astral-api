"""
Compression middleware for Astrologer API
"""

import gzip
import io
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class GzipMiddleware(BaseHTTPMiddleware):
    """Gzip compression middleware for responses"""

    def __init__(self, app, minimum_size: int = 1024, compression_level: int = 6):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level

    def _should_compress(self, request: Request, response: Response) -> bool:
        """Determine if response should be compressed"""
        # Check if client supports gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return False

        # Check response size
        if not hasattr(response, 'body') or not response.body:
            return False

        content_length = len(response.body) if response.body else 0
        if content_length < self.minimum_size:
            return False

        # Check content type
        content_type = response.headers.get("content-type", "")
        compressible_types = [
            "application/json",
            "text/",
            "application/javascript",
            "application/xml",
            "image/svg+xml"
        ]

        if not any(ct in content_type for ct in compressible_types):
            return False

        # Don't compress if already compressed
        if response.headers.get("content-encoding"):
            return False

        return True

    def _compress_response(self, response_body: bytes) -> bytes:
        """Compress response body using gzip"""
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb", compresslevel=self.compression_level) as gz_file:
            gz_file.write(response_body)
        return buffer.getvalue()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        if self._should_compress(request, response):
            try:
                # Get response body
                response_body = response.body

                # Compress the body
                compressed_body = self._compress_response(response_body)

                # Create new response with compressed body
                response.body = compressed_body
                response.headers["content-encoding"] = "gzip"
                response.headers["content-length"] = str(len(compressed_body))

                # Add vary header
                vary_header = response.headers.get("vary", "")
                if "accept-encoding" not in vary_header.lower():
                    if vary_header:
                        response.headers["vary"] = f"{vary_header}, Accept-Encoding"
                    else:
                        response.headers["vary"] = "Accept-Encoding"

            except Exception:
                # If compression fails, return original response
                pass

        return response