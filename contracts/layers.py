from enum import StrEnum


PRODUCTS = "products"
DETAILS = "details"
COLLECTIONS = "collections"
SLIDES = "slides"

LAYERS_IMAGE_FORMAT = "WEBP"
LAYERS_IMAGE_EXTENSION = f".{LAYERS_IMAGE_FORMAT.lower()}"

class ImageLayer(StrEnum):
    product = PRODUCTS
    details = DETAILS
    collections = COLLECTIONS
    slides = SLIDES