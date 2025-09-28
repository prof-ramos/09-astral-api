"""
    This is part of Astrologer API (C) 2023 Giacomo Battaglia
"""

import logging
import logging.config
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from .routers import main_router
from .config.settings import settings
from .middleware.performance_middleware import PerformanceMiddleware, RequestSizeLimitMiddleware
from .middleware.rate_limiting import RateLimitMiddleware
from .middleware.caching import CacheMiddleware
from .middleware.compression import GzipMiddleware as CustomGzipMiddleware

logging.config.dictConfig(settings.LOGGING_CONFIG)

#------------------------------------------------------------------------------
# Lifespan events (replaces deprecated on_event)
#------------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logging.info("Astrologer API starting up...")

    # Warm up any caches or connections here if needed
    # Could pre-load common chart configurations, etc.

    logging.info("Astrologer API startup complete")

    yield

    # Shutdown
    logging.info("Astrologer API shutting down...")

    # Close any open connections, clear caches, etc.
    from .utils.async_helpers import connection_pool, task_manager
    await connection_pool.close()
    task_manager.cancel_all()

    logging.info("Astrologer API shutdown complete")

# Create FastAPI app with performance optimizations
app = FastAPI(
    debug=settings.debug,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    title="Astrologer API",
    version="4.0.0",
    summary="Astrology Made Easy",
    description="The Astrologer API is a RESTful service providing extensive astrology calculations, designed for seamless integration into projects. It offers a rich set of astrological charts and data, making it an invaluable tool for both developers and astrology enthusiasts.",
    contact={
        "name": "Kerykeion Astrology",
        "url": "https://www.kerykeion.net/",
        "email": settings.admin_email,
    },
    license_info={
        "name": "AGPL-3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html",
    },
    lifespan=lifespan,
)

#------------------------------------------------------------------------------
# Middleware (order matters - first added is outermost)
#------------------------------------------------------------------------------

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Compression middleware (should be early in chain)
app.add_middleware(CustomGzipMiddleware, minimum_size=1024)

# Performance monitoring middleware
app.add_middleware(PerformanceMiddleware, slow_request_threshold=2.0)

# Rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,  # Increased for better UX
    requests_per_hour=2000,   # Increased for better UX
    excluded_paths=["/api/v4/health", "/"]
)

# Request size limiting middleware
app.add_middleware(RequestSizeLimitMiddleware, max_size=2 * 1024 * 1024)  # 2MB

# Caching middleware (should be close to the application)
app.add_middleware(CacheMiddleware, cache_ttl=300)  # 5 minutes


#------------------------------------------------------------------------------
# Health check endpoint for monitoring
#------------------------------------------------------------------------------

@app.get("/health", include_in_schema=False)
async def health_check():
    """Extended health check with performance metrics"""
    from .middleware.caching import cache

    cache_stats = cache.get_stats()

    return {
        "status": "healthy",
        "environment": settings.env_type,
        "cache_stats": cache_stats,
        "performance": {
            "middleware_enabled": True,
            "compression_enabled": True,
            "rate_limiting_enabled": True
        }
    }

#------------------------------------------------------------------------------
# Routers
#------------------------------------------------------------------------------

app.include_router(main_router.router, tags=["Endpoints"])