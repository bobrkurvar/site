from fastapi import Response, Request


def get_from_cookie(request: Request, key: str):
    return request.cookies.get(key)


def save_in_cookie_http_only(response: Response, key: str, value, ttl: int):
    response.set_cookie(key, value, httponly=True, max_age=ttl, samesite="strict", secure=True)


REFRESH_KEY = "refresh_token"

def save_in_cookie_refresh_token(response: Response, token, ttl: int):
    save_in_cookie_http_only(response, REFRESH_KEY, token, ttl)

def get_refresh_token_from_cookie(request: Request):
    return get_from_cookie(request, REFRESH_KEY)