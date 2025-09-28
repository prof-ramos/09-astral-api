# Agent Guidelines for Astrologer API

## Commands
- **Test all**: `pipenv run test` or `pytest -v`
- **Test single**: `pytest -k "test_name"` (e.g., `pytest -k "test_birth_chart"`)
- **Test verbose**: `pipenv run test-verbose` or `pytest -vv`
- **Lint/Quality**: `pipenv run quality` or `mypy --ignore-missing-imports .`
- **Format**: `pipenv run format` or `black . --line-length 200`
- **Dev server**: `pipenv run dev` or `uvicorn app.main:app --reload --log-level debug`

## Code Style
- **Python**: 3.11 with type hints
- **Formatting**: Black (200 char lines), 4-space indentation
- **Imports**: External libs first, then local with relative imports (`from ..module`)
- **Naming**: snake_case for functions/vars, PascalCase for classes
- **Error handling**: Try/except with JSONResponse, log exceptions
- **Logging**: `logger = getLogger(__name__)` for all modules
- **Comments**: Docstrings only, no inline comments
- **FastAPI**: Pydantic models for requests/responses, dependency injection for auth