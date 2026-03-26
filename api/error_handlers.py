import logging

from fastapi import Request
from fastapi.responses import RedirectResponse

from domain.exceptions import (AlreadyExistsError, ForeignKeyViolationError,
                               NotFoundError, RefreshTokenNotExistsError, CredentialsValidateError, UserLoginNotFoundError)
from fastapi.templating import Jinja2Templates
from infrastructure.user_agent import CookieManager

log = logging.getLogger(__name__)
templates = Jinja2Templates("templates")

async def not_found_handler(request: Request, exc: NotFoundError):
    log.error("Ошибка поиска в базе данных: %s", exc)
    return RedirectResponse("/admin?err=404", status_code=303)


async def already_exists_handler(request: Request, exc: AlreadyExistsError):
    log.error("Ошибка создания в базе данных: %s", exc)
    return RedirectResponse("/admin?err=409", status_code=303)


async def foreign_key_handler(request: Request, exc: ForeignKeyViolationError):
    log.error("Ошибка создания внешнего ключа: %s", exc)
    return RedirectResponse("/admin?err=409", status_code=303)


async def admin_global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    return RedirectResponse("/admin?err=500", status_code=303)


async def global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    return RedirectResponse("/", status_code=303)


async def invalid_tokens_or_not_exists_handler(request: Request, exc: RefreshTokenNotExistsError):
    log.debug('tokens error: %s', exc)
    response =  templates.TemplateResponse("admin_login.html", {"request": request})
    cookie_manager = CookieManager(request, response)
    cookie_manager.clear_tokens()
    return response


async def user_login_not_found_error_handler(request: Request, exc: UserLoginNotFoundError):
    log.error("user not found: %s", exc)
    response = templates.TemplateResponse("admin_login.html", {"request": request, "error": str(exc)})
    cookie_manager = CookieManager(request, response)
    cookie_manager.clear_tokens()
    return response


async def invalid_credentials_error_handler(request: Request, exc: CredentialsValidateError):
    log.error("invalid credentials: %s", exc)
    response = templates.TemplateResponse("admin_login.html", {"request": request, "error": str(exc)})
    cookie_manager = CookieManager(request, response)
    cookie_manager.clear_tokens()
    return response