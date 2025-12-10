import logging
from decimal import Decimal
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from domain import *
from repo import Crud, get_db_manager
from services.tile import add_tile, delete_tile, update_tile

router = APIRouter(prefix="/admin/tiles")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/insert/slide-image")
async def insert_slide_image(images: Annotated[list[UploadFile], File()]):

    path = Path(__file__).resolve().parent.parent.parent.parent
    upload_dir = Path(path) / "static" / "images" / "slides"

    if not upload_dir.exists():
        upload_dir.mkdir(parents=True, exist_ok=True)
    extra_num = len([f for f in upload_dir.iterdir() if f.is_file()])
    for i, image in enumerate(images):
        image_byte = await image.read()
        image_path = upload_dir / str(extra_num + i)
        log.debug("slide image: %s", image_path)
        try:
            async with aiofiles.open(image_path, "xb") as fw:
                await fw.write(image_byte)
        except FileExistsError:
            log.debug("путь %s уже занять", image_path)

    return RedirectResponse("/admin", status_code=303)


@router.post("/delete/all-slide-image")
async def insert_slide_image():
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    upload_dir = project_root / "static" / "images" / "slides"
    log.debug("deleted slite dir: %s", upload_dir)
    for f in upload_dir.iterdir():
        if f.is_file() and f.exists():
            f.unlink()

    return RedirectResponse("/admin", status_code=303)


@router.post("/delete")
async def delete_tile_by_id_or_all(
    manager: dbManagerDep,
    tile_id: Annotated[int, Form()] = None,
):
    log.debug("tile id for delete: %s", tile_id)
    params = {}
    log.debug("tile_id: %s", tile_id)
    if tile_id is not None:
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
    tile_type: Annotated[str, Form()],
    manager: dbManagerDep,
    color_feature: Annotated[str, Form()],
    surface: Annotated[str, Form()],
    images: Annotated[list[UploadFile], File()],
):
    name, size, color_name, producer, tile_type, color_feature, surface = [value.strip() for value in (name, size, color_name, producer, tile_type, color_feature, surface)]
    bytes_images = [await img.read() for img in images] if images else []
    bytes_main_image = await main_image.read()
    length_str, width_str, height_str = size.split()
    length = Decimal(length_str)
    width = Decimal(width_str)
    height = Decimal(height_str)
    surface = surface or None
    log.debug("tile_type: %s", tile_type)
    await add_tile(
        name,
        length,
        width,
        height,
        color_name,
        producer,
        box_weight,
        box_area,
        boxes_count,
        bytes_main_image,
        tile_type,
        manager,
        bytes_images,
        color_feature,
        surface,
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/update")
async def admin_update_tile(
    manager: dbManagerDep,
    article: Annotated[int, Form()],
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color_name: Annotated[str, Form()],
    producer: Annotated[str, Form()],
    box_weight: Annotated[Decimal | str, Form()],
    box_area: Annotated[Decimal | str, Form()],
    boxes_count: Annotated[int | str, Form()],
    tile_type: Annotated[str, Form()],
    color_feature: Annotated[str, Form()],
    surface: Annotated[str, Form()],
):
    name, size, color_name, producer, tile_type, color_feature, surface = [value.strip() for value in (name, size, color_name, producer, tile_type, color_feature, surface)]
    params = locals()
    params = {
        k: v
        for k, v in params.items()
        if v not in (None, "") and k not in ("manager", "article")
    }
    log.debug("to update: %s", params)
    if params:
        await update_tile(manager, article, **params)
    return RedirectResponse("/admin", status_code=303)
