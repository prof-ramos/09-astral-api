# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Astrologer API** - a FastAPI-based RESTful service providing extensive astrology calculations via the Kerykeion library. The API generates birth charts, synastry charts, transit charts, and composite charts with SVG output, serving both developers and astrology enthusiasts through RapidAPI.

## Project Architecture

### Core Framework Stack
- **FastAPI** - Web framework with automatic OpenAPI documentation
- **Pydantic** - Data validation and serialization for request/response models
- **Kerykeion** - Core astrology calculation library for charts and aspects
- **Uvicorn** - ASGI server for production deployment
- **Starlette** - ASGI toolkit (middleware, routing)

### Application Structure
```
app/
├── main.py              # FastAPI application entry point with middleware setup
├── routers/             # API endpoints organization
│   └── main_router.py   # All astrology API endpoints (/api/v4/*)
├── types/               # Pydantic models
│   ├── request_models.py    # Input validation models for all endpoints
│   └── response_models.py   # Output models for API responses
├── config/              # Configuration management
│   ├── settings.py      # Environment-based configuration loader
│   ├── config.dev.toml  # Development environment settings
│   └── config.prod.toml # Production environment settings
├── middleware/          # Custom middleware
│   └── secret_key_checker_middleware.py  # API key validation for production
└── utils/               # Helper functions
    ├── get_time_from_google.py  # UTC time fetching
    ├── get_ntp_time.py         # Network time protocol
    └── write_request_to_log.py # Request logging utilities
```

### Configuration System
The application uses environment-based configuration with TOML files:
- `ENV_TYPE` environment variable determines which config to load (dev/test/production)
- Settings include debug flags, CORS origins, logging levels, and API documentation URLs
- Authentication via `ALLOWED_API_KEYS` environment variable (FastAPI dependency injection)

### API Endpoint Architecture
All endpoints follow the pattern `/api/v4/{endpoint}` and handle:
- **Chart Generation**: SVG birth/synastry/transit/composite charts with themes and languages
- **Data Only**: Astrological data without chart generation (*-data endpoints)
- **Aspects**: Planetary aspect calculations between subjects
- **Relationship Scoring**: Compatibility analysis using Ciro Discepolo method

### Key Astrology Features
- **Zodiac Systems**: Tropical (default) and Sidereal with multiple ayanamsha modes
- **House Systems**: 20+ house systems (Placidus default)
- **Coordinate Systems**: Manual lat/lng/timezone or automatic via GeoNames API
- **Chart Themes**: classic, light, dark, dark-high-contrast
- **Multi-language**: EN, FR, PT, ES, TR, RU, IT, CN, DE, HI
- **Active Points/Aspects**: Customizable celestial bodies and aspect calculations

## Development Commands

### Environment Management (Pipenv)
- `pipenv install` - Install dependencies from Pipfile
- `pipenv install --dev` - Install dev dependencies
- `pipenv shell` - Activate virtual environment
- `pipenv run <command>` - Run command in virtual environment

### Development Scripts (from Pipfile)
- `pipenv run dev` - Start development server with auto-reload (uvicorn app.main:app --reload --log-level debug)
- `pipenv run test` - Run pytest with verbose output
- `pipenv run test-verbose` - Run pytest with extra verbose output
- `pipenv run quality` - Run MyPy type checking (ignoring missing imports)
- `pipenv run format` - Format code with Black (200 char line length)
- `pipenv run schema` - Generate OpenAPI schema using dump_schema.py

### Direct Commands
- `uvicorn app.main:app --reload` - Start development server
- `uvicorn app.main:app --host=0.0.0.0 --port=5000` - Production server (Heroku style)

### Testing Commands
- `pipenv run test` - Run pytest with verbose output
- `pipenv run test-verbose` - Run pytest with extra verbose output
- `pytest tests/` - Run all tests in tests directory
- `pytest -x` - Stop on first failure
- `pytest -k "test_name"` - Run specific test by name

### Code Quality Commands
- `pipenv run format` - Format code with Black (200 char line length)
- `pipenv run quality` - Run MyPy type checking
- `black . --line-length 200` - Format code directly
- `mypy --ignore-missing-imports .` - Type check directly

### Environment Variables
Set these for different environments:
- `ENV_TYPE` - "dev", "test", or "production" (determines config file)
- `ALLOWED_API_KEYS` - Comma-separated list of API keys for authentication (required for production)
- `GEONAMES_USERNAME` - GeoNames API username for coordinate lookup (optional but recommended)

## Technology Stack

### Core Dependencies (from Pipfile)
- **Python 3.11** - Runtime environment
- **FastAPI** - Modern async web framework with automatic docs
- **Pydantic** + **pydantic-settings** - Data validation and settings management
- **Uvicorn** - ASGI server for FastAPI
- **Starlette** - ASGI toolkit (FastAPI foundation)
- **Kerykeion** - Core astrology calculations library
- **PyTZ** + **types-pytz** - Timezone handling
- **Scour** - SVG optimization
- **typing-extensions** - Enhanced type hints

### Development Tools
- **pytest** - Testing framework
- **mypy** - Static type checking
- **black** - Code formatting (200 char line length)
- **httpx** - HTTP client for testing
- **types-requests** - Type stubs for requests

### Deployment
- **Heroku** - Cloud platform (via Procfile)
- **Pipenv** - Dependency management and virtual environments

## Key Development Patterns

### Request/Response Model Architecture
- **AbstractBaseSubjectModel** - Base validation for astrological subjects (birth data)
- **SubjectModel** - Extended subject with zodiac/house system options
- **Request Models** - Pydantic models for each endpoint (BirthChartRequestModel, etc.)
- **Response Models** - Structured API responses with status, data, and optional SVG charts

### Error Handling Pattern
All endpoints follow consistent error handling:
```python
try:
    # Astrological calculations
    return JSONResponse(content={"status": "OK", ...})
except Exception as e:
    if "data found for this city" in str(e):
        # GeoNames API error
        return JSONResponse(content={"status": "ERROR", "message": GEONAMES_ERROR_MESSAGE})
    # Generic server error
    return InternalServerErrorJsonResponse
```

### Configuration Pattern
- Environment-based config loading via `ENV_TYPE`
- TOML files for different environments (dev/test/prod)
- Pydantic BaseSettings for type-safe configuration
- Environment variables override config files

### Authentication Architecture
- **API Key Security** - FastAPI dependency injection for route protection
- **Public Router** - Health check and status endpoints (no authentication)
- **Protected Router** - All API endpoints require `X-API-Key` header
- Environment-based API key validation via `ALLOWED_API_KEYS`

## API Development Guidelines

### Endpoint Implementation Pattern
Follow this pattern when adding new endpoints:
```python
@router.post("/api/v4/new-endpoint", response_model=ResponseModel)
async def new_endpoint(request_body: RequestModel, request: Request):
    write_request_to_log(20, request, "Description")

    try:
        # Create AstrologicalSubject(s) from request data
        subject = AstrologicalSubject(
            name=request_body.subject.name,
            # ... map all fields from SubjectModel
            geonames_username=request_body.subject.geonames_username,
            online=True if request_body.subject.geonames_username else False,
        )

        # Perform calculations using Kerykeion
        # Return structured response
        return JSONResponse(content={"status": "OK", "data": result})

    except Exception as e:
        if "data found for this city" in str(e):
            return JSONResponse(content={"status": "ERROR", "message": GEONAMES_ERROR_MESSAGE})
        return InternalServerErrorJsonResponse
```

### Adding New Request/Response Models
1. **Request Models** (`app/types/request_models.py`):
   - Inherit from `AbstractBaseSubjectModel` for astrology data
   - Add endpoint-specific fields (theme, language, etc.)
   - Include proper Pydantic validation

2. **Response Models** (`app/types/response_models.py`):
   - Follow consistent structure: status, data, optional chart/aspects
   - Use proper type hints for all fields

### Configuration Changes
- Add new settings to appropriate TOML files (`config.dev.toml`, `config.prod.toml`)
- Update `Settings` class in `app/config/settings.py`
- Environment variables override TOML values

### Testing Approach
- Test files should mirror the `app/` structure
- Use `httpx` for API endpoint testing
- Mock external dependencies (GeoNames API)
- Test both success and error scenarios