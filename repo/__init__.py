from repo.crud import Crud
from db import models
import domain
from core import config

def get_db_manager() -> Crud:
    db_host = config.db_url
    domain_with_orm = {domain.Tile: models.Catalog, domain.TileSize: models.TileSize, domain.TileColor: models.TileColor}
    manager = Crud(db_host, domain_with_orm)

    return manager