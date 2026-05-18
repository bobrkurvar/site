import logging
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from adapters.deps import DbManagerDep, RedisDep
from adapters.web import RequireForAdminDep, authCookiesDep
from services.auth import create_tokens_from_login
from domain import *
import asyncio

router = APIRouter(tags=["admin"], prefix="/admin")

templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("")
async def admin_page(
    request: Request,
    manager: DbManagerDep,
    refreshed_tokens: RequireForAdminDep,
    cookies: authCookiesDep,
):
    tiles = manager.read(Tile, loaded=["images", "size", "box"])
    tile_sizes = manager.read(TileSize)
    colors_names = manager.read(TileColor, distinct="color_name")
    colors_features = manager.read(TileColor, distinct="feature_name")
    surfaces = manager.read(TileSurface)
    boxes_weights = manager.read(Box, distinct="weight")
    boxes_areas = manager.read(Box, distinct="area")
    producers = manager.read(Producer)
    boxes_count = manager.read(Tile, distinct="boxes_count")
    categories = manager.read(Category)
    tasks = [tiles, tile_sizes, colors_names, colors_features, surfaces, boxes_weights, boxes_areas, producers, boxes_count, categories]
    tiles, tile_sizes, colors_names, colors_features, surfaces, boxes_weights, boxes_areas, producers, boxes_count, categories = await asyncio.gather(*tasks)

    response = templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tiles": tiles,
            "tile_sizes": tile_sizes,
            "colors_names": colors_names,
            "colors_features": colors_features,
            "tile_surfaces": surfaces,
            "boxes_weights": boxes_weights,
            "boxes_areas": boxes_areas,
            "producers": producers,
            "categories": categories,
            "boxes_count": boxes_count,
        },
    )
    if refreshed_tokens is not None:
        cookies.set_access_token(response, refreshed_tokens["access_token"])
        cookies.set_refresh_token(response, refreshed_tokens["refresh_token"])
    return response


@router.post("/login/submit")
async def admin_login_submit(
    manager: DbManagerDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    cookies: authCookiesDep,
    redis: RedisDep,
):
    response = RedirectResponse("/admin", status_code=303)
    tokens = await create_tokens_from_login(manager, redis, username, password)
    if tokens:
        cookies.set_access_token(response, tokens["access_token"])
        cookies.set_refresh_token(response, tokens["refresh_token"])
    return response
