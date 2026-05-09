from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .api import auth_routes, admin_routes, booking_routes
from .api.unprotected import unprotected_trips_routes, unprotected_departures_routes
from .api.middleware import RequestIDMiddleware
from .utils.exceptions import DomainException
from .config.logging import setup_logging
from .utils.scheduler import scheduler, run_expire_due_bookings

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_expire_due_bookings()
    scheduler.start()

    yield

    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="Travel Agency Backend",
    version="1.0.0",
    description="""
Backend API for a travel agency booking platform built with FastAPI.

The system supports:
- JWT authentication and role-based authorization
- Trip, departure, and booking management
- Admin and passenger workflows
- Booking lifecycle enforcement
- Structured logging and request tracing
- Integration testing with CI pipeline
""",
    lifespan=lifespan,
)
app.add_middleware(RequestIDMiddleware)
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(unprotected_trips_routes.router)
app.include_router(unprotected_departures_routes.router)
app.include_router(booking_routes.router)


@app.get("/health")
def health_check():
    return {"status": "OK"}


@app.exception_handler(DomainException)
def handle_domain_exception(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )
