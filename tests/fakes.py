class FakeStorage:
    """
    Простая in-memory "БД".
    Хранит таблицы в словарях.
    """

    def __init__(self):
        self.tables = {}

    def register_table(self, model):
        self.tables[model] = {}


class FakeCrudError(Exception):

    def __init__(self, err: str):
        super().__init__()
        self.err = err

    def __str__(self):
        return self.err


class FakeCRUD:
    def __init__(self, storage, model, *, unique_fields=None, foreign_keys=None):
        """
        unique_fields = ['name', 'code']
        foreign_keys = {'color_id': TileColor}
        """
        self.storage = storage
        self.model = model
        self.unique_fields = unique_fields or []
        self.foreign_keys = foreign_keys or {}
        storage.register_table(model)

    def create(self, obj):
        table = self.storage.tables[self.model]

        # UNIQUE CHECK
        for record in table.values():
            for field in self.unique_fields:
                if getattr(record, field) == getattr(obj, field):
                    raise FakeCrudError(f"{self.model.__name__}: unique field {field}")

        # FOREIGN KEY CHECK
        for field, fk_model in self.foreign_keys.items():
            fk_value = getattr(obj, field)
            fk_table = self.storage.tables[fk_model]
            if fk_value not in fk_table:
                raise FakeCrudError(f"FK {field}={fk_value} not in {fk_model.__name__}")

        table[obj.id] = obj
        return obj

    def read_all(self):
        return list(self.storage.tables[self.model].values())

    def read_one(self, obj_id):
        try:
            return self.storage.tables[self.model][obj_id]
        except KeyError:
            raise FakeCrudError(f"{self.model.__name__} with id={obj_id} not found")

    def delete(self, obj_id):
        if obj_id not in self.storage.tables[self.model]:
            raise FakeCrudError(f"{self.model.__name__} with id={obj_id} not found")
        del self.storage.tables[self.model][obj_id]


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
