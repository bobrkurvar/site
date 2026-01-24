from core.security import create_access_token, create_refresh_token, verify, check_refresh_token, algorithm
from domain.user import Admin
import logging
import jwt
from core import config

secret_key = config.secret_key
algorithm = config.algorithm

log = logging.getLogger(__name__)

async def create_dict_tokens_and_save(username):
    access_token = create_access_token({"sub":username, "type": "access"})
    refresh_token = create_refresh_token({"sub": username, "type": "refresh"})
    return access_token, refresh_token

async def get_tokens(manager, refresh_token: str | None = None, password: str | None = None, username: str | None = None):
    cur = (await manager.read(Admin, username=username))
    if len(cur) == 0:
        log.debug("USER NOT FOUND")
        raise Exception
    cur = cur[0]
    ident_val = cur.get("username")
    log.info("access token не существует")
    log.debug("password: %s", password)
    access_token = None
    if password is not None and verify(password, cur.get("password")):
        log.debug("password verify")
        access_token, refresh_token = await create_dict_tokens_and_save(username)
    elif refresh_token is not None:
            log.info("refresh token существует")
            check_refresh_token(refresh_token, ident_val)
            log.info("refresh token прошёл проверку")
            payload = jwt.decode(refresh_token, secret_key, algorithms=algorithm)
            username = payload.get("sub")
            access_token, refresh_token = await create_dict_tokens_and_save(username)
    return access_token, refresh_token