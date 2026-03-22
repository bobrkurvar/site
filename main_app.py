from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_csrf_protect.flexible import CsrfProtect
from pydantic_settings import BaseSettings

from infrastructure.crud import get_db_manager
from infrastructure.http_client import get_http_client
from api import main_router
from api.error_handlers import *
from core.logger import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = get_http_client()
    http_client.connect()
    manager = get_db_manager()
    manager.connect()
    yield
    await manager.close_and_dispose()
    await http_client.close()


log = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(main_router)


class CsrfSettings(BaseSettings):
    secret_key: str = "ваш-секретный-ключ-обязательно-измените"
    cookie_samesite: str = "strict"
    cookie_secure: bool = True
    cookie_httponly: bool = True
    max_age: int = 7200
    refresh_age: int = 1800


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return RedirectResponse("/", status_code=303)


app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(AlreadyExistsError, already_exists_handler)
app.add_exception_handler(ForeignKeyViolationError, foreign_key_handler)


@app.exception_handler(Exception)
async def global_exc_handler(request: Request, exc):
    if request.url.path.startswith("/admin"):
        return await admin_global_error_handler(request, exc)
    else:
        return await global_error_handler(request, exc)
