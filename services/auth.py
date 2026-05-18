import logging
from datetime import datetime, timedelta, timezone
from domain import (
    RefreshTokenReusedCompromisedError,
    RefreshTokenRotationRaceConditionError,
    RefreshTokenFamilyExpiredError,
    RefreshTokenMissingError,
    UserLoginNotFoundError,
    CredentialsValidateError
)
from domain.user import Admin
from infra.security import create_token_jti, create_token_family_id #vefiry
from infra.auth import data_encode_to_jwt, check_refresh_token

log = logging.getLogger(__name__)


def create_token(data: dict, expire: datetime, toke_type: str):
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": toke_type})
    return data_encode_to_jwt(to_encode)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(minutes=15)
    expire, data = datetime.now(timezone.utc) + expires_delta, data.copy()
    return create_token(data, expire, "access")


def create_refresh_token(
    data: dict, family_id: str, jti: str, expires_delta: timedelta = None
) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(days=7)
    expire, data = datetime.now(timezone.utc) + expires_delta, data.copy()
    data.update(family_id=family_id, jti=jti)
    return create_token(data, expire, "refresh")


async def check_rotate(payload: dict, redis):
    jti, family_id = payload["jti"], payload["family_id"]
    if not await redis.exists(f"rtfam:{family_id}"):
        raise RefreshTokenFamilyExpiredError

    if await redis.incr(f"rt:{jti}") != 0:
        await redis.delete(f"rtfam:{family_id}")
        raise RefreshTokenReusedCompromisedError

    if not await redis.exists(f"rtfam:{family_id}"):
        raise RefreshTokenRotationRaceConditionError

    new_jti = create_token_jti()
    await redis.set(f"rt:{new_jti}", -1, ttl=86400 * 7)
    await redis.expire(f"rtfam:{family_id}", ttl=86400 * 7)

    return new_jti, family_id


async def create_tokens_from_refresh(refresh_token: str | None, redis):
    if refresh_token is None:
        raise RefreshTokenMissingError
    sub = check_refresh_token(refresh_token)
    jti, family_id = await check_rotate(sub, redis)
    tokens_data = {
        k: v for k, v in sub.items() if k not in {"jti", "family_id", "exp", "type"}
    }
    return {
        "access_token": create_access_token(tokens_data),
        "refresh_token": create_refresh_token(
            tokens_data, jti=jti, family_id=family_id
        ),
    }


async def check_user(manager, verify, username: str, password: str):
    user = await manager.read_one(Admin, username=username)
    if not user:
        log.debug("user with username: %s not found", username)
        raise UserLoginNotFoundError(username)
    if not verify(password, user.password):
        log.debug("wrong password")
        raise CredentialsValidateError


async def create_tokens_from_login(
    manager, redis, username: str, password: str, verify, **data
):
    log.debug("check user")
    await check_user(manager, verify, username, password)
    log.debug("user approve")
    data.update(username=username)
    jti, family_id = create_token_jti(), create_token_family_id()
    await redis.set(f"rtfam:{family_id}", value=1, ttl=86400 * 7)
    await redis.set(f"rt:{jti}", value=-1, ttl=86400 * 7)
    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token(data, jti=jti, family_id=family_id),
    }
