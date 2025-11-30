import logging
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from repo import Crud, get_db_manager
from services.tile import add_tile, delete_tile
from pathlib import Path
import aiofiles


router = APIRouter(prefix="/admin/tiles")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)



@router.post("/insert/slide-image")
async def insert_slide_image(
    images: Annotated[list[UploadFile], File()]
):
    path = r"static\images\slides"
    upload_dir = Path(path)
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
    # Поднимаемся на 3 уровня вверх от текущего файла
    project_root = Path(__file__).resolve().parent.parent.parent
    upload_dir = project_root / "static" / "images" / "slides"

    # Проверяем существование папки
    if not upload_dir.exists():
        upload_dir.mkdir(parents=True, exist_ok=True)

    # Очищаем только файлы, не папки
    for f in upload_dir.iterdir():
        if f.is_file() and f.exists():
            f.unlink()

    return RedirectResponse("/admin", status_code=303)

@router.post("/delete")
async def delete_tile_by_criteria_or_all(
    manager: dbManagerDep,
    tile_id: Annotated[int, Form()] = None,
):
    params = {}
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
    length_str, width_str,  height_str = size.split()
    length = Decimal(length_str)
    width = Decimal(width_str)
    height = Decimal(height_str)
    surface = surface or None
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
        manager,
        bytes_images,
        color_feature,
        surface,
    )
    return RedirectResponse("/admin", status_code=303)
