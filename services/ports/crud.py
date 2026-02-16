from typing import Protocol, Any


class Session(Protocol):
    async def execute(self): pass


class CrudPort(Protocol):
    async def create(
        self, domain_model, seq_data: list | None = None, session = None, **kwargs
    ) -> tuple[dict, ...] | dict: pass
    async def delete(self, domain_model, session = None, **filters) -> tuple[dict, ...]: pass
    async def update(self, domain_model, filters: dict, session = None, **values): pass
    async def read(
        self,
        domain_model,
        session = None,
        to_join=None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        distinct: str | None = None,
        **filters
    ) -> tuple[dict, ...]: pass
