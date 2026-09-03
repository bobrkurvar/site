import logging

import pytest

from domain import (
    RefreshTokenFamilyExpiredError,
    RefreshTokenReusedCompromisedError,
)
from infra.auth import get_data_from_token
from infra.security import create_token_family_id, create_token_jti
from services.auth import (
    create_access_token,
    create_refresh_token,
    create_tokens_from_refresh,
    consume_refresh_token,
)

log = logging.getLogger(__name__)


def test_create_access_token():
    data = {"role": "user", "sub": "1"}
    access_token = create_access_token(data)
    data_from_token = get_data_from_token(access_token)
    log.debug("data_from_token: %s", data_from_token)
    assert data_from_token["role"] == data["role"]
    assert data_from_token["sub"] == data["sub"]
    assert data_from_token["type"] == "access"


def test_create_refresh_token():
    data = {"role": "user", "sub": "1"}
    family_id, jti = create_token_family_id(), create_token_jti()
    refresh_token = create_refresh_token(data, family_id=family_id, jti=jti)
    data_from_token = get_data_from_token(refresh_token)
    log.debug("data_from_token: %s", data_from_token)
    assert data_from_token["role"] == data["role"]
    assert data_from_token["sub"] == data["sub"]
    assert data_from_token["type"] == "refresh"
    assert family_id == data_from_token["family_id"] and jti == data_from_token["jti"]


@pytest.mark.asyncio
async def test_get_new_tokens_from_refresh_success(redis, uow_fix):
    data = {"role": "user", "sub": "1"}
    family_id, jti = create_token_family_id(), create_token_jti()
    refresh_token = create_refresh_token(data, family_id=family_id, jti=jti)
    # устанавливаю ключи для проверки правильной токена
    await redis.set(f"rtfam:{family_id}", value=1, ttl=86400 * 7)
    await redis.set(f"rt:{jti}", value=-1, ttl=86400 * 7)
    tokens = await create_tokens_from_refresh(
        refresh_token=refresh_token, redis=redis, uow=uow_fix
    )
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    assert access_token and refresh_token


@pytest.mark.asyncio
async def test_get_new_tokens_from_refresh_fail_when_family_not_exists(redis, uow_fix):
    # Если в кэше нет записи о семействе, значит токен выдан не мной или запись закончилась
    # что означает что и refresh токен должен закончиться
    data = {"role": "user", "sub": "1"}
    family_id, jti = create_token_family_id(), create_token_jti()
    refresh_token = create_refresh_token(data, family_id=family_id, jti=jti)
    with pytest.raises(RefreshTokenFamilyExpiredError):
        await create_tokens_from_refresh(
            refresh_token=refresh_token, redis=redis, uow=uow_fix
        )


@pytest.mark.asyncio
async def test_consume_refresh_token_deletes_family_when_token_reused(redis):
    family_id = "family-1"
    jti = "jti-1"

    await redis.set(f"rtfam:{family_id}", value=1, ttl=86400 * 7)
    await redis.set(f"rt:{jti}", value=0, ttl=86400 * 7)

    payload = {
        "family_id": family_id,
        "jti": jti,
    }

    with pytest.raises(RefreshTokenReusedCompromisedError):
        await consume_refresh_token(payload, redis)

    assert not await redis.exists(f"rtfam:{family_id}")
