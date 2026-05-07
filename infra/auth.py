import logging
from core import conf
from domain import (
    AccessTokenNotExistsError,
    RefreshTokenNotExistsError,
    InvalidRefreshTokenError,
    InvalidAccessTokenError,
)
import jwt


log = logging.getLogger(__name__)


secret_key = conf.secret_key
algorithm = conf.algorithm


def get_data_from_token(encoded: str):
    return jwt.decode(encoded, secret_key, algorithms=[algorithm])


def data_encode_to_jwt(decoded: dict):
    return jwt.encode(decoded, secret_key, algorithm)


def check_refresh_token(token: str):
    try:
        payload = get_data_from_token(token)
    except jwt.ExpiredSignatureError:
        raise RefreshTokenNotExistsError
    except jwt.InvalidTokenError as exc:
        log.exception(f"ошибка декодирования refresh токена")
        raise InvalidRefreshTokenError from exc

    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError
    return payload


def check_access_token(token: str):
    try:
        payload = get_data_from_token(token)
    except jwt.ExpiredSignatureError:
        raise AccessTokenNotExistsError
    except jwt.InvalidTokenError as exc:
        log.exception(f"ошибка декодирования access токена")
        raise InvalidAccessTokenError from exc

    if payload.get("type") != "access":
        raise InvalidAccessTokenError

    return payload
