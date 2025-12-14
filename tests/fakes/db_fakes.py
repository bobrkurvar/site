import logging
from dataclasses import dataclass
from typing import Any

from domain import Box, TileSize, TileImages

log = logging.getLogger(__name__)


@dataclass
class Table:
    name: Any
    columns: list[str]
    rows: list[dict] | None
    unique: list[str] | None = None
    foreign_keys: dict | None = None
    defaults: dict[str, Any] | None = None

    def __iadd__(self, other):
        son_parent = self.foreign_keys.get(other.name, None)
        if son_parent and other:
            if other.name is Box:
                self.columns += ["box_weight", "box_area"]
                for i in range(len(self.rows)):
                    to_row = {}
                    for row in other.rows:
                        if row[son_parent["box_id"]] == self.rows[i]["box_id"] and (
                            "weight" in row.keys() or "area" in row.keys()
                        ):
                            to_row.update(
                                {"box_area": row["area"], "box_weight": row["weight"]}
                            )

                    self.rows[i].update(to_row)

            elif other.name is TileSize:
                self.columns += ["size_length", "size_width", "size_height"]
                for i in range(len(self.rows)):
                    to_row = {}
                    for row in other.rows:
                        if row[son_parent["size_id"]] == self.rows[i]["size_id"] and (
                            "length" in row.keys()
                            or "width" in row.keys()
                            or "height" in row.keys()
                        ):
                            to_row.update(
                                {
                                    "size_length": row["length"],
                                    "size_width": row["width"],
                                    "size_height": row["height"],
                                }
                            )

                    self.rows[i].update(to_row)

            elif other.name is TileImages:
                self.columns += ["image_path"]
                for i in range(len(self.rows)):
                    to_row = {}
                    for row in other.rows:
                        if row["tile_id"] == self.rows[i]["id"] and (
                                "image_path" in row.keys()
                        ):
                            to_row.update({"image_path": row["image_path"]})

                    self.rows[i].update(to_row)

        return self


class FakeCrudError(Exception):

    def __init__(self, err: str):
        super().__init__()
        self.err = err

    def __str__(self):
        return self.err


class FakeStorage:

    def __init__(self):
        self.tables: dict[str, Table] = {}
        self.to_join = {
            "size": TileSize,
            "box": Box,
            "images": TileImages,
        }

    def register_tables(self, models: list[Table]):
        for model in models:
            self.tables[model.name] = model
        # log.debug("tables: %s", self.tables)

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

        for parent_table_name, parent_son_cols in table.foreign_keys.items():

            ((col, parent_col),) = parent_son_cols.items()

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
                columns.update(
                    {
                        table_column: (
                            table.defaults[table_column] if table.defaults else None
                        )
                    }
                )

        self._check_unique(table, columns)
        self._check_row_foreign_keys(table, columns)

        table.rows.append(columns)
        return columns

    def read(self, model, session=None, to_join=None, **filters):
        table = self.tables[model]
        if not table.rows:
            return []
        # log.info("model: %s table: %s", model.__name__, table)

        result = []
        # log.debug("to_join: %s", to_join)
        if to_join:
            for t in to_join:
                t = self.to_join.get(t, t)
                t = self.tables[t]
                table += t
        # log.debug("table columns: %s, table rows: %s", table.columns, table.rows)

        for row in table.rows:
            if all(row.get(k) == v for k, v in filters.items()):
                result.append(row)
        return result

    def update(self, model, filters, **values):
        table = self.tables[model]
        log.debug("UPDATE TABLE %s FILTERS: %s, VALUES: %s", model, filters, values)
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                for k, v in values.items():
                    table.rows[i][k] = v


class FakeCRUD:
    _session_factory = None

    def __init__(self, storage: FakeStorage):
        self.storage = storage

    async def create(self, model, **columns):
        return self.storage.add(model, **columns)

    async def read(self, model, **filters):
        return self.storage.read(model, **filters)

    async def update(self, model, filters: dict, session=None, **values):
        return self.storage.update(model, filters, **values)


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
