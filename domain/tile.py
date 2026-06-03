from decimal import Decimal


class TileSize:
    def __init__(
        self,
        width: Decimal | int,
        length: Decimal | int,
        height: Decimal | int,
        size_id: int | None = None,
    ):
        self.id = size_id
        self.height = Decimal(height)
        self.width = Decimal(width)
        self.length = Decimal(length)

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

    def __init__(
        self, weight: Decimal | int, area: Decimal | int, box_id: int | None = None
    ):
        self.id = box_id
        self.weight = Decimal(weight)
        self.area = Decimal(area)

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
        color: TileColor,
        name: str,
        boxes_count: int,
        producer: Producer,
        category: Category,
        size: TileSize | None = None,
        size_id: int | None = None,
        box: Box | None = None,
        box_id: int | None = None,
        images: list["Image"] = None,
        # images_bytes: list[bytes] = None,
        article: int | None = None,
        surface: TileSurface | None = None,
    ):
        self.id = article
        self.article = article
        self.name = name
        self.color = color
        self.surface = surface
        self.size = size
        # на случай если не подгружены все данные о size
        self.size_id = size.id if size else size_id
        self.box = box
        # на случай если не подгружены все данные о box
        self.box_id = box.id if box else box_id
        self.boxes_count = boxes_count
        # self._images_bytes = images_bytes

        self.producer = producer
        self.category = category
        # Первый элемент в images - main image
        self._images = images

        if self.size is None and self.size_id is None:
            raise ValueError(
                "Плитка не может существовать без размера (size или size_id)"
            )

        if self.box is None and self.box_id is None:
            raise ValueError(
                "Плитка не может существовать без коробки (box или box_id)"
            )

    def __str__(self):
        return f"{self.article} {str(self.color)} {self.surface} {self.name}"

    @property
    def images(self) -> list["Image"]:
        if self._images is None:
            raise ValueError("images не заданы!")
        return self._images

    @property
    def present(self):
        return (
            f"{self.category} {self.name} {self.size} {self.color} {self.surface or ''}"
        )

    @property
    def producer_name(self):
        return self.producer.name

    @property
    def category_name(self):
        return self.category.name

    @property
    def surface_name(self):
        return self.surface.name

    @property
    def color_name(self):
        return self.color.color_name

    @property
    def feature_name(self):
        return self.color.feature_name

    @property
    def size_height(self):
        if not self.size:
            raise ValueError("Size нет")
        return self.size.height

    @property
    def size_width(self):
        if not self.size:
            raise ValueError("Size нет")
        return self.size.width

    @property
    def size_length(self):
        if not self.size:
            raise ValueError("Size нет")
        return self.size.length


# class TileImage:
#     def __init__(
#         self,
#         image_bytes: bytes | None = None,
#         image_path: str | None = None,
#         tile_id: int | None = None,
#         image_id: int | None = None,
#     ):
#         if not image_bytes and not image_path:
#             raise ValueError("Изображение плитки должно содержать либо байты, либо путь")
#
#         self.id = image_id
#         self.tile_id = tile_id
#         self.image_bytes = image_bytes
#         self.image_path = image_path
#
#     def consume_bytes(self) -> bytes:
#         if self.image_bytes is None:
#             raise ValueError("Байты уже были потреблены или не заданы")
#
#         data = self.image_bytes
#         self.image_bytes = None
#         return data
class Image:
    def __init__(
        self,
        image_bytes: bytes | None = None,
        image_path: str | None = None,
        master_id: int | None = None,
        image_id: int | None = None,
    ):
        if not image_bytes and not image_path:
            raise ValueError("Изображение должно содержать либо байты, либо путь")

        self.id = image_id
        self.master_id = master_id
        self.image_bytes = image_bytes
        self.image_path = image_path

    def consume_bytes(self) -> bytes:
        if self.image_bytes is None:
            raise ValueError("Байты уже были потреблены или не заданы")

        data = self.image_bytes
        self.image_bytes = None
        return data


class Collection:
    def __init__(
        self,
        name: str,
        # image_bytes: bytes | None = None,
        # image_path: str | None = None,
        image: Image,
        categories: list[Category] | Category | None = None,
        collection_id: int | None = None,
        slug: str | None = None,
    ):
        # if not image_path and not image_bytes:
        #     raise ValueError(f"Коллекция '{name}' не может существовать без изображения")
        self.id = collection_id
        self.name = name.strip()
        # self.image_path = image_path
        # self.image_bytes = image_bytes
        self.image = image
        self.slug = slug

        if isinstance(categories, list):
            self.categories = categories
        elif categories:
            self.categories = [categories]
        else:
            self.categories = []

    def assign_image_path(self, path: str):
        self.image = Image(
            image_bytes=self.image.image_bytes,
            image_path=path,
        )

    @property
    def image_path(self):
        return self.image.image_path

    def merge_categories(self, new_categories: list[Category]):
        existing_names = {cat.name for cat in self.categories}
        unique_new = [cat for cat in new_categories if cat.name not in existing_names]
        self.categories.extend(unique_new)


class CollectionCategory:
    def __init__(self, collection_id: int, category_name: str):
        self.collection_id = collection_id
        self.category_name = category_name
