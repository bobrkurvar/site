from domain import (
    Admin,
    Box,
    Category,
    CollectionCategory,
    Collection,
    Producer,
    Slug,
    Tile,
    TileColor,
    TileImage,
    TileSize,
    TileSurface,
)


class DomainToOrmMapper:
    domain_model_to_orm_fields_mapper = {
        Tile: (
            "id",
            "name",
            "box_id",
            "color_name",
            "feature_name",
            "surface_name",
            "producer_name",
            "boxes_count",
            "category_name",
            "size_id",
        ),
        Category: ("name",),
        TileImage: ("image_id", "tile_id", "image_path"),
        Collection: ("id", "name", "image_path"),
        CollectionCategory: (
            "collection_id",
            "collection_name",
            "category_name",
            "image_path",
        ),
        TileSize: ("id", "length", "width", "height"),
        TileColor: ("color_name", "feature_name"),
        TileSurface: ("name",),
        Producer: ("name",),
        Box: ("id", "weight", "area"),
        Admin: ("username", "password"),
        Slug: ("name", "slug"),
    }

    @classmethod
    def fields(cls, domain_model):
        return cls.domain_model_to_orm_fields_mapper[domain_model]



