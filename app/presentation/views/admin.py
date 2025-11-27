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
    tiles = await manager.read(Tile, to_join=["images"])
    for t in tiles:
        log.debug("images: %s", t['images_paths'])
    tile_sizes = await manager.read(TileSize)
    tile_sizes = [TileSize(size['height'], size['width']) for size in tile_sizes]
    tile_colors = await manager.read(TileColor)
    surfaces = await manager.read(TileSurface)
    boxes = await manager.read(Box)
    producers = await manager.read(Producer)

    unique_color = set()
    unique_feature = set()
    tile_colors_unique_color = []
    tile_colors_unique_feature = []
    for color in tile_colors:
        if color.get("color_name") not in unique_color:
            tile_colors_unique_color.append(color)
            unique_color.add(color.get("color_name"))

        if color.get("feature_name") not in unique_feature:
            tile_colors_unique_feature.append(color)
            unique_feature.add(color.get("feature_name"))

    unique_weight = set()
    unique_area = set()
    boxes_unique_weight = []
    boxes_unique_area = []

    for box in boxes:
        if box.get("weight") not in unique_weight:
            boxes_unique_weight.append(box)
            unique_weight.add(box.get("weight"))

        if box.get("area") not in unique_area:
            boxes_unique_area.append(box)
            unique_area.add(box.get("area"))


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
            "colors_unique_color": tile_colors_unique_color,
            "colors_unique_feature": tile_colors_unique_feature,
            "boxes_unique_weight": boxes_unique_weight,
            "boxes_unique_area": boxes_unique_area,
        },
    )
