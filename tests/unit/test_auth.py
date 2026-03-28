import logging

import pytest

from services.auth import (create_access_token, create_refresh_token,
                           create_token_from_refresh, create_tokens_from_login,
                           get_data_from_token)
from services.security import get_hash
from domain import Admin, CredentialsValidateError
from tests.fakes.user_agen_fakes import FakeCookieManager

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
    access_token = create_refresh_token(data)
    data_from_token = get_data_from_token(access_token)
    log.debug("data_from_token: %s", data_from_token)
    assert data_from_token["user"] == data["user"]
    assert data_from_token["id"] == data["id"]
    assert data_from_token["type"] == "refresh"


@pytest.mark.asyncio
async def test_get_tokens_from_login_success(crud):
    cookie_manager = FakeCookieManager()
    username, password = "username", "password"
    hash_password = get_hash(password)
    await crud.create(Admin, username=username, password=hash_password)
    await create_tokens_from_login(crud, username, password, cookie_manager)
    refresh_token, access_token = cookie_manager.get_refresh_token(), cookie_manager.get_access_token()
    log.debug("refresh_token: %s", refresh_token)
    assert refresh_token and access_token


@pytest.mark.asyncio
async def test_get_tokens_from_login_wrong_password(crud):
    cookie_manager = FakeCookieManager()
    username, password = "username", "password"
    hash_password = get_hash(password)
    await crud.create(Admin, username=username, password=hash_password)
    wrong_password = "wrong_password"
    with pytest.raises(CredentialsValidateError):
        await create_tokens_from_login(crud, username, wrong_password, cookie_manager)
    refresh_token, access_token = cookie_manager.get_refresh_token(), cookie_manager.get_access_token()
    log.debug("refresh_token: %s", refresh_token)


@pytest.mark.asyncio
async def test_get_tokens_from_login_wrong_username(crud):
    cookie_manager = FakeCookieManager()
    username, password = "username", "password"
    hash_password = get_hash(password)
    await crud.create(Admin, username=username, password=hash_password)
    wrong_username = "wrong_username"
    with pytest.raises(CredentialsValidateError):
        await create_tokens_from_login(crud, username, wrong_username, cookie_manager)
    refresh_token, access_token = cookie_manager.get_refresh_token(), cookie_manager.get_access_token()
    log.debug("refresh_token: %s", refresh_token)


