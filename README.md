# Travel Agency Backend

Production-style backend API for a travel agency booking platform built with FastAPI.

The application supports:
- JWT authentication and role-based authorization
- Trip, departure, and booking management
- Admin and passenger workflows
- Booking lifecycle management
- Scheduled expiration jobs
- Structured logging and request tracing
- Integration testing with CI pipeline
- Dockerized deployment

## Live API

- Swagger Docs:
  https://travel-agency-backend-k3xm.onrender.com/docs

- ReDoc:
  https://travel-agency-backend-k3xm.onrender.com/redoc

> Note:
> Admin endpoints require authentication and admin privileges.

## Features

### Authentication & Authorization
- JWT Bearer authentication
- Password hashing with Argon2
- Role-based access control (Admin / Passenger)
- Protected admin endpoints
- Ownership validation for user resources

### Trip & Departure Management
- Create, update, activate/deactivate, and delete trips
- Create and manage departures
- Public endpoints for active trips and departures
- Soft delete support for historical data preservation

### Booking System
- Seat reservation system
- Booking lifecycle:
  - RESERVED
  - CONFIRMED
  - CANCELLED
  - EXPIRED
- Booking expiration scheduler
- Capacity validation
- User seat limit validation
- Snapshot pricing system
- Booking summaries grouped by departure

### Background Jobs
- APScheduler-based expiration job
- Automatic expiration of overdue reserved bookings
- Startup cleanup for expired reservations

### Logging
- Structured application logging
- Request tracing using request IDs
- Centralized logging configuration

### Testing & CI
- Pytest integration tests
- Database transaction isolation in tests
- GitHub Actions CI workflow
- Automated test execution on push and pull request events

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Pydantic
- Pydantic Settings
- JWT Authentication
- Argon2
- APScheduler
- Pytest
- Docker
- GitHub Actions

## Project Structure

```
travel_agency_backend/
├── .github/                      # CI workflow
├── alembic/                      # Database migrations
├── src/travel_agency_backend/
    ├── api/                      # API routes
    │   ├── admin/
    │   ├── public/
    │   ├── admin_routes.py
    │   ├── auth_routes.py
    │   ├── booking_routes.py
    │   └── middleware.py
    ├── config/                   # Application configuration
    ├── db/                       # Database setup
    ├── models/                   # SQLAlchemy models
    ├── schemas/                  # Pydantic schemas
    ├── services/                 # Business logic
    ├── utils/                    # Exceptions, security, enums, scheduler
    └── main.py                   # FastAPI application entry point
├── tests/                            # Integration tests
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Running Locally

### 1. Clone Repository

```
git clone https://github.com/oliveraladrovic/travel_agency_backend.git
cd travel_agency_backend
```

### 2. Install Dependencies

```
poetry install
```

### 3. Create PostgreSQL Databases

Create two PostgreSQL databases:

- development database
- test database

Example names:
- `travel_agency_db`
- `travel_agency_test`

### 4. Environment Variables

Copy the example environment file:

```
cp .env.example .env
```

Update `.env` with your local database credentials and secret key.

> Note: You can generate a secure secret key with:

> ```
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

### 5. Run Database Migrations

```
poetry run alembic upgrade head
```

### 6. Run Application

```
poetry run uvicorn travel_agency_backend.main:app --reload
```

## API Documentation

Swagger Docs:
- http://localhost:8000/docs

ReDoc:
- http://localhost:8000/redoc

## Running Tests

```
poetry run pytest -v
```

## Docker

### 1. Create Docker Environment File

```
cp .env.example.docker .env.docker
```

Update `.env.docker`.

### 2. Build Docker Image

```
docker build -t travel-agency-backend .
```

### 3. Run Docker Container

```
docker run --env-file .env.docker -p 8000:8000 travel-agency-backend
```

## CI Pipeline

GitHub Actions workflow automatically runs tests on:
- push events
- pull request events

## API Highlights

### Public Endpoints

- View active trips
- View departures
- User registration
- User login

### Passenger Endpoints

- Create bookings
- Confirm bookings
- Cancel bookings
- Update bookings
- View booking summaries

### Admin Endpoints

- Manage users
- Manage trips
- Manage departures
- View all bookings

## Future Improvements

- Pagination and filtering
- Advanced admin dashboard endpoints
- Email notifications
- Payment integration
- Concurrency-safe seat reservations
- Row-level locking
- Advanced booking lifecycle state machine
- Rate limiting
- Caching
- Async migration
- Kubernetes deployment

## Deployment

The application is deployed on Render using:
- Docker container deployment
- Managed PostgreSQL database
- Environment-based configuration
> Note:
> The application is deployed on Render free tier, so the first request may take a few moments while the service wakes up.

## Author

Oliver Aladrović

GitHub:
https://github.com/oliveraladrovic