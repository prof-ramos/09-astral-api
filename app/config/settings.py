"""
    This is part of Astrologer API (C) 2023 Giacomo Battaglia
"""

import pathlib
from logging import getLogger
from os import getenv
from pydantic_settings import BaseSettings
try:
    from tomllib import load as load_toml
except ImportError:
    from tomli import load as load_toml


logger = getLogger(__name__)

ENV_TYPE = getenv("ENV_TYPE", False)
GEONAMES_USERNAME = getenv("GEONAMES_USERNAME", False)

# Open config file
if ENV_TYPE == "production":
    logger.info("Loading production config")
    with open(pathlib.Path(__file__).parent.absolute() / "config.prod.toml", "rb") as config_file:
        config = load_toml(config_file)

elif ENV_TYPE == "test":
    logger.info("Loading test config")
    with open(pathlib.Path(__file__).parent.absolute() / "config.test.toml", "rb") as config_file:
        config = load_toml(config_file)

elif ENV_TYPE == "dev":
    logger.info("Loading development config")
    with open(pathlib.Path(__file__).parent.absolute() / "config.dev.toml", "rb") as config_file:
        config = load_toml(config_file)

else:
    logger.info("No ENV_TYPE set, loading production config")
    with open(pathlib.Path(__file__).parent.absolute() / "config.prod.toml", "rb") as config_file:
        config = load_toml(config_file)


class Settings(BaseSettings):
    # Environment variables
    geonames_username: str = getenv("GEONAMES_USERNAME", "")
    env_type: str | bool = ENV_TYPE

    @property
    def allowed_api_keys(self) -> list[str]:
        keys_str = getenv("ALLOWED_API_KEYS", "")
        return [key.strip() for key in keys_str.split(",") if key.strip()] if keys_str else []

    # Config file
    admin_email: str = config["admin_email"]
    allowed_hosts: list = config["allowed_hosts"]
    allowed_cors_origins: list = config["allowed_cors_origins"]
    debug: bool = config["debug"]
    docs_url: str | None = config["docs_url"]
    redoc_url: str | None = config["redoc_url"]

    # Common settings
    log_level: int = int(config["log_level"])
    LOGGING_CONFIG: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "[%(asctime)s] %(levelprefix)s %(message)s - Module: %(name)s",
                "use_colors": None,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": "[%(asctime)s] %(levelprefix)s %(message)s - Module: %(name)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": log_level, "propagate": False},
            "uvicorn.error": {
                "level": log_level,
            },
            "root": {
                "handlers": ["default"],
                "level": log_level,
            },
            "uvicorn.access": {"handlers": ["access"], "level": log_level, "propagate": False},
        },
    }


settings = Settings()
