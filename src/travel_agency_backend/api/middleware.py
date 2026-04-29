from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from collections.abc import Callable
from starlette.responses import Response
import uuid

from ..config.logging import request_id_context


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        token = request_id_context.set(request_id)

        try:
            response = await call_next(request)
        finally:
            request_id_context.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response
