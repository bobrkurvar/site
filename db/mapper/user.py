import domain
from db import models



def map_admin_to_domain(o: models.Admin) -> domain.Admin:
    return domain.Admin(username=o.username, password=o.password)

def map_admin_to_orm(o: domain.Admin) -> models.Admin:
    return models.Admin(username=o.username, password=o.password)