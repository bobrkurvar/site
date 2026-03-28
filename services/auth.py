import logging
from datetime import datetime, timedelta, timezone

import jwt

from core import conf
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

def create_token(data: dict, expire: datetime, toke_type: str):
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": toke_type})
    return data_encode_to_jwt(to_encode)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(minutes=15)
    expire, data = datetime.now(timezone.utc) + expires_delta, data.copy()
    return create_token(data, expire, "access")


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(days=7)
    expire, data = datetime.now(timezone.utc) + expires_delta, data.copy()
    return create_token(data, expire, "refresh")


def check_refresh_token(token: str, fp: str):
    try:
        payload = get_data_from_token(token)
    except jwt.ExpiredSignatureError:
        raise RefreshTokenNotExistsError
    except jwt.InvalidTokenError as exc:
        log.exception(f"ошибка декодирования refresh токена")
        raise InvalidRefreshTokenError from exc

    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError

    if not verify(fp, payload.get("fp")):
        log.debug("fingerprint not match")
        raise InvalidRefreshTokenError

    return payload


def check_access_token(token: str, fp: str):
    try:
        payload = get_data_from_token(token)
    except jwt.ExpiredSignatureError:
        raise RefreshTokenNotExistsError
    except jwt.InvalidTokenError as exc:
        log.exception(f"ошибка декодирования access токена")
        raise InvalidAccessTokenError from exc

    if payload.get("type") != "access":
        raise InvalidAccessTokenError

    if not verify(fp, payload.get("fp")):
        log.debug("fingerprint not match")
        raise InvalidAccessTokenError

    return payload


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
        return {"access_token": access_token, "refresh_token": refresh_token}
    raise RefreshTokenNotExistsError



def set_tokens(tokens_manager, access_token, refresh_token):
    tokens_manager.set_access_token(access_token)
    tokens_manager.set_refresh_token(refresh_token)


async def check_user(manager, username: str, password: str):
    try:
        user = (await manager.read(Admin, username=username))[0]
        if not verify(password, user["password"]):
            raise CredentialsValidateError
    except IndexError:
        log.debug("user with username: %s not found", username)
        raise UserLoginNotFoundError(username)


async def create_tokens_from_login(
    manager, username: str, password: str, tokens_manager, **data
):
    log.debug("check user")
    await check_user(manager, username, password)
    log.debug("user approve")
    data.update(username=username)
    access_token_ttl, refresh_token_ttl = timedelta(seconds=900), timedelta(
        seconds=86400 * 7
    )
    access_token, refresh_token = create_access_token(
        data, access_token_ttl
    ), create_refresh_token(data, refresh_token_ttl)
    tokens_manager.set_access_token(access_token)
    tokens_manager.set_refresh_token(refresh_token)


def require_admin(tokens_manager, fp):
    access_token = tokens_manager.get_access_token()
    if access_token:
        log.debug("access token exists")
        check_access_token(access_token, fp=fp)
        log.debug("access token approve")
    else:
        return create_token_from_refresh(tokens_manager, fp)
