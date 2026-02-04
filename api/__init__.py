from .entities import admin_router
from .views import view_router
from fastapi import APIRouter

main_router = APIRouter()
main_router.include_router(admin_router)
main_router.include_router(view_router)