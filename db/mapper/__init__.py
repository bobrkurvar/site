from .collection import *
from .tile import *
from .user import *


class MapperRegistry:
    def __init__(self):
        self._models = {}  # domain_cls -> orm_model
        self._to_orm_funcs = {}  # domain_cls -> func
        self._to_domain_funcs = {}  # orm_model -> func (Внимание: ключ - ORM класс!)

    def register(self, domain_cls, orm_model, to_orm, to_domain):
        self._models[domain_cls] = orm_model
        self._to_orm_funcs[domain_cls] = to_orm
        self._to_domain_funcs[orm_model] = to_domain

    def get_model(self, domain_cls):
        return self._models[domain_cls]

    def to_orm(self, domain_obj):
        domain_cls = type(domain_obj)
        func = self._to_orm_funcs.get(domain_cls)
        if not func:
            raise RuntimeError(f"Маппер в ORM не найден для {domain_cls}")
        return func(domain_obj)

    def to_domain(self, orm_obj):
        orm_cls = type(orm_obj)
        func = self._to_domain_funcs.get(orm_cls)
        if not func:
            raise RuntimeError(f"Маппер в Домен не найден для {orm_cls}")
        return func(orm_obj)


registry = MapperRegistry()
registry.register(domain.Tile, models.Tile, map_tile_to_orm, map_tile_to_domain)
registry.register(
    domain.Category, models.Category, map_category_to_orm, map_category_to_domain
)
registry.register(
    domain.Collection,
    models.Collection,
    map_collection_to_orm,
    map_collection_to_domain,
)
registry.register(domain.Size, models.TileSize, map_size_to_orm, map_size_to_domain)
registry.register(domain.Color, models.TileColor, map_color_to_orm, map_color_to_domain)
registry.register(
    domain.Surface, models.TileSurface, map_surface_to_orm, map_surface_to_domain
)
registry.register(
    domain.Producer, models.Producer, map_producer_to_orm, map_producer_to_domain
)
registry.register(domain.Box, models.Box, map_box_to_orm, map_box_to_domain)
registry.register(
    domain.Image, models.TileImage, map_tile_image_to_orm, map_tile_image_to_domain
)
registry.register(domain.Admin, models.Admin, map_admin_to_orm, map_admin_to_domain)
