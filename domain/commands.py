import abc
from domain import TileColor, TileSize, TileSurface, Producer, Box, Category

class UpdateCommand(abc.ABC):
    def __init__(self, model, relation_name, output_map, **fields):
        self.model = model
        self.relation_name = relation_name  # Имя связи для join ("size", "color")
        self.output_map = output_map        # {колонка_в_tile: атрибут_в_новой_модели}
        self.fields = fields

    def need_update(self):
        return any(v is not None for v in self.fields.values())

    def need_read(self):
        return len(self.fields) > 1 and any(v is None for v in self.fields.values())

    @property
    def field_to_read(self):
        return [k for k, v in self.fields.items() if v is None]

    def filters(self):
        return {k: v for k, v in self.fields.items() if v is not None}

    @abc.abstractmethod
    def tile_map(self, field):
        pass

    def set_fields(self, tile_flat_dict):
        for field in self.field_to_read:
            flat_key = self.tile_map(field)
            self.fields[field] = tile_flat_dict.get(flat_key)

    def domain_model(self):
        return self.model(**self.fields)


class ColorUpdate(UpdateCommand):
    def __init__(self, color_name=None, feature_name=None):
        super().__init__(
            model=TileColor,
            relation_name="color",
            output_map={"color_name": "color_name", "feature_name": "feature_name"},
            color_name=color_name,
            feature_name=feature_name
        )

    def tile_map(self, field):
        return field # В to_dict ключи совпадают


class SizeUpdate(UpdateCommand):
    def __init__(self, length=None, width=None, height=None):
        super().__init__(
            model=TileSize,
            relation_name="size",
            output_map={"size_id": "id"}, # Берем "id" из TileSize, кладем в "size_id"
            length=length,
            width=width,
            height=height
        )

    def tile_map(self, field):
        return f"size_{field}" # length -> size_length


class BoxUpdate(UpdateCommand):
    def __init__(self, area=None, weight=None):
        super().__init__(
            model=Box,
            relation_name="box",
            output_map={"box_id": "id"},
            area=area,
            weight=weight
        )

    def tile_map(self, field):
        return f"box_{field}"


class CategoryUpdate(UpdateCommand):
    def __init__(self, name=None):
        super().__init__(
            model=Category,
            relation_name="category",
            output_map={"category_name": "name"},
            name=name
        )

    def tile_map(self, field):
        return "category_name"


class SurfaceUpdate(UpdateCommand):
    def __init__(self, name=None):
        super().__init__(
            model=TileSurface,
            relation_name="surface",
            output_map={"surface_name": "name"},
            name=name
        )

    def tile_map(self, field):
        return "surface_name"


class ProducerUpdate(UpdateCommand):
    def __init__(self, name=None):
        super().__init__(
            model=Producer,
            relation_name="producer",
            output_map={"producer_name": "name"},
            name=name
        )

    def tile_map(self, field):
        return "producer_name"