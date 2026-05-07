from typing import Annotated
from fastapi import Depends, Request
from adapters.redis import RedisService
from adapters.http_client import HttpClient
from adapters.db import Crud, build_crud


def get_redis(request: Request) -> RedisService:
    provider = request.app.state.redis
    if provider is None:
        raise RuntimeError("Redis connection is not initialized")
    return RedisService(redis=provider.client)


def get_image_api(request: Request) -> HttpClient:
    client = request.app.state.image_api
    if client is None:
        raise RuntimeError("Image API client is not initialized")
    return client


def get_db_manager(request: Request):
    db_provider = request.app.state.db_provider
    if db_provider is None:
        raise RuntimeError("db connection is not initialized")
    return build_crud(db_provider.session_factory)


RedisDep = Annotated[RedisService, Depends(get_redis)]
HttpClientDep = Annotated[HttpClient, Depends(get_image_api)]
DbManagerDep = Annotated[Crud, Depends(get_db_manager)]
