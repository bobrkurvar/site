from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from adapters.crud import get_db_manager
from adapters.http_client import get_http_client
from api import main_router
from api.error_handlers import *
from core.logger import setup_logging
from fastapi_csrf_protect import CsrfProtect

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

# csrf = CsrfProtect(
#     secret="твой_очень_длинный_секретный_ключ_!!!",
#     cookie_name="csrftoken",
#     token_key="csrf_token",
#     cookie_secure=True,
#     cookie_samesite="lax",
#     cookie_http_only=False,
# )

app = FastAPI(lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(main_router)


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
