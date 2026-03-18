import logging

#from core.auth import get_tokens
from datetime import timedelta, datetime, timezone
from domain.exceptions import *
from domain.user import Admin
from services.security import verify
from core import conf
import jwt

log = logging.getLogger(__name__)
secret_key = conf.secret_key
algorithm = conf.algorithm


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, secret_key, algorithm)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(days=7)
    )
    to_encode.update({"exp": expire, "type":"refresh"})
    # log.debug("refresh to_encode: %s", to_encode)
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def check_refresh_token(refresh_token: str, my_id: int):
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise RefreshTokenExpireError
    except jwt.InvalidTokenError as exc:
        log.exception("ошибка декодирования refresh токена")
        raise InvalidRefreshTokenError from exc

    if payload.get("type") != "refresh":
        raise InvalidRefreshTokenError

    if payload.get("sub") != str(my_id):
        raise InvalidRefreshTokenError


def get_access_token(
    data: dict, token_getter, token_setter
):
    access_token = token_getter("access_token")
    if access_token is None:
        refresh_token = token_getter("refresh_token")
        if refresh_token is not None:
            sub = jwt.decode(refresh_token, conf.secret_key, [conf.algorithm])
            access_token_ttl_in_seconds, refresh_token_ttl_in_seconds = 900, 86400*7
            access_token_ttl, refresh_token_ttl = timedelta(seconds=access_token_ttl_in_seconds), timedelta(seconds=refresh_token_ttl_in_seconds)
            access_token, refresh_token = create_access_token(sub, access_token_ttl), create_refresh_token(sub, refresh_token_ttl)
            token_setter("access_token", access_token, access_token_ttl_in_seconds)
            token_setter("refresh_token", refresh_token, refresh_token_ttl_in_seconds)
        raise RefreshTokenExpireError



async def get_token_from_password(
    manager,
    username: str,
    password: str,
    token_setter
):
    user = (await manager.read(Admin, username=username))[0]
    if len(user) != 0:
        if verify(password, user["password"]):
            sub = {"username": username}
            access_token_ttl_in_seconds, refresh_token_ttl_in_seconds = 900, 86400 * 7
            access_token_ttl, refresh_token_ttl = timedelta(seconds=access_token_ttl_in_seconds), timedelta(
                seconds=refresh_token_ttl_in_seconds)
            access_token, refresh_token = create_access_token(sub, access_token_ttl), create_refresh_token(sub, refresh_token_ttl)
            token_setter("access_token", access_token, access_token_ttl_in_seconds)
            token_setter("refresh_token", refresh_token, refresh_token_ttl_in_seconds)
        else:
            raise CredentialsValidateError
    else:
        log.debug("user with username: %s not found", username)
        raise NotFoundError


