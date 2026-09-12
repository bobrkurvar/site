import domain
from db import models
from sqlalchemy import inspect


def map_collection_to_domain(o: models.Collection) -> domain.Collection:
    insp = inspect(o)
    categories = None
    if "categories" not in insp.unloaded:
        categories = [
            domain.Category(name=link.category.name, id=link.category_id)
            for link in o.categories
        ]

    return domain.Collection(
        collection_id=o.id,
        name=o.name,
        image=domain.Image(image_path=o.image_path),
        categories=categories,
    )


def map_collection_to_orm(d: domain.Collection) -> models.Collection:
    return models.Collection(
        id=d.id,
        name=d.name,
        image_path=d.image.image_path,
        # Маппер сливает строки в прокси
        categories_proxy=[c.id for c in d.categories],
    )


def map_collection_category_to_domain(
    o: models.CollectionCategory,
) -> domain.CollectionCategory:
    return domain.CollectionCategory(
        collection_id=o.collection_id, category_id=o.category_id
    )


def map_collection_category_to_orm(
    d: domain.CollectionCategory,
) -> models.CollectionCategory:
    return models.CollectionCategory(
        collection_id=d.collection_id, category_id=d.category_id
    )
