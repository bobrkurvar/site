import logging
from pathlib import Path
from .http_client import http_client


log = logging.getLogger(__name__)



async def get_image_path(my_path: str, *directories):
    if directories:
        root = Path("static/images")
        my_path_name = Path(my_path).name
        for directory in directories:
            root /= directory
        root /= my_path_name
        str_path = str(root)
        if root.exists():
            log.debug("Path: %s", str_path)
            return str_path
    return my_path

async def generate_image_products_catalog_and_details(input_path):
    input_path = str(input_path) if not isinstance(input_path, str) else input_path
    return await http_client.generate_products_images(input_path=input_path, targets=("products", "details"))

async def generate_image_collections_catalog(input_path):
    input_path = str(input_path) if not isinstance(input_path, str) else input_path
    return await http_client.generate_products_images(input_path=input_path, targets=("collections",))

async def generate_slides(input_path):
    input_path = str(input_path) if not isinstance(input_path, str) else input_path
    return await http_client.generate_products_images(input_path=input_path, targets=("slides",))

