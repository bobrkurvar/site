import logging
from copy import deepcopy
from typing import Any

from domain import Box, Collections, NotFoundError, TileImages, TileSize

log = logging.getLogger(__name__)


def join_tile_with_box(new_table, other_table):
    new_table.columns += ["box_weight", "box_area"]

    for row in new_table.rows:
        to_row = {}
        for other_row in other_table.rows or []:
            if other_row["id"] == row["box_id"]:
                to_row.update(
                    {"box_area": other_row["area"], "box_weight": other_row["weight"]}
                )
        row.update(to_row)


def join_tile_with_size(new_table, other_table):
    new_table.columns += ["size_length", "size_width", "size_height"]

    for row in new_table.rows:
        to_row = {}
        for other_row in other_table.rows or []:
            if other_row["id"] == row["size_id"]:
                to_row.update(
                    {
                        "size_length": other_row["length"],
                        "size_width": other_row["width"],
                        "size_height": other_row["height"],
                    }
                )
        row.update(to_row)


def join_tile_with_images(new_table, other_table):
    new_table.columns += ["images_paths"]

    for row in new_table.rows:
        images = [
            other_row["image_path"]
            for other_row in (other_table.rows or [])
            if other_row["tile_id"] == row["id"]
        ]

        if images:
            row["images_paths"] = images


def join_category_collection_with_collection(new_table, other_table):
    new_table.columns += ["collection_name", "image_path"]
    for row in new_table.rows:
        to_row = {}
        for other_row in other_table:
            to_row.update(
                collection_name=other_row["collection_name"],
                image_path=other_row["image_path"],
            )
        row.update(to_row)


class Table:

    def __init__(
        self,
        name,
        columns: list[str],
        rows: list[dict] | None = None,
        defaults: dict[str, Any] | None = None,
    ):
        self.name = name
        self.columns = columns
        self.rows = rows if rows else []
        self.defaults = defaults

    def __add__(self, other):
        new_table = Table(
            name=self.name,
            columns=self.columns.copy(),
            rows=deepcopy(self.rows),
            defaults=self.defaults,
        )
        if other.name is Box:
            join_tile_with_box(new_table, other)
        elif other.name is TileSize:
            join_tile_with_size(new_table, other)
        elif other.name is TileImages:
            join_tile_with_images(new_table, other)
        elif other.name is Collections:
            join_category_collection_with_collection(new_table, other)

        return new_table


class FakeStorage:

    def __init__(self):
        self.tables: dict[Any, Table] = {}
        self.to_join = {
            "size": TileSize,
            "box": Box,
            "images": TileImages,
            "collection": Collections,
        }

    def register_tables(self, models: list[Table]):
        for model in models:
            self.tables[model.name] = model

    @staticmethod
    def _add_default(table_column, table, columns):
        columns.update(
            {table_column: (table.defaults[table_column] if table.defaults else None)}
        )
        if isinstance(table.defaults[table_column], int):
            table.defaults[table_column] += 1

    def add(self, model, **columns):
        table = self.tables[model]
        for table_column in table.columns:
            if table_column not in columns:
                self._add_default(table_column, table, columns)
        table.rows.append(columns)
        return columns

    def read(
        self, model, to_join=None, distinct=None, limit=None, offset=None, **filters
    ):
        table = self.tables[model]
        if not table.rows:
            return []

        result = []
        if to_join:
            for t in to_join:
                t = self.to_join.get(t, t)
                t = self.tables[t]
                table = table + t

        for row in table.rows:
            if all(row.get(k) == v for k, v in filters.items()):
                result.append(row)

        if distinct:
            if isinstance(distinct, str):
                distinct = (distinct,)
            seen = set()
            unique_result = []
            for row in result:
                key = tuple(row.get(f) for f in distinct)
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
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                for k, v in values.items():
                    table.rows[i][k] = v

    def delete(self, model, **filters):
        table = self.tables[model]
        del_res = []
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                del_res.append(table.rows[i])
                del table.rows[i]
        if not del_res:
            raise NotFoundError(model, **filters)
        return del_res


class FakeCRUD:
    _session_factory = None

    def __init__(self, storage: FakeStorage):
        self.storage = storage

    async def create(self, model, session=None, **columns):
        return self.storage.add(model, **columns)

    async def read(
        self,
        model,
        session=None,
        to_join=None,
        distinct=None,
        limit=None,
        offset=None,
        **filters,
    ):
        return self.storage.read(
            model,
            to_join=to_join,
            distinct=distinct,
            limit=limit,
            offset=offset,
            **filters,
        )

    async def update(self, model, filters: dict, session=None, **values):
        return self.storage.update(model, filters, **values)

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
