import logging

from fastapi import Request, status
from fastapi.responses import RedirectResponse

from repo.exceptions import (AlreadyExistsError,
                             CustomForeignKeyViolationError, DatabaseError,
                             NotFoundError)

log = logging.getLogger(__name__)


async def admin_not_found_handler(request: Request, exc: NotFoundError):
    log.error("Ошибка поиска в базе данных: %s", exc)
    return RedirectResponse("/admin?err=404", status_code=303)


async def admin_already_exists_handler(request: Request, exc: AlreadyExistsError):
    log.error("Ошибка создания в базе данных: %s", exc)
    return RedirectResponse("/admin?err=409", status_code=303)


async def admin_foreign_key_handler(
    request: Request, exc: CustomForeignKeyViolationError
):
    log.error("Ошибка создания внешнего ключа: %s", exc)
    return RedirectResponse("/admin?err=409", status_code=303)


async def admin_database_error_handler(request: Request, exc: DatabaseError):
    log.error("Ошибка базы данных: %s", exc)
    return RedirectResponse("/admin?err=500", status_code=303)


async def admin_global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    return RedirectResponse("/admin?err=500", status_code=303)


async def presentation_global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    return RedirectResponse("/", status_code=303)
