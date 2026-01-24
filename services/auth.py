from domain.user import Admin
from domain.policies.auth import get_tokens
import logging

log = logging.getLogger(__name__)

async def get_tokens_and_check_user(manager, refresh_token: str | None = None, password: str | None = None, username: str | None = None):
    cur = (await manager.read(Admin, username=username))
    if len(cur) == 0:
        log.debug("USER NOT FOUND")
        raise Exception
    cur = cur[0]
    username = cur.get("username")
    password_hash = cur.get("password")
    log.info("access token не существует")
    await get_tokens(refresh_token, password_hash, password, username)