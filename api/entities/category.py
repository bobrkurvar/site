import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from domain import Categories
from adapters.crud import Crud, get_db_manager

router = APIRouter(prefix="/admin/tiles/categories")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_create_tile_box(manager: dbManagerDep, name: Annotated[str, Form()]):
    filters = {}
    if name is not None:
        filters["name"] = name

    await manager.delete(Categories, **filters)
    return RedirectResponse("/admin", status_code=303)
