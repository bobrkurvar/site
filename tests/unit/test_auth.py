import logging

import pytest

from domain import (Admin, CredentialsValidateError,
                    RefreshTokenFamilyExpiredError,
                    RefreshTokenReusedCompromisedError, UserLoginNotFoundError)
from infra.auth import get_data_from_token
from infra.security import create_token_family_id, create_token_jti
from services.auth import (create_access_token, create_refresh_token,
                           create_tokens_from_login,
                           create_tokens_from_refresh)

log = logging.getLogger(__name__)


def test_create_access_token():
    data = {"user": "user", "id": 1}
    access_token = create_access_token(data)
    data_from_token = get_data_from_token(access_token)
    log.debug("data_from_token: %s", data_from_token)
    assert data_from_token["user"] == data["user"]
    assert data_from_token["id"] == data["id"]
    assert data_from_token["type"] == "access"


def test_create_refresh_token():
    data = {"user": "user", "id": 1}
    family_id, jti = create_token_family_id(), create_token_jti()
    refresh_token = create_refresh_token(data, family_id=family_id, jti=jti)
    data_from_token = get_data_from_token(refresh_token)
    log.debug("data_from_token: %s", data_from_token)
    assert data_from_token["user"] == data["user"]
    assert data_from_token["id"] == data["id"]
    assert data_from_token["type"] == "refresh"
    assert family_id == data_from_token["family_id"] and jti == data_from_token["jti"]


@pytest.mark.asyncio
async def test_get_tokens_from_login_success(crud, redis):
    username, password = "username", "password"
    # hash_password = get_hash(password)
    await crud.create(Admin(username=username, password=password))
    verify = lambda pas, hash: True
    tokens = await create_tokens_from_login(
        manager=crud, redis=redis, username=username, password=password, verify=verify
    )
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    log.debug("refresh_token: %s", refresh_token)
    assert refresh_token and access_token


@pytest.mark.asyncio
async def test_get_tokens_from_login_wrong_password(crud, redis):
    username, password = "username", "password"
    # hash_password = get_hash(password)
    await crud.create(Admin(username=username, password=password))
    verify = lambda pas, hash: False
    wrong_password = "wrong_password"
    with pytest.raises(CredentialsValidateError):
        await create_tokens_from_login(
            manager=crud,
            redis=redis,
            username=username,
            password=wrong_password,
            verify=verify,
        )


@pytest.mark.asyncio
async def test_get_tokens_from_login_wrong_username(crud, redis):
    username, password = "username", "password"
    # hash_password = get_hash(password)
    verify = lambda pas, hash: True
    await crud.create(Admin(username=username, password=password))
    wrong_username = "wrong_username"
    with pytest.raises(UserLoginNotFoundError):
        await create_tokens_from_login(
            manager=crud,
            redis=redis,
            username=wrong_username,
            password=password,
            verify=verify,
        )


@pytest.mark.asyncio
async def test_get_new_tokens_from_refresh_success(redis):
    data = {"user": "user", "id": 1}
    family_id, jti = create_token_family_id(), create_token_jti()
    refresh_token = create_refresh_token(data, family_id=family_id, jti=jti)
    # устанавливаю ключи для проверки правильной токена
    await redis.set(f"rtfam:{family_id}", value=1, ttl=86400 * 7)
    await redis.set(f"rt:{jti}", value=-1, ttl=86400 * 7)
    tokens = await create_tokens_from_refresh(refresh_token, redis)
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    assert access_token and refresh_token


@pytest.mark.asyncio
async def test_get_new_tokens_from_refresh_fail_when_family_not_exists(redis):
    data = {"user": "user", "id": 1}
    family_id, jti = create_token_family_id(), create_token_jti()
    refresh_token = create_refresh_token(data, family_id=family_id, jti=jti)
    # Если в кэше нет записи о семействе, значит токен выдан не мной или запись закончилась
    # что означает что и refresh токен должен закончиться
    with pytest.raises(RefreshTokenFamilyExpiredError):
        await create_tokens_from_refresh(refresh_token, redis)


@pytest.mark.asyncio
async def test_get_new_tokens_from_refresh_fail_when_token_already_used(redis):
    data = {"user": "user", "id": 1}
    family_id, jti1, jti2 = (
        create_token_family_id(),
        create_token_jti(),
        create_token_jti(),
    )
    # выдаю 2 токена инвалидируется всё семейство токенов
    refresh_token1 = create_refresh_token(data, family_id=family_id, jti=jti1)
    refresh_token2 = create_refresh_token(data, family_id=family_id, jti=jti2)
    await redis.set(f"rtfam:{family_id}", value=1, ttl=86400 * 7)
    # ставлю 0 вместо -1, а это значит что этот токен уже не валиден при ротации и выдаче нового refresh
    await redis.set(f"rt:{jti1}", value=0, ttl=86400 * 7)
    # а этот валидный
    await redis.set(f"rt:{jti2}", value=-1, ttl=86400 * 7)
    with pytest.raises(RefreshTokenReusedCompromisedError):
        await create_tokens_from_refresh(refresh_token1, redis)
    assert not await redis.exists(f"rtfam:{family_id}")
    # даже другой токен из этого же семейства инвалидируется
    with pytest.raises(RefreshTokenFamilyExpiredError):
        await create_tokens_from_refresh(refresh_token2, redis)
