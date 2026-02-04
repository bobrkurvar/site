import logging

from fastapi import Request
from fastapi.responses import RedirectResponse
from core import logger

from domain.exceptions import (AlreadyExistsError,
                               ForeignKeyViolationError,
                               NotFoundError)

log = logging.getLogger(__name__)


async def not_found_handler(request: Request, exc: NotFoundError):
    log.error("Ошибка поиска в базе данных: %s", exc)
    return RedirectResponse("/admin?err=404", status_code=303)


async def already_exists_handler(request: Request, exc: AlreadyExistsError):
    log.error("Ошибка создания в базе данных: %s", exc)
    return RedirectResponse("/admin?err=409", status_code=303)


async def foreign_key_handler(
    request: Request, exc: ForeignKeyViolationError
):
    log.error("Ошибка создания внешнего ключа: %s", exc)
    return RedirectResponse("/admin?err=409", status_code=303)



async def global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    return RedirectResponse("/admin?err=500", status_code=303)


