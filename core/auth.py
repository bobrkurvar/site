import logging
from datetime import datetime, timedelta, timezone

import jwt
from domain.exceptions import UnauthorizedError
import bcrypt

from core import config, logger

secret_key = config.secret_key
algorithm = config.algorithm
log = logging.getLogger(__name__)


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    #log.debug("UTC: %s", datetime.now(timezone.utc))
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(days=7)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)


def check_refresh_token(refresh_token: str, username: str):
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
    # except jwt.ExpiredSignatureError:
    #     raise UnauthorizedError(refresh_token=True)
    except jwt.InvalidTokenError:
        raise UnauthorizedError(refresh_token=True)
    if payload.get("type") != "refresh":
        raise UnauthorizedError(refresh_token=True)
    if payload.get("sub") != username:
        raise UnauthorizedError(refresh_token=True)


async def create_dict_tokens_and_save(username):
    access_token = create_access_token({"sub":username, "type": "access"})
    refresh_token = create_refresh_token({"sub": username, "type": "refresh"})
    return access_token, refresh_token

async def get_tokens(refresh_token: str | None = None, password_hash: str = None, password: str | None = None, username: str | None = None):
    access_token = None
    if password is not None and verify(password, password_hash):
        log.debug("password verify")
        access_token, refresh_token = await create_dict_tokens_and_save(username)
    elif refresh_token is not None:
        log.info("refresh token существует")
        payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
        log.debug("PAYLOAD: %s", payload)
        check_refresh_token(refresh_token, username)
        log.info("refresh token прошёл проверку")
        username = payload.get("sub")
        access_token, refresh_token = await create_dict_tokens_and_save(username)
    return access_token, refresh_token