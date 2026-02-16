import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from adapters.crud import Crud, get_db_manager
from adapters.images import (ProductImagesManager,
                             generate_image_products_catalog_and_details)
from domain import *
from services.tile import add_tile, delete_tile, update_tile

router = APIRouter(prefix="/admin/tiles")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

log = logging.getLogger(__name__)


@router.post("/delete")
async def delete_tile_by_id_or_all(
    manager: dbManagerDep,
    tile_id: Annotated[int, Form()] = None,
):
    params = {}
    log.debug("tile_id: %s", tile_id)
    if tile_id is not None:
        params["id"] = tile_id
    log.debug("params: %s", params)
    await delete_tile(manager, ProductImagesManager(), **params)
    return RedirectResponse("/admin", status_code=303)


@router.post("/create")
async def admin_create_tile(
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color_name: Annotated[str, Form()],
    producer_name: Annotated[str, Form()],
    box_weight: Annotated[Decimal, Form()],
    box_area: Annotated[Decimal, Form()],
    boxes_count: Annotated[int, Form()],
    main_image: Annotated[UploadFile, File()],
    category_name: Annotated[str, Form()],
    manager: dbManagerDep,
    feature_name: Annotated[str, Form()],
    surface_name: Annotated[str, Form()],
    images: Annotated[list[UploadFile], File()],
):
    name, size, color_name, producer_name, category_name, feature_name, surface_name = [
        value.strip()
        for value in (
            name,
            size,
            color_name,
            producer_name,
            category_name,
            feature_name,
            surface_name,
        )
    ]
    bytes_images = [await img.read() for img in images] if images else []
    bytes_main_image = await main_image.read()
    length_str, width_str, height_str = size.split()
    length = Decimal(length_str)
    width = Decimal(width_str)
    height = Decimal(height_str)
    surface_name = surface_name or None
    log.debug("tile_type: %s", category_name)
    await add_tile(
        name,
        length,
        width,
        height,
        color_name,
        producer_name,
        box_weight,
        box_area,
        boxes_count,
        bytes_main_image,
        category_name,
        manager,
        bytes_images,
        generate_images=generate_image_products_catalog_and_details,
        file_manager=ProductImagesManager(),
        color_feature=feature_name,
        surface=surface_name,
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/update")
async def admin_update_tile(
    manager: dbManagerDep,
    article: Annotated[int, Form()],
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color_name: Annotated[str, Form()],
    producer_name: Annotated[str, Form()],
    box_weight: Annotated[Decimal | str, Form()],
    box_area: Annotated[Decimal | str, Form()],
    boxes_count: Annotated[int | str, Form()],
    category_name: Annotated[str, Form()],
    feature_name: Annotated[str, Form()],
    surface_name: Annotated[str, Form()],
):
    name, size, color_name, producer_name, category_name, feature_name, surface_name = [
        value.strip()
        for value in (
            name,
            size,
            color_name,
            producer_name,
            category_name,
            feature_name,
            surface_name,
        )
    ]
    params = locals()
    params = {
        k: v
        for k, v in params.items()
        if v not in (None, "") and k not in ("manager", "article")
    }
    if size != "":
        length, width, height = size.split()
        params.pop("size")
        params["size"] = {"length": Decimal(length), "width": Decimal(width), "height": Decimal(height)}

    log.debug("to update: %s", params)
    if params:
        await update_tile(manager, article, **params)
    return RedirectResponse("/admin", status_code=303)
