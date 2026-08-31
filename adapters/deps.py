from typing import Annotated

from fastapi import Depends, Request

from adapters.uow import UnitOfWork
from adapters.http_client import HttpClient
from adapters.query_service import CatalogQueryService
from adapters.redis import RedisService
from db.mapper import registry


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


# def get_db_manager(request: Request):
#     db_provider = request.app.state.db_provider
#     if db_provider is None:
#         raise RuntimeError("db connection is not initialized")
#     return build_crud(db_provider.session_factory)


def get_uow(request: Request):
    db_provider = request.app.state.db_provider
    if db_provider is None:
        raise RuntimeError("db connection is not initialized")
    return UnitOfWork(registry=registry, provider=db_provider)


def get_catalog_query_service(request: Request):
    db_provider = request.app.state.db_provider
    if db_provider is None:
        raise RuntimeError("db connection is not initialized")
    return CatalogQueryService(db_provider.session_factory)


RedisDep = Annotated[RedisService, Depends(get_redis)]
HttpClientDep = Annotated[HttpClient, Depends(get_image_api)]
UowDep = Annotated[UnitOfWork, Depends(get_uow)]
QueryServiceDep = Annotated[CatalogQueryService, Depends(get_catalog_query_service)]
