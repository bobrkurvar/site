from contextlib import asynccontextmanager

from fastapi import FastAPI

from domain import InvalidAccessTokenError, InvalidRefreshTokenError
from api import main_router
from api.error_handlers import *
from core.logger import setup_logging
from adapters.redis import RedisProvider
from adapters.http_client import HttpClient
from adapters.dbProvider import DbProvider
from core import conf


setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = await RedisProvider.create(conf.redis_host)
    app.state.image_api = HttpClient(url=f"http://{conf.image_service_url}/")
    app.state.db_provider = DbProvider(conf.db_url)
    try:
        yield
    finally:
        await app.state.db_provider.close()
        await app.state.image_api.close()
        await app.state.redis_provider.close()

log = logging.getLogger(__name__)
app = FastAPI(lifespan=lifespan)
app.include_router(main_router)



@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    log.debug("ТАКОЙ URL НЕ ОБСЛУЖИВАЕТСЯ")
    return RedirectResponse("/", status_code=303)


app.add_exception_handler(UserLoginNotFoundError, user_login_not_found_error_handler)
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(AlreadyExistsError, already_exists_handler)
app.add_exception_handler(ForeignKeyViolationError, foreign_key_handler)
app.add_exception_handler(
    RefreshTokenNotExistsError, invalid_tokens_or_not_exists_handler
)
app.add_exception_handler(
    InvalidRefreshTokenError, invalid_tokens_or_not_exists_handler
)
app.add_exception_handler(InvalidAccessTokenError, invalid_tokens_or_not_exists_handler)
app.add_exception_handler(CredentialsValidateError, invalid_credentials_error_handler)


@app.exception_handler(Exception)
async def global_exc_handler(request: Request, exc):
    if request.url.path.startswith("/admin"):
        return await admin_global_error_handler(request, exc)
    else:
        return await global_error_handler(request, exc)
