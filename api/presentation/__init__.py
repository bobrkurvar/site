from fastapi import APIRouter

# from .entities import (categories_router, entity_collections_router,
#                        tile_boxes_router, tile_color_router,
#                        tile_producers_router, tile_router, tile_size_router,
#                        tile_surface_router)
from .entities import admin_router
from .views import (catalog_router, clients_router, collections_router,
                    home_router, view_admin_router)

presentation_router = APIRouter()

#presentation_router.include_router(tile_router)
#presentation_router.include_router(tile_size_router)
#presentation_router.include_router(tile_color_router)
#presentation_router.include_router(tile_surface_router)
presentation_router.include_router(home_router)
presentation_router.include_router(catalog_router)
presentation_router.include_router(view_admin_router)
#presentation_router.include_router(tile_boxes_router)
#presentation_router.include_router(tile_producers_router)
#presentation_router.include_router(categories_router)
presentation_router.include_router(clients_router)
#presentation_router.include_router(entity_collections_router)
presentation_router.include_router(collections_router)
presentation_router.include_router(admin_router)