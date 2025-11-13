from fastapi import APIRouter
from .manage import router as manager_router

api_router = APIRouter(tags=['api'])

api_router.include_router(manager_router)