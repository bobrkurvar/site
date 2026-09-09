import logging
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from adapters.deps import UowDep
from domain import Box

router = APIRouter(prefix="/admin/tiles/boxes")
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_delete_box(
    uow: UowDep,
    weight: Annotated[Decimal, Form()] = None,
    area: Annotated[Decimal, Form()] = None,
):
    filters = {}
    if weight is not None:
        filters["weight"] = weight
    if area is not None:
        filters["area"] = area
    async with uow:
        await uow.db.delete(Box, **filters)
    return RedirectResponse("/admin", status_code=303)
