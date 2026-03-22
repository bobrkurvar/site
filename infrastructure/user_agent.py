from typing import Annotated

from fastapi import Depends, Request, Response

from services.security import get_hash


class CookieManager:

    def __init__(self, request: Request = None, response: Response = None):
        self.request = request
        self.response = response
        self.refresh_token_key = "refresh_token"
        self.access_token_key = "access_token"

    def get_refresh_token(self):
        return self.request.cookies.get(self.refresh_token_key)

    def set_refresh_token(self, value):
        ttl = 86400 * 7
        self.response.set_cookie(
            self.refresh_token_key,
            value,
            httponly=True,
            max_age=ttl,
            samesite="strict",
            secure=True,
            path="/admin/refresh"
        )

    def set_access_token(self, value):
        ttl = 900
        self.response.set_cookie(
            self.access_token_key,
            value,
            httponly=True,
            max_age=ttl,
            samesite="strict",
            secure=True,
        )


def compute_fingerprint(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host
    combined = user_agent + str(client_ip)
    return get_hash(combined)


fingerPrintDep = Annotated[str, Depends(compute_fingerprint)]
