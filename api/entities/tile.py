import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from adapters.deps import DbManagerDep, HttpClientDep
from adapters.images import ProductImagesManager, ImageGenerator
from domain import *
from services.tile import add_tile, delete_tile, update_tile
from api.utils import api_input_to_params, strip_input_params
from api.schemas import CreateTile

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
    dto: Annotated[CreateTile, Form()],
    main_image: Annotated[UploadFile, File()],
    images: Annotated[list[UploadFile], File()],
    manager: DbManagerDep,
    http_client: HttpClientDep,
):
    #bytes_images = [await img.read() for img in images] if images else []
    bytes_main_image = await main_image.read()
    bytes_images = [bytes_main_image] + [await img.read() for img in images]
    tile = Tile(
        size = TileSize(length=dto.length, width=dto.width, height=dto.height),
        color = TileColor(color_name=dto.color_name, feature_name=dto.feature_name),
        name=dto.name,
        box=Box(area=dto.box_area, weight=dto.box_weight),
        producer=Producer(name=dto.producer_name),
        category=Category(name=dto.category_name),
        surface=TileSurface(name=dto.surface_name),
        boxes_count=dto.boxes_count,
        images=bytes_images
    )
    await add_tile(
        tile,
        manager=manager,
        images_generator=ImageGenerator(http_client),
        file_manager=ProductImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)


# @router.post("/create")
# async def admin_create_tile(
#     name: Annotated[str, Form()],
#     size: Annotated[str, Form()],
#     color_name: Annotated[str, Form()],
#     producer_name: Annotated[str, Form()],
#     box_weight: Annotated[Decimal, Form()],
#     box_area: Annotated[Decimal, Form()],
#     boxes_count: Annotated[int, Form()],
#     main_image: Annotated[UploadFile, File()],
#     category_name: Annotated[str, Form()],
#     manager: DbManagerDep,
#     http_client: HttpClientDep,
#     feature_name: Annotated[str, Form()],
#     surface_name: Annotated[str, Form()],
#     images: Annotated[list[UploadFile], File()],
# ):
#     #tile = map_to_tile_domain()
#     name, size, color_name, producer_name, category_name, feature_name, surface_name = [
#         value.strip()
#         for value in (
#             name,
#             size,
#             color_name,
#             producer_name,
#             category_name,
#             feature_name,
#             surface_name,
#         )
#     ]
#     bytes_images = [await img.read() for img in images] if images else []
#     bytes_main_image = await main_image.read()
#     length_str, width_str, height_str = size.split()
#     length, width, height = Decimal(length_str), Decimal(width_str), Decimal(height_str)
#     surface_name = surface_name or None
#     tile = Tile(
#         size = TileSize(length=length, width=width, height=height),
#         color = TileColor(color_name=color_name, feature_name=feature_name),
#         name=name,
#         box=Box(area=box_area, weight=box_weight),
#
#     )
#     await add_tile(
#         name,
#         length,
#         width,
#         height,
#         color_name,
#         producer_name,
#         box_weight,
#         box_area,
#         boxes_count,
#         bytes_main_image,
#         category_name,
#         manager,
#         bytes_images,
#         images_generator=ImageGenerator(http_client),
#         file_manager=ProductImagesManager(),
#         color_feature=feature_name,
#         surface=surface_name,
#     )
#     return RedirectResponse("/admin", status_code=303)


@router.post("/update")
async def admin_update_tile(
    manager: DbManagerDep,
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
    params = {
        k: v
        for k, v in locals().items()
        if v not in (None, "") and k not in ("manager", "article")
    }
    params = strip_input_params(**params)
    params = api_input_to_params(**params)

    log.debug("to update: %s", params)
    if params:
        await update_tile(manager, article, **params)
    return RedirectResponse("/admin", status_code=303)
