from domain import (Admin, Box, Categories, CollectionCategory, Collections,
                    Producer, Slug, Tile, TileColor, TileImages, TileSize,
                    TileSurface)


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
        Categories: ("name",),
        TileImages: ("image_id", "tile_id", "image_path"),
        Collections: ("id", "name", "image_path"),
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
