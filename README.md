# Travel Agency Backend
Backend API for managing a travel agency booking system built with FastAPI, SQLAlchemy and PostgreSQL.

This project is focused on real-world backend architecture and business rules rather than simple CRUD operations.

## Features
- User registration
- Password hashing with Argon2
- PostgreSQL database
- SQLAlchemy ORM
- Alembic migrations
- Structured service layer architecture
- Domain exception handling
- Request ID logging
- Automated testing with pytest
- GitHub Actions CI

## Tech Stack
- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Pydantic
- Pytest
- GitHub Actions

## Project Structure
```
travel_agency_backend/
├── .github/
├── alembic/
├── src/travel_agency_backend/
        ├── api/
        ├── config/
        ├── db/
        ├── models/
        ├── schemas/
        ├── services/
        ├── utils/
        └── main.py # main entrypoint
├── tests/
├── .env
├── .gitignore
├── poetry.lock
└── pyproject.toml
```

## Setup
### Clone repository
```
git clone https://github.com/oliveraladrovic/travel_agency_backend.git
cd travel-agency-backend
```

### Install dependencies
```
poetry install
```

### Create .env file
```
cp .env.example .env
```
Create PostgreSQL databases and update the connection strings and JWT secret_key in `.env`.

You can generate secure secret_key using:
```
python -c "import secrets; print(secrets.token_hex(32))"
```

## Run migrations
```
poetry run alembic upgrade head
```

## Start development server
```
poetry run uvicorn travel_agency_backend.main:app --reload
```

## Run tests
```
poetry run pytest -v
```

## API Documentation
After starting the server:

- Swagger UI:
http://localhost:8000/docs
- ReDoc:
http://localhost:8000/redoc

## Current Status
Implemented:
- database models
- migrations
- registration flow
- logging foundation
- testing infrastructure
- CI pipeline

In progress:
- JWT authentication
- authorization
- booking system
- admin features

## Design Goals
This project aims to simulate a production-style backend system with:
- layered architecture
- domain-driven business rules
- transactional integrity
- concurrency-safe booking logic
- maintainable and testable codebase