from typing import Annotated

from fastapi import Depends, Request, Response
import logging
from core import conf
from infra.auth import check_access_token
from services.auth import create_token_from_refresh
from adapters.deps import RedisDep

log = logging.getLogger(__name__)


class AuthCookies:
    def __init__(self):
        self.refresh_token_key = "refresh_token"
        self.access_token_key = "access_token"
        self.cookie_secret = not conf.is_test

    def get_refresh_token(self, request: Request):
        return request.cookies.get(self.refresh_token_key)

    def get_access_token(self, request: Request):
        return request.cookies.get(self.access_token_key)

    def clear_tokens(self, response: Response):
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token", path="/admin")

    def set_refresh_token(self, response: Response, value: str):
        ttl = 86400 * 7
        response.set_cookie(
            self.refresh_token_key,
            value,
            httponly=True,
            max_age=ttl,
            samesite="strict",
            secure=self.cookie_secret,
            path="/admin",
        )

    def set_access_token(self, response: Response, value: str):
        ttl = 900
        response.set_cookie(
            self.access_token_key,
            value,
            httponly=True,
            max_age=ttl,
            samesite="strict",
            secure=self.cookie_secret,
        )


authCookiesDep = Annotated[AuthCookies, Depends()]


async def require_admin(request: Request, cookies: authCookiesDep, redis: RedisDep):
    access_token = cookies.get_access_token(request)
    if access_token:
        log.debug("access token exists")
        check_access_token(access_token)
        log.debug("access token approve")
    else:
        refresh_token = cookies.get_refresh_token(request)
        return await create_token_from_refresh(refresh_token, redis)


RequireForAdminDep = Annotated[dict | None, Depends(require_admin)]
