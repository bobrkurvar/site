import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi_csrf_protect.flexible import CsrfProtect
from starlette.responses import RedirectResponse

from adapters.crud import Crud, get_db_manager
from adapters.user_agent import CookieManager, fingerPrintDep
from domain import *
from domain.exceptions import NotFoundError, UnauthorizedError
from services.auth import create_token_from_refresh, create_tokens_from_login

router = APIRouter(tags=["admin"], prefix="/admin")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
csrfProtectDep = Annotated[CsrfProtect, Depends()]

templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("")
async def admin_page(
    request: Request, manager: dbManagerDep, csrf_token: csrfProtectDep
):
    cookies = request.cookies
    access_token = request.cookies.get("access_token")
    log.debug("cookies: %s", cookies)
    if access_token is None:
        return RedirectResponse("/admin/refresh", status_code=303)

    plain_token, signed_token = csrf_token.generate_csrf_tokens()

    tiles = await manager.read(Tile, to_join=["images", "size", "box"])
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
    tile_colors = await manager.read(TileColor)
    surfaces = await manager.read(TileSurface)
    boxes = await manager.read(Box)
    producers = await manager.read(Producer)

    unique_colors = set()
    unique_features = set()

    for tile_color in tile_colors:
        unique_colors.add(tile_color["color_name"])
        if tile_color["feature_name"] != "":
            unique_features.add(tile_color["feature_name"])

    boxes_unique_weight = set()
    boxes_unique_area = set()

    for box in boxes:
        boxes_unique_weight.add(box["weight"])
        boxes_unique_area.add(box["area"])

    tiles = [map_to_tile_domain(**t) for t in tiles]
    boxes_unique_count = set(q.boxes_count for q in tiles)

    categories = await manager.read(Categories)

    response = templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tiles": tiles,
            "tile_sizes": tile_sizes,
            "tile_colors": tile_colors,
            "tile_surfaces": surfaces,
            "boxes": boxes,
            "producers": producers,
            "unique_colors": unique_colors,
            "unique_features": unique_features,
            "boxes_unique_weight": boxes_unique_weight,
            "boxes_unique_area": boxes_unique_area,
            "categories": categories,
            "boxes_unique_count": boxes_unique_count,
            "csrf_token": plain_token,
        },
    )
    csrf_token.set_csrf_cookie(signed_token, response)
    return response


@router.post("/refresh")
async def refresh_access_token(request: Request, fingerprint: fingerPrintDep):
    try:
        response = RedirectResponse("/admin", 303)
        cookie_manager = CookieManager(request=request, response=response)
        create_token_from_refresh(tokens_manager=cookie_manager, fp=fingerprint)
    except RefreshTokenNotExistsError:
        response = RedirectResponse("admin/login", 303)
    return response


@router.post("/login")
async def admin_login_submit(
    request: Request,
    manager: dbManagerDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    fingerprint: fingerPrintDep,
):
    try:
        response = RedirectResponse("/admin", status_code=303)
        cookie_manager = CookieManager(request=request, response=response)
        await create_tokens_from_login(
            manager,
            username=username,
            password=password,
            tokens_manager=cookie_manager,
            fp=fingerprint,
        )
    except UnauthorizedError:
        return RedirectResponse("/admin/login?err=401", status_code=303)
    except NotFoundError:
        return RedirectResponse("/admin/login?err=409", status_code=303)
