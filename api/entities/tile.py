import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from adapters.deps import DbManagerDep, HttpClientDep
from adapters.images import ImageGenerator, ProductImagesManager

# from api.utils import api_input_to_params, strip_input_params
from api.schemas import CreateTile, UpdateTile
from api.utils import create_tile_form
from domain import *
from services.tile import add_tile, delete_tile, update_tile

router = APIRouter(prefix="/admin/tiles")

log = logging.getLogger(__name__)


@router.post("/delete")
async def delete_tile_by_id_or_all(
    manager: DbManagerDep,
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
    dto: Annotated[CreateTile, Depends(create_tile_form)],
    main_image: Annotated[UploadFile, File()],
    images: Annotated[list[UploadFile], File()],
    manager: DbManagerDep,
    http_client: HttpClientDep,
):
    bytes_main_image = await main_image.read()
    bytes_images = [bytes_main_image] + [await img.read() for img in images]
    images = [Image(image_bytes=img) for img in bytes_images]
    tile = Tile(
        size=TileSize(length=dto.length, width=dto.width, height=dto.height),
        color=TileColor(color_name=dto.color_name, feature_name=dto.feature_name),
        name=dto.name,
        box=Box(area=dto.box_area, weight=dto.box_weight),
        producer=Producer(name=dto.producer_name),
        category=Category(name=dto.category_name),
        surface=TileSurface(name=dto.surface_name),
        boxes_count=dto.boxes_count,
        images=images,
    )
    await add_tile(
        tile,
        manager=manager,
        images_generator=ImageGenerator(http_client),
        file_manager=ProductImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/update")
async def admin_update_tile(
    manager: DbManagerDep,
    dto: Annotated[UpdateTile, Form()],
):
    params = dto.custom_dump()
    log.debug("to update: %s", params)
    if params:
        await update_tile(manager, **params)
    return RedirectResponse("/admin", status_code=303)
