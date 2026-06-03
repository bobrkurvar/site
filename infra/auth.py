import logging

import jwt

from core import conf
from domain import (AccessTokenDecodedError, AccessTokenExpireError,
                    AccessTokenMalformedError, RefreshTokenDecodedError,
                    RefreshTokenExpireError, RefreshTokenMalformedError)

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
        raise RefreshTokenExpireError
    except jwt.InvalidTokenError as exc:
        log.exception(f"ошибка декодирования refresh токена")
        raise RefreshTokenDecodedError from exc

    if (
        payload.get("type") != "refresh"
        or not payload.get("jti", None)
        or not payload.get("family_id", None)
    ):
        raise RefreshTokenMalformedError
    return payload


def check_access_token(token: str):
    try:
        payload = get_data_from_token(token)
    except jwt.ExpiredSignatureError:
        raise AccessTokenExpireError
    except jwt.InvalidTokenError as exc:
        log.exception(f"ошибка декодирования access токена")
        raise AccessTokenDecodedError from exc

    if payload.get("type") != "access":
        raise AccessTokenMalformedError

    return payload
