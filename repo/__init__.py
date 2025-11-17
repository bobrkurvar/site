import domain
from core import config
from db import models
from repo.crud import Crud


def get_db_manager() -> Crud:
    db_host = config.db_url
    domain_with_orm = {
        domain.Tile: models.Catalog,
        domain.TileSize: models.TileSize,
        domain.TileColor: models.TileColor,
        domain.TileColorFeature: models.TileColorFeature,
        domain.Surface: models.Surface,
    }
    manager = Crud(db_host, domain_with_orm)

    return manager
