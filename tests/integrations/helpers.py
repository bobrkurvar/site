import io
from decimal import Decimal

from PIL import Image

from domain import Box, Categories, Producer, TileColor, TileSize, TileSurface
from services.UoW import UnitOfWork
from services.exceptions import ImageProcessingError

# def _iter_files(file_manager, layer: str, names=None):
#     path = file_manager.resolve_path(layer=layer)
#     if not path.exists():
#         return []
#     return (
#         [f for f in path.iterdir() if f.is_file() and f.name in names]
#         if names
#         else [f for f in path.iterdir() if f.is_file()]
#     )
#
#
# def count_by_layer(file_manager, layer: str, names: str | None = None) -> int:
#     return len(_iter_files(file_manager, layer, names))
#
#
# def slides_files_count(file_manager) -> int:
#     return count_by_layer(file_manager, "original_slide") + count_by_layer(
#         file_manager, "slides"
#     )
#
#
# def collection_files_count(file_manager, names=None) -> int:
#     return count_by_layer(
#         file_manager, names=names, layer="original_collection"
#     ) + count_by_layer(file_manager, names=names, layer="collections")
#
#
# def product_files_count(file_manager, names=None) -> int:
#     return (
#         count_by_layer(file_manager, names=names, layer="original_product")
#         + count_by_layer(file_manager, names=names, layer="products")
#         + count_by_layer(file_manager, names=names, layer="details")
#     )


def _iter_files(file_manager, layer: str):
    path = file_manager.resolve_path(layer=layer)
    if not path.exists():
        return []
    return [f for f in path.iterdir() if f.is_file()]


def count_by_layer(file_manager, layer: str) -> int:
    return len(_iter_files(file_manager, layer))


def slides_files_count(file_manager) -> int:
    return count_by_layer(file_manager, "original_slide") + count_by_layer(
        file_manager, "slides"
    )


def collection_files_count(file_manager) -> int:
    return count_by_layer(file_manager, layer="original_collection") + count_by_layer(
        file_manager, layer="collections"
    )


def product_files_count(file_manager) -> int:
    return (
        count_by_layer(file_manager, layer="original_product")
        + count_by_layer(file_manager, layer="products")
        + count_by_layer(file_manager, layer="details")
    )


async def fill_handbooks(
    length: Decimal,
    width: Decimal,
    height: Decimal,
    color_name: str,
    producer_name: str,
    box_weight: Decimal,
    box_area: Decimal,
    category_name: str,
    manager,
    color_feature: str = "",
    surface: str | None = None,
    uow_class=UnitOfWork,
):
    async with uow_class(manager) as uow:
        await manager.create(
            TileColor,
            color_name=color_name,
            feature_name=color_feature,
            session=uow.session,
        )
        await manager.create(TileSurface, name=surface, session=uow.session)
        await manager.create(Categories, name=category_name, session=uow.session)
        await manager.create(
            TileSize, length=length, width=width, height=height, session=uow.session
        )
        await manager.create(Producer, name=producer_name, session=uow.session)
        await manager.create(Box, weight=box_weight, area=box_area, session=uow.session)


def create_fake_image(format="JPEG", size=(100, 100), color="red"):
    """Создаёт изображение заданного формата и возвращает его байты."""
    img = Image.new("RGB", size, color=color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()
