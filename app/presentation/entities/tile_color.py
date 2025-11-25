import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from domain import TileColor
from repo import Crud, get_db_manager

router = APIRouter(prefix="/admin/tiles")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


# @router.post("/color/feature/create")
# async def admin_create_tile_color_feature(
#     manager: dbManagerDep, name: Annotated[str, Form()]
# ):
#     await manager.create(TileColorFeature, name=name)
#     return RedirectResponse("/admin", status_code=303)
#
#
# @router.post("/color/feature/delete")
# async def admin_delete_tile_color_feature(
#     manager: dbManagerDep, name: Annotated[str, Form()] = None
# ):
#     if name:
#         log.debug("name: %s", name)
#         await manager.delete(TileColorFeature, name=name)
#     else:
#         await manager.delete(TileColorFeature)
#     return RedirectResponse("/admin", status_code=303)
#
#
# @router.post("/color/create")
# async def admin_create_tile_color(
#     manager: dbManagerDep, name: Annotated[str, Form()], feature: Annotated[str, Form()]
# ):
#     await manager.create(TileColor, name=name, feature_name=feature)
#     return RedirectResponse("/admin", status_code=303)
#
#
# @router.post("/color/delete")
# async def admin_delete_all_colors(
#     manager: dbManagerDep, name: Annotated[str, Form()] = None
# ):
#     if name:
#         await manager.delete(TileColor, name=name)
#     else:
#         await manager.delete(TileColor)
#     return RedirectResponse("/admin", status_code=303)
