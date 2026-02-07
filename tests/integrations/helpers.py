from decimal import Decimal
from services.UoW import UnitOfWork
from domain import TileColor, TileSize, TileSurface, Categories, Box, Producer

def _iter_files(file_manager, layer: str, names=None):
    path = file_manager.resolve_path(layer=layer)
    if not path.exists():
        return []
    return (
        [f for f in path.iterdir() if f.is_file() and f.name in names]
        if names
        else [f for f in path.iterdir() if f.is_file()]
    )


def count_by_layer(file_manager, layer: str, names: str | None = None) -> int:
    return len(_iter_files(file_manager, layer, names))


def slides_files_count(file_manager) -> int:
    return count_by_layer(file_manager, "original_slide") + count_by_layer(
        file_manager, "slides"
    )


def collection_files_count(file_manager, names=None) -> int:
    return count_by_layer(
        file_manager, names=names, layer="original_collection"
    ) + count_by_layer(file_manager, names=names, layer="collections")


def product_files_count(file_manager, names=None) -> int:
    return (
        count_by_layer(file_manager, names=names, layer="original_product")
        + count_by_layer(file_manager, names=names, layer="products")
        + count_by_layer(file_manager, names=names, layer="details")
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
    async with uow_class(manager._session_factory) as uow:
        await manager.create(TileColor, color_name=color_name, feature_name=color_feature, session=uow.session)
        await manager.create(TileSurface, name=surface, session=uow.session)
        await manager.create(Categories, name=category_name)
        await manager.create(TileSize, length=length, width=width, height=height)
        await manager.create(Producer, name=producer_name)
        await manager.create(Box, weight=box_weight, area=box_area)

