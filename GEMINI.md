# Project Overview

This is a FastAPI-based RESTful API that provides astrological calculations. It uses the `kerykeion` library to perform the calculations and returns the results in JSON format. The API is designed to be easily integrated into other projects.

## Building and Running

### Dependencies

The project uses `pipenv` to manage dependencies. To install the dependencies, run:

```bash
pipenv install
```

### Running the Application

To run the application in a development environment, use the following command:

```bash
pipenv run dev
```

This will start the Uvicorn server with hot-reloading enabled.

### Testing

To run the tests, use the following command:

```bash
pipenv run test
```

## Development Conventions

### Code Style

The project uses `black` for code formatting. To format the code, run:

```bash
pipenv run format
```

### Type Checking

The project uses `mypy` for static type checking. To run the type checker, use the following command:

```bash
pipenv run quality
```

### API Schema

The OpenAPI schema is generated using the `dump_schema.py` script. To generate the schema, run:

```bash
pipenv run schema
```
