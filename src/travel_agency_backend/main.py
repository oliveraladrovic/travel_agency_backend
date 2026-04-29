from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import auth_routes
from .api.middleware import RequestIDMiddleware
from .utils.exceptions import DomainException
from .config.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Travel Agency Backend",
    version="1.0.0",
    description="Backend API for managing travel agency operations.",
)
app.add_middleware(RequestIDMiddleware)
app.include_router(auth_routes.router)


@app.get("/health")
def health_check():
    return {"status": "OK"}


@app.exception_handler(DomainException)
def handle_domain_exception(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )
