import logging
from services.slides import add_slides, delete_slides
from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import RedirectResponse


router = APIRouter(prefix="/admin/slides")
log = logging.getLogger(__name__)


@router.post("/insert")
async def insert_slide_image(images: Annotated[list[UploadFile], File()]):
    images_bytes = [await image.read() for image in images]
    await add_slides(images_bytes)
    return RedirectResponse("/admin", status_code=303)


@router.post("/delete")
async def insert_slide_image():
    await delete_slides()
    return RedirectResponse("/admin", status_code=303)
