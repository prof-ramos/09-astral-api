"""
API Key security module for Astrologer API independent authentication
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config.settings import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

def validate_api_key(api_key: str = Security(API_KEY_HEADER)) -> bool:
    """Valida a chave de API fornecida."""
    if not api_key or api_key not in settings.allowed_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return True