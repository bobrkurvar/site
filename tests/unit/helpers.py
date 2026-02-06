from tests.fakes import FakeFileManager


def collection_catalog_path(manager: FakeFileManager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, "collections")
    return wrapper

def product_catalog_path(manager: FakeFileManager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, "products")
    return wrapper

def product_details_path(manager: FakeFileManager):
    def wrapper(file_name):
        return manager.resolve_path(file_name, "details")
    return wrapper