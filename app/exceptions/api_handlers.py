import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from repo.exceptions import (
    AlreadyExistsError,
    CustomForeignKeyViolationError,
    DatabaseError,
    NotFoundError,
)

log = logging.getLogger(__name__)


def not_found_in_db_exceptions_handler(request: Request, exc: NotFoundError):
    log.error("Ошибка поиска в базе данных: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"code": status.HTTP_404_NOT_FOUND, "detail": str(exc)},
    )


def entity_already_exists_in_db_exceptions_handler(
    request: Request, exc: AlreadyExistsError
):
    log.error("Ошибка создания в базе данных: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"code": status.HTTP_409_CONFLICT, "detail": str(exc)},
    )


def foreign_key_violation_exceptions_handler(
    request: Request, exc: CustomForeignKeyViolationError
):
    log.error("Ошибка создания внешнего ключа: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"code": status.HTTP_409_CONFLICT, "detail": str(exc)},
    )


def data_base_exception_handler(request: Request, exc: DatabaseError):
    log.error("Ошибка базы данных: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "detail": str(exc)},
    )


def global_exception_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "detail": str(exc) + " " + exc.__class__.__name__,
        },
    )
