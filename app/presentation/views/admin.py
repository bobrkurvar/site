import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from domain import *
from repo import Crud, get_db_manager

router = APIRouter(tags=["admin"], prefix="/admin")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
templates = Jinja2Templates("templates")
log = logging.getLogger(__name__)


@router.get("")
async def admin_page(request: Request, manager: dbManagerDep):
    tiles = await manager.read(Tile, to_join=["images", "size", "box"])
    for t in tiles:
        log.debug("images: %s", t["images_paths"])
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

    tiles = [map_to_tile_domain(t) for t in tiles]
    boxes_unique_count = set(tile.boxes_count for tile in tiles)

    log.debug("colors_names: %s", unique_colors)
    log.debug("features_names: %s", unique_features)
    categories = await manager.read(Types)

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
        },
    )
