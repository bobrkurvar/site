class FakeStorage:
    """
    Простая in-memory "БД".
    Хранит таблицы в словарях.
    """

    def __init__(self):
        self.tables = {}

    def register_tables(self, *models):
        for model in models:
            self.tables[model] = {}


class FakeCrudError(Exception):

    def __init__(self, err: str):
        super().__init__()
        self.err = err

    def __str__(self):
        return self.err


class FakeCRUD:
    def __init__(self, storage, *, unique_fields=None, foreign_keys=None):
        """
        unique_fields = ['name', 'code']
        foreign_keys = {'color_id': TileColor}
        """
        self.storage = storage
        self.unique_fields = unique_fields or []
        self.foreign_keys = foreign_keys or {}

    async def create(self, model, obj):
        table = self.storage.tables[model]

        # UNIQUE CHECK
        for record in table.values():
            for field in self.unique_fields:
                if getattr(record, field) == getattr(obj, field):
                    raise FakeCrudError(f"{model.__name__}: unique field {field}")

        # FOREIGN KEY CHECK
        for field, fk_model in self.foreign_keys.items():
            fk_value = getattr(obj, field)
            fk_table = self.storage.tables[fk_model]
            if fk_value not in fk_table:
                raise FakeCrudError(f"FK {field}={fk_value} not in {fk_model.__name__}")

        table[obj.id] = obj
        return obj

    async def read(self, model, **filters):
        table = self.storage.tables[model]
        return [{k: table.get(k, None)} for k in filters if table.get(k, None) == filters[k]]

    async def delete(self, model, **filters):
        table = self.storage.tables[model]
        for_delete = [{k: table.get(k, None)} for k in filters if table.get(k, None) == filters[k]]
        if not for_delete:
            raise FakeCrudError(f"{model.__name__} with filters={filters} not found")
        # del self.storage.tables[model][obj_id]


class FakeUoW:
    def __init__(self):
        self.committed = False
        self.storage = FakeStorage()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            return False  # не подавлять ошибки

    async def commit(self):
        self.committed = True
