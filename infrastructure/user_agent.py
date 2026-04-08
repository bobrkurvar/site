from typing import Annotated

from fastapi import Depends, Request, Response, HTTPException, status
from services.auth import require_admin
from services.security import compute_user_fingerprint
import logging
from core import conf
# import secrets
# import hmac
# from itsdangerous import URLSafeSerializer, BadSignature
# from core import conf
# from domain import CSRFCookiesTokenNotExistsError, CSRFFormTokenNotExistsError

log = logging.getLogger(__name__)


class TokensManager:

    def __init__(self, request: Request = None, response: Response = None):
        self.request = request
        self.refresh_token_key = "refresh_token"
        self.access_token_key = "access_token"
        self.cookie_secret = False if conf.is_test else True
        log.debug("cookie_secret: %s", self.cookie_secret)
        self.response = response
        #log.debug("cookies: %s", self.request.cookies)

    def set_response(self, response: Response):
        self.response = response

    def set_request(self, request: Request):
        self.request = request

    def get_refresh_token(self):
        return self.request.cookies.get(self.refresh_token_key)

    def get_access_token(self):
        return self.request.cookies.get(self.access_token_key)

    def clear_tokens(self):
        if self.response:
            # self.response.set_cookie("access_token", value="", max_age=0)
            # self.response.set_cookie("refresh_token", value="", max_age=0, path="/admin/refresh")
            self.response.delete_cookie("access_token")
            self.response.delete_cookie("refresh_token", path="/admin/refresh")

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
                secure=self.cookie_secret,
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
                secure=self.cookie_secret,
            )


def compute_fingerprint_from_request(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "")
    #client_ip = request.client.host
    host = request.url.hostname or ""
    log.debug("user agent: %s", user_agent)
    #log.debug("client ip: %s", client_ip)
    log.debug("client host: %s", host)
    return compute_user_fingerprint(user_agent, host)


fingerPrintDep = Annotated[str, Depends(compute_fingerprint_from_request)]

def get_tokens_manager(
    request: Request,
) -> TokensManager:
    return TokensManager(request=request)

tokensManagerDep = Annotated[TokensManager, Depends(get_tokens_manager)]

def require_admin_for_dep(tokens_manager: tokensManagerDep, fp: fingerPrintDep):
    return require_admin(tokens_manager, fp)



# class CsrfManager:
#     def __init__(self) -> None:
#         self.secret_key = conf.secret_key
#         self.cookie_name = "csrf_token"
#         self.form_field_name = "token_key"
#         self.max_age = 60 * 60 * 2
#         self.salt = "csrf-token"
#         self.serializer = URLSafeSerializer(
#             secret_key=self.secret_key,
#             salt=self.salt,
#         )
#
#     @staticmethod
#     def generate_plain_token() -> str:
#         return secrets.token_urlsafe(32)
#
#     def sign_token(self, plain_token: str) -> str:
#         return self.serializer.dumps(plain_token)
#
#     def use_token(self, signed_token: str) -> str:
#         try:
#             token = self.serializer.loads(signed_token)
#         except BadSignature as exc:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid CSRF signature",
#             ) from exc
#
#         if not isinstance(token, str):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid CSRF payload",
#             )
#
#         return token
#
#     def get_tokens(self) -> tuple[str, str]:
#         plain_token = self.generate_plain_token()
#         signed_token = self.sign_token(plain_token)
#         return plain_token, signed_token
#
#     def set_csrf_cookie(self, response: Response, signed_token: str) -> None:
#         response.set_cookie(
#             key=self.cookie_name,
#             value=signed_token,
#             max_age=self.max_age,
#             secure=False,
#             httponly=True,
#             samesite="strict",
#         )
#
#     def clear_csrf_cookie(self, response: Response) -> None:
#         response.delete_cookie(self.cookie_name)
#
#     def validate_csrf(self, request: Request, plain_token_from_form: str | None) -> None:
#         signed_token = request.cookies.get(self.cookie_name)
#
#         if not signed_token:
#             raise CSRFCookiesTokenNotExistsError
#             # raise HTTPException(
#             #     status_code=status.HTTP_403_FORBIDDEN,
#             #     detail="Missing CSRF cookie",
#             # )
#
#         if not plain_token_from_form:
#             raise CSRFFormTokenNotExistsError
#             # raise HTTPException(
#             #     status_code=status.HTTP_403_FORBIDDEN,
#             #     detail="Missing CSRF form token",
#             # )
#
#         plain_token_from_cookie = self.use_token(signed_token)
#
#         if not hmac.compare_digest(plain_token_from_cookie, plain_token_from_form):
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="CSRF token mismatch",
#             )

