import logging

import pytest

from services.auth import (
    create_access_token,
    create_refresh_token,
    create_token_from_refresh,
    create_tokens_from_login,
)
from infra.auth import get_data_from_token
from infra.security import get_hash
from domain import Admin, CredentialsValidateError

log = logging.getLogger(__name__)


async def test_create_access_token():
    data = {"user": "user", "id": 1}
    access_token = create_access_token(data)
    data_from_token = get_data_from_token(access_token)
    log.debug("data_from_token: %s", data_from_token)
    assert data_from_token["user"] == data["user"]
    assert data_from_token["id"] == data["id"]
    assert data_from_token["type"] == "access"


def test_create_refresh_token():
    data = {"user": "user", "id": 1}
    family_id, jti = "1", "1"
    refresh_token = create_refresh_token(data, family_id, jti)
    data_from_token = get_data_from_token(refresh_token)
    log.debug("data_from_token: %s", data_from_token)
    assert data_from_token["user"] == data["user"]
    assert data_from_token["id"] == data["id"]
    assert data_from_token["type"] == "refresh"
    assert data_from_token["family_id"] == family_id
    assert data_from_token["jti"] == jti


@pytest.mark.asyncio
async def test_get_tokens_from_login_success(crud, redis):
    username, password = "username", "password"
    hash_password = get_hash(password)
    await crud.create(Admin, username=username, password=hash_password)
    tokens = await create_tokens_from_login(crud, redis, username, password)
    assert tokens["refresh_token"] and tokens["access_token"]


@pytest.mark.asyncio
async def test_get_tokens_from_login_wrong_password(crud, redis):
    username, password = "username", "password"
    hash_password = get_hash(password)
    await crud.create(Admin, username=username, password=hash_password)
    wrong_password = "wrong_password"
    with pytest.raises(CredentialsValidateError):
        await create_tokens_from_login(crud, redis, username, wrong_password)


@pytest.mark.asyncio
async def test_get_tokens_from_login_wrong_username(crud, redis):
    username, password = "username", "password"
    hash_password = get_hash(password)
    await crud.create(Admin, username=username, password=hash_password)
    wrong_username = "wrong_username"
    with pytest.raises(CredentialsValidateError):
        await create_tokens_from_login(crud, redis, username, wrong_username)


@pytest.mark.asyncio
async def test_get_access_token_from_refresh_access(crud, redis):
    username, password = "username", "password"
    hash_password = get_hash(password)
    await crud.create(Admin, username=username, password=hash_password)
    data = {"user": "user", "id": 1}
    family_id, jti = "1", "1"
    refresh_token = create_refresh_token(data, family_id, jti)
    tokens = await create_token_from_refresh(refresh_token, redis)
    refresh_token = tokens["refresh_token"]
