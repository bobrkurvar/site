import logging
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from repo import Crud, get_db_manager
from services.tile import add_tile, delete_tile

router = APIRouter(prefix="/admin/tiles")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/delete")
async def delete_tile_by_criteria_or_all(
    manager: dbManagerDep,
    name: Annotated[str, Form()] = None,
    tile_id: Annotated[int, Form()] = None,
):
    params = {}
    if name:
        params["name"] = name
    if tile_id:
        params["id"] = tile_id
    log.debug("params: %s", params)
    await delete_tile(manager, **params)
    return RedirectResponse("/admin", status_code=303)


@router.post("/create")
async def admin_create_tile(
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color_name: Annotated[str, Form()],
    producer: Annotated[str, Form()],
    box_weight: Annotated[Decimal, Form()],
    box_area: Annotated[Decimal, Form()],
    boxes_count: Annotated[int, Form()],
    main_image: Annotated[UploadFile, File()],
    manager: dbManagerDep,
    color_feature: Annotated[str, Form()] = "",
    surface: Annotated[str, Form()] = "",
    images: Annotated[list[UploadFile], File()] = None,
):
    bytes_images = [await img.read() for img in images] if images else []
    bytes_main_image = await main_image.read()
    height_str, width_str = size.split()
    height = Decimal(height_str)
    width = Decimal(width_str)
    surface = surface or None
    await add_tile(
        name,
        height,
        width,
        color_name,
        producer,
        box_weight,
        box_area,
        boxes_count,
        bytes_main_image,
        manager,
        bytes_images,
        color_feature,
        surface,
    )
    return RedirectResponse("/admin", status_code=303)
