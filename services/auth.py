import logging
from datetime import datetime, timedelta, timezone

from domain import (CredentialsValidateError, RefreshTokenFamilyExpiredError,
                    RefreshTokenMissingError,
                    RefreshTokenReusedCompromisedError,
                    RefreshTokenRotationRaceConditionError,
                    UserLoginNotFoundError)
from domain.user import Admin
from infra.auth import check_refresh_token, data_encode_to_jwt
from infra.security import create_token_family_id, create_token_jti

log = logging.getLogger(__name__)

REFRESH_TTL_SECONDS = 86400 * 7

def _create_token(data: dict, expire: datetime, toke_type: str):
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": toke_type})
    return data_encode_to_jwt(to_encode)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(minutes=15)
    expire, data = datetime.now(timezone.utc) + expires_delta, data.copy()
    return _create_token(data, expire, "access")


def create_refresh_token(
    data: dict, family_id: str, jti: str, expires_delta: timedelta = None
) -> str:
    expires_delta = expires_delta if expires_delta else timedelta(days=7)
    expire, data = datetime.now(timezone.utc) + expires_delta, data.copy()
    data.update(family_id=family_id, jti=jti)
    return _create_token(data, expire, "refresh")


async def delete_redis_keys(redis, jti: str, family_id: str):
    await redis.delete(f"rtfam:{family_id}")
    await redis.delete(f"rt:{jti}")


async def consume_refresh_token(payload: dict, redis):
    """
    Потребляет refresh-токен при ротации.

    Refresh-токен должен быть использован ровно один раз.
    Для защиты от гонки используется атомарный Redis INCR:
    первый consume переводит значение jti из -1 в 0,
    повторное использование даёт значение не 0 и инвалидирует всё семейство.
    """
    jti, family_id = payload["jti"], payload["family_id"]
    if not await redis.exists(f"rtfam:{family_id}"):
        raise RefreshTokenFamilyExpiredError

    if await redis.incr(f"rt:{jti}") != 0:
        await delete_redis_keys(redis, jti, family_id)
        raise RefreshTokenReusedCompromisedError

    if not await redis.exists(f"rtfam:{family_id}"):
        await redis.delete(f"rtfam:{family_id}")
        raise RefreshTokenRotationRaceConditionError

    new_jti = create_token_jti()
    await redis.set(f"rt:{new_jti}", -1, ttl=REFRESH_TTL_SECONDS)
    await redis.expire(f"rtfam:{family_id}", ttl=REFRESH_TTL_SECONDS)

    return new_jti, family_id



async def create_tokens_from_refresh(uow, refresh_token: str | None, redis):
    if refresh_token is None:
        raise RefreshTokenMissingError
    payload = check_refresh_token(refresh_token)
    user_id = int(payload["int"])
    async with uow:
        await uow.db.read_one(Admin, id=user_id, with_raise=True)
    jti, family_id = await consume_refresh_token(payload, redis)
    tokens_data = {
        k: v for k, v in payload.items() if k not in {"jti", "family_id", "exp", "type"}
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
