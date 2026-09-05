import logging

import pytest

from domain import (
    Admin,
    CredentialsValidateError,
    RefreshTokenFamilyExpiredError,
    RefreshTokenReusedCompromisedError,
    UserLoginNotFoundError,
)
from infra.security import create_token_family_id, create_token_jti
from services.auth import (
    create_refresh_token,
    create_tokens_from_login,
    create_tokens_from_refresh,
)

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_get_tokens_from_login_success(uow_fix, redis):
    username, password = "username", "password"
    verify = lambda pas, hash: True
    async with uow_fix as uow:
        await uow.db.create(Admin(username=username, password=password))
        tokens = await create_tokens_from_login(
            manager=uow.db,
            redis=redis,
            username=username,
            password=password,
            verify=verify,
        )
    access_token, refresh_token = tokens["access_token"], tokens["refresh_token"]
    log.debug("refresh_token: %s", refresh_token)
    assert refresh_token and access_token


@pytest.mark.asyncio
async def test_get_tokens_from_login_wrong_password(uow_fix, redis):
    username, password = "username", "password"
    verify = lambda pas, hash: False
    wrong_password = "wrong_password"
    async with uow_fix as uow:
        await uow.db.create(Admin(username=username, password=password))
        with pytest.raises(CredentialsValidateError):
            await create_tokens_from_login(
                manager=uow.db,
                redis=redis,
                username=username,
                password=wrong_password,
                verify=verify,
            )


@pytest.mark.asyncio
async def test_get_tokens_from_login_wrong_username(uow_fix, redis):
    username, password = "username", "password"
    # hash_password = get_hash(password)
    verify = lambda pas, hash: True
    wrong_username = "wrong_username"
    async with uow_fix as uow:
        await uow.db.create(Admin(username=username, password=password))
        with pytest.raises(UserLoginNotFoundError):
            await create_tokens_from_login(
                manager=uow.db,
                redis=redis,
                username=wrong_username,
                password=password,
                verify=verify,
            )


@pytest.mark.asyncio
async def test_get_new_tokens_from_refresh_fail_when_token_already_used(uow_fix, redis):
    username, password = "username", "password"
    data = {"user": "user", "sub": username}
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
    async with uow_fix as uow:
        await uow.db.create(Admin(username=username, password=password))
    with pytest.raises(RefreshTokenReusedCompromisedError):
        await create_tokens_from_refresh(
            refresh_token=refresh_token1, redis=redis, uow=uow
        )
    with pytest.raises(RefreshTokenFamilyExpiredError):
        await create_tokens_from_refresh(
            refresh_token=refresh_token2, redis=redis, uow=uow
        )
    assert not await redis.exists(f"rtfam:{family_id}")
    # даже другой токен из этого же семейства инвалидируется
