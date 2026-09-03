import logging
from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import RedirectResponse

from adapters.deps import HttpClientDep
from adapters.images import ImageGenerator, SlideImagesManager
from services.slides import add_slides, delete_slides

router = APIRouter(prefix="/admin/slides")
log = logging.getLogger(__name__)


@router.post("/insert")
async def admin_insert_slide(
    http_client: HttpClientDep, images: Annotated[list[UploadFile], File()]
):
    images_bytes = [await image.read() for image in images]
    await add_slides(
        images_bytes,
        images_generator=ImageGenerator(http_client),
        file_manager=SlideImagesManager(),
    )
    return RedirectResponse("/admin", status_code=303)


@router.post("/delete")
async def delete_slide_image():
    await delete_slides(file_manager=SlideImagesManager())
    return RedirectResponse("/admin", status_code=303)
