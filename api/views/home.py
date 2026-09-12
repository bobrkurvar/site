import logging

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from adapters.deps import UowDep
from adapters.images import SlideImagesManager
from adapters.web import AuthCookies
from domain import Category

router = APIRouter()
templates = Jinja2Templates("templates")

log = logging.getLogger(__name__)


@router.get("/")
async def get_main_page(request: Request, uow: UowDep):
    slide_manager = SlideImagesManager()
    slide_images = slide_manager.get_all_slides_paths()
    async with uow:
        categories = await uow.db.read(Category)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "slide_images": slide_images,
            "categories": categories,
        },
    )


@router.get("/cookie/delete")
async def cookie_delete(request: Request):
    response = RedirectResponse("/", status_code=303)
    AuthCookies().clear_tokens(response)
    log.debug("COOKIES after delete: %s", response.headers)
    return response
