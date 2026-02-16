from typing import Protocol


class CrudPort(Protocol):
    async def create(
        self, domain_model, seq_data: list | None = None, session=None, **kwargs
    ): pass
    async def delete(self, domain_model, session=None, **filters): pass
    async def update(self, domain_model, filters: dict, session=None, **values): pass
    async def read(
        self,
        domain_model,
        session=None,
        to_join=None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        distinct: str | None = None,
        **filters
    ): pass
