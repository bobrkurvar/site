import logging
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class Table:
    name: Any
    columns: list[str]
    rows: list[dict] | None
    unique: list[str] | None = None
    foreign_keys: list[tuple[list[str] | str, Any, list[str] | str]] | None = None
    defaults: dict[str, Any] | None = None


class FakeCrudError(Exception):

    def __init__(self, err: str):
        super().__init__()
        self.err = err

    def __str__(self):
        return self.err


class FakeStorage:

    def __init__(self):
        self.tables: dict[str, Table] = {}

    def register_tables(self, models: list[Table]):
        for model in models:
            self.tables[model.name] = model

    def _check_unique(self, table: Table, new_row: dict):
        if not table.unique:
            return
        for col in table.unique:
            value = new_row.get(col)
            if value is None:
                continue
            if any(existing.get(col) == value for existing in (table.rows or [])):
                raise FakeCrudError(
                    f"Unique constraint failed: {table.name.__name__}.{col}={value}"
                )

    def _check_row_foreign_keys(self, table: Table, new_row: dict):
        if not table.foreign_keys:
            return

        for col, parent_table_name, parent_col in table.foreign_keys:

            # нормализуем к спискам
            cols = col if isinstance(col, list) else [col]
            parent_cols = parent_col if isinstance(parent_col, list) else [parent_col]

            # заполняем значения нового ряда
            values = [new_row.get(c) for c in cols]

            # если нет всех значений — FK не активен
            if any(v is None for v in values):
                continue

            parent_table = self.tables[parent_table_name]

            # сравнение по всем ключам одновременно
            exists = any(
                all(row.get(pcol) == val for pcol, val in zip(parent_cols, values))
                for row in (parent_table.rows or [])
            )

            if not exists:
                raise FakeCrudError(
                    f"ForeignKey error: {table.name.__name__}.{cols}={values} "
                    f"does not exist in {parent_table_name.__name__}.{parent_cols}"
                )

    def add(self, model, session=None, **columns):
        table = self.tables[model]
        if table.rows is None:
            table.rows = []
        for table_column in table.columns:
            if table_column not in columns:
                columns.update({table_column: table.defaults[table_column]})

        self._check_unique(table, columns)
        self._check_row_foreign_keys(table, columns)

        table.rows.append(columns)
        return columns

    def read(self, model, session=None, **filters):
        table = self.tables[model]
        if not table.rows:
            return []

        result = []
        for row in table.rows:
            if all(row.get(k) == v for k, v in filters.items()):
                result.append(row)
        return result


class FakeCRUD:
    _session_factory = None

    def __init__(self, storage: FakeStorage):
        self.storage = storage

    async def create(self, model, **columns):
        return self.storage.add(model, **columns)

    async def read(self, model, **filters):
        return self.storage.read(model, **filters)


class FakeUoW:
    def __init__(self, *args, **kwargs):
        self.committed = False
        self.session = self  # если session нужен, но не используется

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def commit(self):
        self.committed = True
