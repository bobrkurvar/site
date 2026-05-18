from shared import COLLECTIONS, PRODUCTS, DETAILS

def collection_catalog_path(manager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, COLLECTIONS)

    return wrapper


def product_catalog_path(manager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, PRODUCTS)

    return wrapper


def product_details_path(manager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, DETAILS)

    return wrapper
