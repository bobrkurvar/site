from fastapi import APIRouter

from .tile import router as manager_router

api_router = APIRouter(tags=["api"], prefix="/api")

api_router.include_router(manager_router)
