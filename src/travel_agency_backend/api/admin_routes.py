from fastapi import APIRouter, Depends

from ..utils.security import require_admin
from .admin import (
    admin_trips_routes,
    admin_departures_routes,
    admin_bookings_routes,
    admin_users_routes,
)

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])

router.include_router(admin_trips_routes.router)
router.include_router(admin_departures_routes.router)
router.include_router(admin_bookings_routes.router)
router.include_router(admin_users_routes.router)
