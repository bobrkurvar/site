import logging
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse

from adapters.deps import UowDep
from domain import Size

router = APIRouter(prefix="/admin/tiles/sizes")
log = logging.getLogger(__name__)


@router.post("/delete")
async def admin_delete_tile_size(
    uow: UowDep,
    height: Annotated[Decimal, Form(gt=0)] = None,
    width: Annotated[Decimal, Form(gt=0)] = None,
    length: Annotated[Decimal, Form(gt=0)] = None,
):
    async with uow:
        if height is not None and width is not None and length is not None:
            await uow.db.delete(Size, height=height, width=width, length=length)
        else:
            await uow.db.delete(Size)
    return RedirectResponse("/admin", status_code=303)
