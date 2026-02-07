import logging
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from adapters.crud import Crud, get_db_manager
from domain import Box

router = APIRouter(prefix="/admin/tiles/boxes")
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_create_tile_box(
    manager: dbManagerDep,
    weight: Annotated[Decimal, Form()] = None,
    area: Annotated[Decimal, Form()] = None,
):
    filters = {}
    if weight is not None:
        filters["weight"] = weight
    if area is not None:
        filters["area"] = area

    await manager.delete(Box, **filters)
    return RedirectResponse("/admin", status_code=303)
