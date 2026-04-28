from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api import auth_routes
from .utils.exceptions import DomainException

app = FastAPI(
    title="Travel Agency Backend",
    version="1.0.0",
    description="Backend API for managing travel agency operations.",
)


@app.get("/health")
def health_check():
    return {"status": "OK"}


app.include_router(auth_routes.router)


@app.exception_handler(DomainException)
def handle_domain_exception(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )
