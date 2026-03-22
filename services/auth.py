import logging
from datetime import datetime, timedelta, timezone

import jwt

from core import conf
from domain import RefreshTokenNotExistsError
from domain.exceptions import *
from domain.user import Admin
from services.security import verify

log = logging.getLogger(__name__)
secret_key = conf.secret_key
algorithm = conf.algorithm


def get_data_from_token(encoded: str):
    return jwt.decode(encoded, secret_key, algorithms=[algorithm])


def data_encode_to_jwt(decoded: dict):
    return jwt.encode(decoded, secret_key, algorithm)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return data_encode_to_jwt(to_encode)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(days=7)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return data_encode_to_jwt(to_encode)


def check_refresh_token(refresh_token: str, fp: str):
    try:
        payload = get_data_from_token(refresh_token)
    except jwt.ExpiredSignatureError:
        raise RefreshTokenNotExistsError
    except jwt.InvalidTokenError as exc:
        log.exception("ошибка декодирования refresh токена")
        raise InvalidRefreshTokenError from exc

    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError

    if payload.get("fp") != fp:
        log.debug("fingerprint not match")
        raise InvalidRefreshTokenError

    return payload
    # if payload.get("sub") != str(my_id):
    #     raise InvalidRefreshTokenError


def create_token_from_refresh(tokens_manager, fp: str):
    refresh_token = tokens_manager.get_refresh_token()
    log.debug("refresh_token: %s", refresh_token)
    if refresh_token is not None:
        sub = check_refresh_token(refresh_token, fp)
        access_token_ttl_in_seconds, refresh_token_ttl_in_seconds = 900, 86400 * 7
        access_token_ttl, refresh_token_ttl = timedelta(
            seconds=access_token_ttl_in_seconds
        ), timedelta(seconds=refresh_token_ttl_in_seconds)
        access_token, refresh_token = create_access_token(
            sub, access_token_ttl
        ), create_refresh_token(sub, refresh_token_ttl)
        tokens_manager.set_access_token(access_token)
        tokens_manager.set_refresh_token(refresh_token)
    raise RefreshTokenNotExistsError


async def check_user(manager, username: str, password: str):
    try:
        user = (await manager.read(Admin, username=username))[0]
        if not verify(password, user["password"]):
            raise CredentialsValidateError
    except IndexError:
        log.debug("user with username: %s not found", username)
        raise NotFoundError


async def create_tokens_from_login(
    manager, username: str, password: str, tokens_manager, **data
):
    await check_user(manager, username, password)
    data.update(username=username)
    access_token_ttl, refresh_token_ttl = timedelta(seconds=900), timedelta(
        seconds=86400 * 7
    )
    access_token, refresh_token = create_access_token(
        data, access_token_ttl
    ), create_refresh_token(data, refresh_token_ttl)
    tokens_manager.set_access_token(access_token)
    tokens_manager.set_refresh_token(refresh_token)
