from fastapi import APIRouter

from .entities import admin_router
from .views import (catalog_router, clients_router, collections_router,
                    home_router, view_admin_router)

presentation_router = APIRouter()

presentation_router.include_router(home_router)
presentation_router.include_router(catalog_router)
presentation_router.include_router(view_admin_router)
presentation_router.include_router(clients_router)
presentation_router.include_router(collections_router)
presentation_router.include_router(admin_router)