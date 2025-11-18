import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.exceptions.api_handlers import *
from app.exceptions.presentation_handlers import *
from app.presentation import presentation_router
import core.logger
from repo import get_db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    manager = get_db_manager()
    await manager.close_and_dispose()


log = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(api_router)
app.include_router(presentation_router)


@app.exception_handler(NotFoundError)
async def global_not_found_handler(request: Request, exc: NotFoundError):
    if request.url.path.startswith("/admin"):
        return await admin_not_found_handler(request, exc)
    else:
        return not_found_in_db_exceptions_handler(request, exc)


@app.exception_handler(AlreadyExistsError)
async def global_already_exists_handler(request: Request, exc: AlreadyExistsError):
    if request.url.path.startswith("/admin"):
        return await admin_already_exists_handler(request, exc)
    else:
        return entity_already_exists_in_db_exceptions_handler(request, exc)


@app.exception_handler(CustomForeignKeyViolationError)
async def global_foreign_key_handler(
    request: Request, exc: CustomForeignKeyViolationError
):
    if request.url.path.startswith("/admin"):
        return await admin_foreign_key_handler(request, exc)
    else:
        return foreign_key_violation_exceptions_handler(request, exc)


@app.exception_handler(DatabaseError)
async def global_database_handler(request: Request, exc: DatabaseError):
    if request.url.path.startswith("/admin"):
        return await admin_database_error_handler(request, exc)
    else:
        return data_base_exception_handler(request, exc)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if request.url.path.startswith("/admin"):
        return await admin_global_error_handler(request, exc)
    else:
        return global_exception_handler(request, exc)
