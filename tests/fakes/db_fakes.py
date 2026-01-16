import logging
from dataclasses import dataclass
from typing import Any
from copy import deepcopy

from domain import Box, TileImages, TileSize

log = logging.getLogger(__name__)


@dataclass
class Table:
    name: Any
    columns: list[str]
    rows: list[dict] | None
    unique: list[str] | None = None
    foreign_keys: dict | None = None
    defaults: dict[str, Any] | None = None

    def __add__(self, other):
        son_parent = self.foreign_keys.get(other.name, None) or other.foreign_keys.get(self.name, None)
        if not son_parent or not other or not self.rows:
            return self

        # создаём новую таблицу
        new_table = Table(
            name=self.name,
            columns=self.columns.copy(),
            rows=deepcopy(self.rows),
            unique=self.unique,
            foreign_keys=self.foreign_keys,
            defaults=self.defaults,
        )

        if other.name is Box:
            new_table.columns += ["box_weight", "box_area"]

            for i in range(len(new_table.rows)):
                to_row = {}
                for row in other.rows or []:
                    if row[son_parent["box_id"]] == new_table.rows[i]["box_id"] and (
                            "weight" in row or "area" in row
                    ):
                        to_row.update(
                            {"box_area": row["area"], "box_weight": row["weight"]}
                        )
                new_table.rows[i].update(to_row)

        elif other.name is TileSize:
            new_table.columns += ["size_length", "size_width", "size_height"]

            for i in range(len(new_table.rows)):
                to_row = {}
                for row in other.rows or []:
                    if row[son_parent["size_id"]] == new_table.rows[i]["size_id"] and (
                            "length" in row or "width" in row or "height" in row
                    ):
                        to_row.update(
                            {
                                "size_length": row["length"],
                                "size_width": row["width"],
                                "size_height": row["height"],
                            }
                        )
                new_table.rows[i].update(to_row)

        elif other.name is TileImages:
            new_table.columns += ["images_paths"]

            for i in range(len(new_table.rows)):
                images = [
                    row["image_path"]
                    for row in (other.rows or [])
                    if row["tile_id"] == new_table.rows[i]["id"]
                       and "image_path" in row
                ]

                if images:
                    new_table.rows[i]["images_paths"] = images
        return new_table

class FakeCrudError(Exception):

    def __init__(self, err: str):
        super().__init__()
        self.err = err

    def __str__(self):
        return self.err


class FakeStorage:

    def __init__(self):
        self.tables: dict[Any, Table] = {}
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
                if isinstance(table.defaults[table_column], int):
                    table.defaults[table_column] += 1

        self._check_unique(table, columns)
        self._check_row_foreign_keys(table, columns)

        table.rows.append(columns)
        return columns

    def read(self, model, to_join=None, distinct = None, limit=None, offset=None, **filters):
        table = self.tables[model]
        if not table.rows:
            return []

        result = []
        if to_join:
            for t in to_join:
                log.debug("FAKE JOIN %s", t)
                t = self.to_join.get(t, t)
                t = self.tables[t]
                table = table + t

        for row in table.rows:
            if all(row.get(k) == v for k, v in filters.items()):
                result.append(row)

        if distinct:
            if isinstance(distinct, str):
                distinct = [distinct]
            seen = set()
            unique_result = []
            for row in result:
                key = tuple(row.get(f) for f in distinct)
                log.debug("DISTINCT: %s", key)
                if key not in seen:
                    seen.add(key)
                    unique_result.append(row)
            result = unique_result

        if offset:
            result = result[offset:]
        if limit:
            result = result[:limit]

        return result

    def update(self, model, filters, **values):
        table = self.tables[model]
        log.debug("UPDATE TABLE %s FILTERS: %s, VALUES: %s", model, filters, values)
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                for k, v in values.items():
                    table.rows[i][k] = v

    def delete(self, model, **filters):
        table = self.tables[model]
        del_res = []
        log.debug("DELETE TABLE %s FILTERS: %s", model, filters)
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                del_res.append(table.rows[i])
                del table.rows[i]
        return del_res


class FakeCRUD:
    _session_factory = None

    def __init__(self, storage: FakeStorage):
        self.storage = storage

    async def create(self, model, session = None, **columns):
        return self.storage.add(model, **columns)

    async def read(self, model, session = None, to_join = None, distinct = None, limit = None, offset=None, **filters):
        return self.storage.read(model, to_join=to_join, distinct=distinct, limit=limit, offset=offset, **filters)

    async def update(self, model, filters: dict, session=None, **values):
        return self.storage.update(model, filters,  **values)

    async def delete(self, model, session=None, **filters):
        return self.storage.delete(model, **filters)


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
