import logging

from domain import Box, Collections, NotFoundError, TileImages, TileSize
from infrastructure.orm_mapper import DomainToOrmMapper


log = logging.getLogger(__name__)




class Table:

    def __init__(
        self,
        columns: list[str],
        rows: list[dict] | None = None,
        default_num: int = 0
    ):
        self.default_num = default_num
        self.columns = set(columns)
        self.rows = rows if rows else []

    def add_row(self, **row):
        for i in self.columns - row.keys():
            #log.debug("III: %s = %s", i, self.default_num)
            row[i] = self.default_num
            self.default_num += 1
        #log.debug("row after default: %s", row)
        self.rows.append(row)
        return row


class FakeCRUD:
    def __init__(self):
        self.tables = {}
        self._session_factory = None

    def _new_table(self, model):
        self.tables[model] = Table(DomainToOrmMapper.fields(model))

    def _get_table(self, model):
        if model not in self.tables:
            self._new_table(model)
        return self.tables[model]

    async def create(self, model, **row):
        ignored = {"session", "seq_data"}
        row = {k: v for k, v in row.items() if k not in ignored}
        log.debug("FAKE CREATE MODEL: %s", model)
        table = self._get_table(model)
        res = table.add_row(**row)
        #log.debug("create res: %s", res)
        return res

    async def read(self, model, **kwargs):
        ignored = {"limit", "offset", "loaded", "distinct", "session"}
        table = self._get_table(model)
        filters = {k: v for k, v in kwargs.items() if k not in ignored}
        return tuple(
            r for r in table.rows if all(r.get(k) == v for k, v in filters.items())
        )

    async def update(self, model, filters, **values):
        ignored = {"session"}
        log.debug("UPDATE FILTERS: %s", filters)
        values = {k: v for k, v in values.items() if k not in ignored}
        table = self._get_table(model)
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                for k, v in values.items():
                    log.debug("column %s :: new value %s", k, v)
                    table.rows[i][k] = v

    async def delete(self, model, **filters) -> tuple[dict, ...]:
        ignored = {"session"}
        filters = {k: v for k, v in filters.items() if k not in ignored}

        table = self._get_table(model)
        del_res = []
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                del_res.append(table.rows[i])
                del table.rows[i]
        if not del_res:
            raise NotFoundError(model, **filters)
        return tuple(del_res)


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
