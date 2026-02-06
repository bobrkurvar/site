def _iter_files(file_manager, layer: str, names=None):
    path = file_manager.resolve_path(layer=layer)
    if not path.exists():
        return []
    return [f for f in path.iterdir() if f.is_file() and f.name in names] if names else [f for f in path.iterdir() if
                                                                                         f.is_file()]

def count_by_layer(file_manager, layer: str, names: str | None = None) -> int:
    return len(_iter_files(file_manager, layer, names))


def slides_files_count(file_manager) -> int:
    return count_by_layer(file_manager, "original_slide") + count_by_layer(file_manager, "slides")


def collection_files_count(file_manager, names=None) -> int:
    return count_by_layer(file_manager, names=names, layer="original_collection") + count_by_layer(file_manager, names=names,
                                                                                               layer="collections")

def product_files_count(file_manager, names = None) -> int:
    return (
            count_by_layer(file_manager, names=names, layer="original_product")
            + count_by_layer(file_manager, names=names, layer="products")
            + count_by_layer(file_manager, names=names, layer="details")
    )