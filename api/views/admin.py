import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from adapters.crud import Crud, get_db_manager
from domain import *
from domain.exceptions import UnauthorizedError, NotFoundError
from services.auth import get_tokens_and_check_user

router = APIRouter(tags=["admin"], prefix="/admin")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("")
async def admin_page(request: Request, manager: dbManagerDep):
    #cookies = request.cookies
    #access_token = request.cookies.get("access_token")
    #log.debug("cookies: %s", cookies)
    #if access_token is None:
    #    return RedirectResponse("/admin/login", status_code=303)

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

    return templates.TemplateResponse(
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
            "access_token": access_token,
        },
    )


@router.get("/login")
async def admin_login(request: Request, manager: dbManagerDep):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is not None:
        try:
            access_token, refresh_token = await get_tokens_and_check_user(
                manager, refresh_token
            )
            response = RedirectResponse("/admin", status_code=303)
            response.set_cookie(
                "access_token", access_token, httponly=True, max_age=900
            )
            response.set_cookie(
                "refresh_token", refresh_token, httponly=True, max_age=86400 * 7
            )
        except UnauthorizedError:
            response = templates.TemplateResponse(
                "admin_login.html", {"request": request}
            )
    else:
        response = templates.TemplateResponse(
            "admin_login.html", {"request": request}
        )
    return response


@router.post("/login/submit")
async def admin_login_submit(
    manager: dbManagerDep,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    try:
        access_token, refresh_token = await get_tokens_and_check_user(
            manager, username=username, password=password
        )
        if access_token and refresh_token:
            response = RedirectResponse("/admin", status_code=303)
            response.set_cookie("access_token", access_token, httponly=True, max_age=900)
            response.set_cookie(
                "refresh_token", refresh_token, httponly=True, max_age=86400 * 7
            )
            return response
    except UnauthorizedError:
        return RedirectResponse("/admin/login?err=401", status_code=303)
    except NotFoundError:
        return RedirectResponse("/admin/login?err=409", status_code=303)
