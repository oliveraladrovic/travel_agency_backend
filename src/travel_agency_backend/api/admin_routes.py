from fastapi import APIRouter, Depends

from ..utils.security import require_admin
from .admin import admin_trips_routes

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])

router.include_router(admin_trips_routes.router)
