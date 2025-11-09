from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import main_router
import logging
from contextlib import asynccontextmanager
from db import get_db_manager
from app.exceptions import *
from db.exceptions import *

app = FastAPI()

app.include_router(main_router)
app.mount("/static", StaticFiles(directory="/static"), name="static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    manager = get_db_manager()
    await manager.close_and_dispose()


log = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

app.include_router(main_router)
app.add_exception_handler(NotFoundError, not_found_in_db_exceptions_handler)
app.add_exception_handler(
    AlreadyExistsError, entity_already_exists_in_db_exceptions_handler
)
app.add_exception_handler(
    CustomForeignKeyViolationError, foreign_key_violation_exceptions_handler
)
app.add_exception_handler(DatabaseError, data_base_exception_handler)

app.add_exception_handler(Exception, global_exception_handler)
