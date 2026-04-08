from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
# from fastapi_csrf_protect.flexible import CsrfProtect

from infrastructure.user_agent import require_admin_for_dep

from .category import router as categories_router
from .collections import router as entity_collections_router
from .tile import router as tile_router
from .tile_boxes import router as tile_boxes_router
from .tile_color import router as tile_color_router
from .tile_producers import router as tile_producers_router
from .tile_size import router as tile_size_router
from .tile_surface import router as tile_surface_router
import logging


# csrfProtectDep = Annotated[CsrfProtect, Depends()]
log = logging.getLogger(__name__)

# async def csrf_validate(request: Request, csrf_protect: csrfProtectDep):
#     if request.method in {"POST", "PUT", "DELETE", "PATCH"}:
#         form = await request.form()
#         token = form.get("token_key")
#         log.debug("TOKEN: %s", repr(token))
#         log.debug("TYPE: %s", type(token))
#         await csrf_protect.validate_csrf(request)

# async def csrf_validate(request: Request, csrf_token: Annotated[str, Form()],):
#     cookie_manager = TokensManager(request=request)
#     cookie_manager.validate_csrf(csrf_token)


admin_router = APIRouter(dependencies=[Depends(require_admin_for_dep)])
admin_router.include_router(tile_router)
admin_router.include_router(tile_size_router)
admin_router.include_router(tile_color_router)
admin_router.include_router(tile_surface_router)
admin_router.include_router(tile_boxes_router)
admin_router.include_router(tile_producers_router)
admin_router.include_router(categories_router)
admin_router.include_router(entity_collections_router)
