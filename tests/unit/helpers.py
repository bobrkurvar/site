def collection_catalog_path(manager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, "collections")

    return wrapper


def product_catalog_path(manager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, "products")

    return wrapper


def product_details_path(manager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, "details")

    return wrapper


