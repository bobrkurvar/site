from fastapi import Response, Request, Depends
from services.security import get_hash
from typing import Annotated


def get_from_cookie(request: Request, key: str):
    return request.cookies.get(key)


def save_in_cookie_http_only(response: Response, key: str, value, ttl: int):
    response.set_cookie(
        key, value, httponly=True, max_age=ttl, samesite="strict", secure=True
    )


REFRESH_KEY = "refresh_token"


def save_in_cookie_refresh_token(response: Response, token, ttl: int):
    save_in_cookie_http_only(response, REFRESH_KEY, token, ttl)


def get_refresh_token_from_cookie(request: Request):
    return get_from_cookie(request, REFRESH_KEY)


def compute_fingerprint(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host
    combined = user_agent + str(client_ip)
    return get_hash(combined)

fingerPrintDep = Annotated[str, Depends(compute_fingerprint)]