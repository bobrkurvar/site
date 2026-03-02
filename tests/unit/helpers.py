from tests.fakes import FakeFileManager
from datetime import timedelta
from services.auth import create_access_token, create_refresh_token


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


def get_tokens(
    access_data: dict | None = None,
    refresh_data: dict | None = None,
    time_life: timedelta | None = None,
):
    access_data = {} if access_data is None else access_data
    access_token = create_access_token(access_data, time_life)
    refresh_data = {} if refresh_data is None else refresh_data
    refresh_token = create_refresh_token(refresh_data, time_life)
    return access_token, refresh_token
