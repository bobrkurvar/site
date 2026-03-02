import pytest
from .helpers import get_tokens
from tests.fakes.http_fake import token_getter_with_storage, token_setter_with_storage
from services.auth import get_access_token
from core import conf
import jwt

@pytest.mark.asyncio
async def test_get_access_token_from_refresh_access():
    _, refresh_token = get_tokens()
    token_storage = {"refresh_token": refresh_token}
    token_setter, token_getter = token_setter_with_storage(token_storage), token_getter_with_storage(token_storage)
    access_token = get_access_token(token_getter, token_setter)
    assert access_token is not None
    payload = jwt.decode(access_token, conf.secret_key, [conf.algorithm])
    #assert payload["username"]


