import logging
from typing import Annotated
from decimal import Decimal


from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from domain import TileSize
from repo import Crud, get_db_manager

router = APIRouter(prefix="/admin/tiles")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/sizes/delete")
async def admin_delete_tile_size(
    manager: dbManagerDep,
    height: Annotated[Decimal, Form(gt=0)] = None,
    width: Annotated[Decimal, Form(gt=0)] = None,
    length: Annotated[Decimal, Form(gt=0)] = None,
):
    if height is not None and width is not None and length is not None:
        await manager.delete(TileSize, height=height, width=width, length=length)
    else:
        await manager.delete(TileSize)
    return RedirectResponse("/admin", status_code=303)


# @router.post("/sizes/create")
# async def admin_create_tile_size(
#     manager: dbManagerDep,
#     height: Annotated[float | None, Form(gt=0)],
#     width: Annotated[float | None, Form(gt=0)],
# ):
#     await manager.create(TileSize, height=height, width=width)
#     return RedirectResponse("/admin", status_code=303)
