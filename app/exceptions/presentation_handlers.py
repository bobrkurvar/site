import logging
from pathlib import Path

from fastapi import Request, status
from fastapi.templating import Jinja2Templates

from domain import Box, Tile, TileColor, TileSize, TileSurface
from repo import get_db_manager
from repo.exceptions import (AlreadyExistsError,
                             CustomForeignKeyViolationError, DatabaseError,
                             NotFoundError)

log = logging.getLogger(__name__)
templates = Jinja2Templates("templates")


async def admin_not_found_handler(request: Request, exc: NotFoundError):
    log.error("Ошибка поиска в базе данных: %s", exc)

    manager = get_db_manager()
    tiles = await manager.read(Tile)

    tile_sizes = await manager.read(TileSize)
    tile_colors = await manager.read(TileColor)
    surfaces = await manager.read(TileSurface)
    boxes = await manager.read(Box)

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tiles": tiles,
            "tile_sizes": tile_sizes,
            "tile_colors": tile_colors,
            "tile_surfaces": surfaces,
            "boxes": boxes,
        },
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def admin_already_exists_handler(request: Request, exc: AlreadyExistsError):
    log.error("Ошибка создания в базе данных: %s", exc)

    manager = get_db_manager()
    tiles = await manager.read(Tile)

    tile_sizes = await manager.read(TileSize)
    tile_colors = await manager.read(TileColor)
    surfaces = await manager.read(TileSurface)
    boxes = await manager.read(Box)

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tiles": tiles,
            "tile_sizes": tile_sizes,
            "tile_colors": tile_colors,
            "tile_surfaces": surfaces,
            "boxes": boxes,
        },
        status_code=status.HTTP_409_CONFLICT,
    )


async def admin_foreign_key_handler(
    request: Request, exc: CustomForeignKeyViolationError
):
    log.error("Ошибка создания внешнего ключа: %s", exc)

    manager = get_db_manager()
    tiles = await manager.read(Tile)

    tile_sizes = await manager.read(TileSize)
    tile_colors = await manager.read(TileColor)
    surfaces = await manager.read(TileSurface)
    boxes = await manager.read(Box)

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tiles": tiles,
            "tile_sizes": tile_sizes,
            "tile_colors": tile_colors,
            "tile_surfaces": surfaces,
            "boxes": boxes,
        },
        status_code=status.HTTP_409_CONFLICT,
    )


async def admin_database_error_handler(request: Request, exc: DatabaseError):
    log.error("Ошибка базы данных: %s", exc)

    manager = get_db_manager()
    tiles = await manager.read(Tile)

    tile_sizes = await manager.read(TileSize)
    tile_colors = await manager.read(TileColor)
    surfaces = await manager.read(TileSurface)
    boxes = await manager.read(Box)

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tiles": tiles,
            "tile_sizes": tile_sizes,
            "tile_colors": tile_colors,
            "tile_surfaces": surfaces,
            "boxes": boxes,
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def admin_global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    manager = get_db_manager()
    tiles = await manager.read(Tile)

    tile_sizes = await manager.read(TileSize)
    tile_colors = await manager.read(TileColor)
    surfaces = await manager.read(TileSurface)
    boxes = await manager.read(Box)

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "tiles": tiles,
            "tile_sizes": tile_sizes,
            "tile_colors": tile_colors,
            "tile_surfaces": surfaces,
            "boxes": boxes,
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def presentation_global_error_handler(request: Request, exc: Exception):
    log.error("Глобальная ошибка: %s", exc)
    slides_dir = Path.cwd() / "static" / "images" / "slides"

    slide_images = [
        f"/static/images/slides/{img.name}"
        for img in slides_dir.iterdir()
        if img.is_file()
    ]
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "slide_images": slide_images},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
