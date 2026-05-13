from decimal import Decimal


class TileSize:
    def __init__(self, width: Decimal, length: Decimal, height: Decimal, size_id: int | None = None):
        self.id = size_id
        self.height = height
        self.width = width
        self.length = length

    def __str__(self):
        return f"{self.format_decimal(self.length)}×{self.format_decimal(self.width)}×{self.format_decimal(self.height)}"

    @staticmethod
    def format_decimal(value: Decimal) -> str:
        as_float = float(value)
        if as_float.is_integer():
            return str(int(as_float))
        return f"{as_float:g}"


class TileColor:
    def __init__(self, color_name: str, feature_name: str = ""):
        self.color_name = color_name.strip()
        self.feature_name = feature_name

    def __str__(self):
        return f"{self.color_name} {self.feature_name}"


class TileSurface:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class Producer:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f"{self.name}"


class Box:

    def __init__(self, weight: Decimal, area: Decimal, box_id: int | None = None):
        self.id = box_id
        self.weight = weight
        self.area = area

    def __str__(self):
        return str(self.weight.normalize())


class Category:

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name



class Tile:
    def __init__(
        self,
        size: TileSize,
        color: TileColor,
        name: str,
        box: Box,
        boxes_count: int,
        producer: Producer,
        category: Category,
        images: list["TileImage"] | list[bytes] = None,
        article: int | None = None,
        surface: TileSurface | None = None,
    ):
        self.id = article
        self.article = article
        self.name = name
        self.color = color
        self.size = size
        self.surface = surface
        self.box = box
        self.boxes_count = boxes_count
        self.producer = producer
        self.category = category
        self.images = images

    @property
    def present(self):
        return (
            f"{self.category} {self.name} {self.size} {self.color} {self.surface or ''}"
        )

    def __str__(self):
        return f"{self.article} {str(self.color)} {self.surface} {self.name}"

    def to_dict(self):
        return {
            "id": self.article,
            "name": self.name,
            "boxes_count": self.boxes_count,
            "category_name": self.category.name,
            "producer_name": self.producer.name,
            "surface_name": self.surface.name if self.surface else None,
            "size_length": self.size.length,
            "size_width": self.size.width,
            "size_height": self.size.height,
            "size_id": self.size.id,
            "box_area": self.box.area,
            "box_weight": self.box.weight,
            "box_id": self.box.id,
            "color_name": self.color.color_name,
            "feature_name": self.color.feature_name
        }



class TileImage:

    def __init__(self, image: bytes | None = None, image_path: str | None = None, tile_id: int | None = None, image_id: int | None = None):
        self.id = image_id
        self.tile_id = tile_id
        self.image = image
        self.image_path = image_path


class Collection:
    def __init__(
        self,
        name: str,
        image_bytes: bytes | None = None,
        image_path: str | None = None,
        categories: list[Category] | Category | None = None,
        collection_id: int | None = None
    ):
        self.id = collection_id
        self.name = name.strip()
        self.image_path = image_path
        self.image_bytes = image_bytes

        if isinstance(categories, list):
            self.categories = categories
        elif categories:
            self.categories = [categories]
        else:
            self.categories = []



class CollectionCategory:
    def __init__(self, collection_id: int, category_name: str):
        self.collection_id = collection_id
        self.category_name = category_name

