import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from domain import TileColor
from repo import Crud, get_db_manager

router = APIRouter(prefix="/admin/products/colors")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_delete_tile_color_feature(
    manager: dbManagerDep,
    color_name: Annotated[str, Form()] = None,
    feature_name: Annotated[str, Form()] = None,
):
    filters = {}
    if color_name:
        log.debug("color_name: %s", color_name)
        filters["color_name"] = color_name
    if feature_name:
        log.debug("feature_name: %s", feature_name)
        filters["feature_name"] = feature_name
    await manager.delete(TileColor, **filters)
    return RedirectResponse("/admin", status_code=303)
