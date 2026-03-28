from typing import Annotated

from fastapi import Depends, Request, Response
from services.auth import require_admin
from services.security import compute_user_fingerprint
import logging

log = logging.getLogger(__name__)


class CookieManager:

    def __init__(self, request: Request = None, response: Response = None):
        self.request = request
        self.refresh_token_key = "refresh_token"
        self.access_token_key = "access_token"
        self.response = response
        log.debug("cookies: %s", self.request.cookies)

    def set_response(self, response: Response):
        self.response = response

    def get_refresh_token(self):
        return self.request.cookies.get(self.refresh_token_key)

    def get_access_token(self):
        return self.request.cookies.get(self.access_token_key)

    def clear_tokens(self):
        if self.response:
            self.response.set_cookie("access_token", value="", max_age=0)
            self.response.set_cookie("refresh_token", value="", max_age=0, path="/admin/refresh")

    def set_refresh_token(self, value):
        log.debug("response: %s", self.response)
        if self.response is not None:
            log.debug("set refresh token in cookie")
            ttl = 86400 * 7
            self.response.set_cookie(
                self.refresh_token_key,
                value,
                httponly=True,
                max_age=ttl,
                samesite="strict",
                secure=True,
                path="/admin"
            )

    def set_access_token(self, value):
        log.debug("response: %s", self.response)
        if self.response is not None:
            log.debug("set access token in cookie")
            ttl = 900
            self.response.set_cookie(
                self.access_token_key,
                value,
                httponly=True,
                max_age=ttl,
                samesite="strict",
                secure=True,
            )


def compute_fingerprint_from_request(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host
    log.debug("user agent: %s", user_agent)
    log.debug("client ip: %s", client_ip)
    return compute_user_fingerprint(user_agent, client_ip)


fingerPrintDep = Annotated[str, Depends(compute_fingerprint_from_request)]

def get_cookie_manager(
    request: Request,
) -> CookieManager:
    return CookieManager(request=request)

tokensManagerDep = Annotated[CookieManager, Depends(get_cookie_manager)]

def require_admin_for_dep(tokens_manager: tokensManagerDep, fp: fingerPrintDep):
    return require_admin(tokens_manager, fp)