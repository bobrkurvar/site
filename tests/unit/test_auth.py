import pytest
from services.auth import (
    create_refresh_token,
    create_access_token,
    get_data_from_token,
    create_tokens_from_login,
    create_token_from_refresh,
)
from services.security import get_hash
import logging

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
async def get_tokens_from_login():
    username, password = "username", "password"
    hash_password = get_hash(password)
    # await create_tokens_from_login()


@pytest.mark.asyncio
async def get_tokens_from_refresh():
    pass
