import logging

from domain import NotFoundError
from typing import Any
from .mapper import registry


log = logging.getLogger(__name__)


class FakeCRUD:
    def __init__(self):
        self.tables = {}
        self._session_factory = None
        self._mapper = registry

    def _new_table(self, model):
        self.tables[model] = []

    def _get_table(self, model):
        if model not in self.tables:
            self._new_table(model)
        return self.tables[model]

    def _create_one(self, domain_obj):
        table = self._get_table(type(domain_obj))
        table.append(domain_obj)
        return domain_obj

    async def create(self, domain_obj=None, seq_data=None, **kwargs):
        if seq_data:
            for obj in seq_data:
                self._create_one(obj)
        return self._create_one(domain_obj)

    async def read(self, model, **kwargs):
        ignored = {"limit", "offset", "loaded", "distinct", "session"}
        table = self._get_table(model)
        filters = {k: v for k, v in kwargs.items() if k not in ignored}
        return tuple(
            item
            for item in table
            if all(self._mapper.to_orm(item)[k] == v for k, v in filters.items())
        )

    async def read_one(self, model, **kwargs):
        record = await self.read(model, **kwargs)
        if record:
            return record[0]

    async def update(self, model, filters, **values):
        ignored = {"session"}
        values = {k: v for k, v in values.items() if k not in ignored}
        table = self._get_table(model)
        for i in range(len(table)):
            orm_obj = self._mapper.to_orm(table[i])
            if all(orm_obj[f] == v for f, v in filters.items()):
                for k, v in values.items():
                    orm_obj[k] = v
                    table[i] = self._mapper.to_domain(model, orm_obj)

    async def delete(self, model, **filters) -> tuple[Any, ...]:
        ignored = {"session"}
        filters = {k: v for k, v in filters.items() if k not in ignored}

        table = self._get_table(model)
        new_list = []
        del_res = []
        for i in range(len(table)):
            orm_obj = self._mapper.to_orm(table[i])
            if all(orm_obj[f] == v for f, v in filters.items()):
                del_res.append(self._mapper.to_domain(model, orm_obj))
            else:
                new_list.append(self._mapper.to_domain(model, orm_obj))
        if not del_res:
            raise NotFoundError(str(model))

        table[:] = new_list
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
