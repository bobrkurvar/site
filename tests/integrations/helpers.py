
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


