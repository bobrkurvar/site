import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.templating import Jinja2Templates
#from fastapi_csrf_protect.flexible import CsrfProtect
from starlette.responses import RedirectResponse

from infrastructure.crud import Crud, get_db_manager
from infrastructure.user_agent import (
    TokensManager,
    fingerPrintDep,
    require_admin_for_dep,
)
from services.auth import create_tokens_from_login_and_set, set_tokens
from domain import *
from services.security import get_hash

router = APIRouter(tags=["admin"], prefix="/admin")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
#csrfProtectDep = Annotated[CsrfProtect, Depends()]
requireAdminDep = Annotated[dict | None, Depends(require_admin_for_dep)]

templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("")
async def admin_page(
    request: Request,
    manager: dbManagerDep,
    #csrf_token: csrfProtectDep,
    tokens: requireAdminDep,
):
    #plain_token, signed_token = csrf_token.generate_csrf_tokens()
    token_manager = TokensManager()
    tiles = await manager.read(Tile, loaded=["images", "size", "box"])
    tile_sizes = await manager.read(TileSize)
    tile_sizes = [
        TileSize(
            size_id=size["id"],
            length=size["length"],
            width=size["width"],
            height=size["height"],
        )
        for size in tile_sizes
    ]
    colors_names = await manager.read(TileColor, distinct="color_name")
    colors_features = await manager.read(TileColor, distinct="feature_name")
    surfaces = await manager.read(TileSurface)
    boxes_weights = await manager.read(Box, distinct="weight")
    boxes_areas = await manager.read(Box, distinct="area")
    producers = await manager.read(Producer)
    boxes_count = await manager.read(Tile, distinct="boxes_count")
    tiles = [map_to_tile_domain(**t) for t in tiles]
    categories = await manager.read(Categories)

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
            #"csrf_token": csrf_token,

        },
    )
    if tokens:
        token_manager.set_request(request)
        token_manager.set_response(response)
        set_tokens(
            token_manager,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
    #csrf_token.set_csrf_cookie(signed_token, response)
    #cookie_manager.set_csrf_cookie(response, csrf_token)
    return response


@router.post("/login/submit")
async def admin_login_submit(
    request: Request,
    manager: dbManagerDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    fingerprint: fingerPrintDep,
):
    fp = get_hash(fingerprint)
    response = RedirectResponse("/admin", status_code=303)
    await create_tokens_from_login_and_set(
        manager,
        username=username,
        password=password,
        tokens_manager=TokensManager(request=request, response=response),
        fp=fp,
    )
    return response
