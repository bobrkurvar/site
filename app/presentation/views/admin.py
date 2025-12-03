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
        unique_features.add(tile_color["feature_name"])
    # for color in tile_colors:
    #     if color.get("color_name") not in unique_color:
    #         tile_colors_unique_color.append(color)
    #         unique_color.add(color.get("color_name"))
    #
    #     if color.get("feature_name") not in unique_feature:
    #         tile_colors_unique_feature.append(color)
    #         unique_feature.add(color.get("feature_name"))

    # unique_weight = set()
    # unique_area = set()
    boxes_unique_weight = set()
    boxes_unique_area =  set()
    for box in boxes:
        boxes_unique_weight.add(box["weight"])
        boxes_unique_area.add(box["area"])

    tiles = [map_to_tile_domain(t) for t in tiles]
    boxes_unique_count = set(tile.boxes_count for tile in tiles)

    # for box in boxes:
    #     if box.get("weight") not in unique_weight:
    #         boxes_unique_weight.append(box)
    #         unique_weight.add(box.get("weight"))
    #
    #     if box.get("area") not in unique_area:
    #         boxes_unique_area.append(box)
    #         unique_area.add(box.get("area"))

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
