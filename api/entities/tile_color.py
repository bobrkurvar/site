import logging
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from adapters.deps import DbManagerDep
from domain import TileColor

router = APIRouter(prefix="/admin/tiles/colors")
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_delete_tile_color_feature(
    manager: DbManagerDep,
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
