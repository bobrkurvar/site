import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse

from repo import Crud, get_db_manager
from services.tile import add_tile, delete_tile

router = APIRouter(prefix='/admin/tile')
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/delete")
async def delete_tile_by_criteria_or_all(
    manager: dbManagerDep,
    name: Annotated[str, Form()] = None,
    tile_id: Annotated[int, Form()] = None
):
    params = {}
    if name: params['name'] = name
    if tile_id: params['id'] = tile_id
    log.debug("params: %s", params)
    await delete_tile(manager, **params)
    return RedirectResponse("/admin", status_code=303)


@router.post("/create")
async def admin_create_tile(
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color_name: Annotated[str, Form()],
    color_feature: Annotated[str, Form()],
    surface: Annotated[str, Form()],
    image: Annotated[UploadFile, File()],
    manager: dbManagerDep,
):
    bytes_image = await image.read()
    height_str, width_str = size.split()
    height = float(height_str)
    width = float(width_str)
    log.debug("height: %s, width: %s, color: %s, surface: %s", height, width, color_name, surface)
    await add_tile(name, height, width, color_name, color_feature, surface, bytes_image, manager)
    return RedirectResponse("/admin", status_code=303)
