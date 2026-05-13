import logging
from collections.abc import Collection

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload
from db.mapper import registry as rg
from sqlalchemy import func
from domain import (AlreadyExistsError, ForeignKeyViolationError,
                               NotFoundError, DomainFilter)

log = logging.getLogger(__name__)


class Crud:
    def __init__(self, session_factory, registry):
        self._session_factory = session_factory
        self._registry = registry

    @property
    def session_factory(self) -> async_sessionmaker:
        if self._session_factory is None:
            raise RuntimeError("Not connected")
        return self._session_factory

    async def create(
            self, domain_obj=None, seq_data: list | None = None, session=None,
    ) -> tuple | object:
        incoming_data = seq_data if seq_data is not None else [domain_obj]

        async def _create_internal(cur_session):
            orm_objs = []
            for d_obj in incoming_data:
                orm_objs.append(self._registry.to_orm(d_obj))

            if seq_data:
                log.debug("Создание нескольких объектов")
                cur_session.add_all(orm_objs)
            else:
                log.debug("Создание одного объекта")
                cur_session.add(orm_objs[0])

            await cur_session.flush()

            created_domains = tuple(self._registry.to_domain(o) for o in orm_objs)
            return created_domains if seq_data is not None else created_domains[0]

        try:
            if session is not None:
                return await _create_internal(session)
            else:
                async with self.session_factory.begin() as session_ctx:
                    return await _create_internal(session_ctx)

        except IntegrityError as err:
            diag = getattr(err.orig, "diag", None)
            table_name = getattr(diag, "table_name", "unknown_table") if diag else "unknown_table"
            pgcode = getattr(err.orig, "pgcode", None)

            if pgcode == "23505":
                constraint_name = getattr(diag, "constraint_name", "unknown") if diag else "unknown"
                raise AlreadyExistsError(table_name, constraint_name)
            elif pgcode == "23503":
                detail = getattr(diag, "message_detail", str(err)) if diag else str(err)
                raise ForeignKeyViolationError(table_name, detail)
            raise

    async def delete(self, domain_cls, session=None, **filters) -> tuple:
        async def _delete_internal(cur_session) -> tuple:
            log.debug("%s filter for delete: %s", domain_cls.__name__, filters)
            model = self._registry.get_model(domain_cls)
            conditions = [getattr(model, field) == value for field, value in filters.items()]
            if not conditions:
                raise ValueError("Delete operation must have filters.")
            delete_query = delete(model).where(*conditions).returning(model)
            result = await cur_session.execute(delete_query)
            deleted_domains = tuple(self._registry.to_domain(record) for record in result.scalars())
            log.debug("Удалено %d записей из %s", len(deleted_domains), model.__name__)
            if not deleted_domains:
                raise NotFoundError(model.__name__, **filters)
            return deleted_domains

        if session is not None:
            return await _delete_internal(session)
        async with self.session_factory.begin() as session_ctx:
            return await _delete_internal(session_ctx)


    async def update(self, domain_cls, filters: dict, session=None, **values) -> tuple:
        async def _update_internal(cur_session):
            model = self._registry.get_model(domain_cls)
            conditions = [getattr(model, field) == value for field, value in filters.items()]
            if not conditions:
                raise ValueError("Update must have filters.")

            query = update(model).where(*conditions).values(**values).returning(model)
            result = await cur_session.execute(query)
            updated_records = result.scalars()
            return tuple(self._registry.to_domain(record) for record in updated_records)

        if session is not None:
            return await _update_internal(session)
        async with self.session_factory.begin() as session_ctx:
            return await _update_internal(session_ctx)

    async def read_one(
        self,
        domain_cls,
        *,
        session=None,
        loaded=None,
        **filters
    ) -> object | None:
        results = await self.read(
            domain_cls,
            session=session,
            loaded=loaded,
            limit=1,
            **filters
        )

        return results[0] if results else None


    # async def read(
    #     self,
    #     domain_cls,
    #     *,
    #     session=None,
    #     loaded=None,
    #     limit: int | None = None,
    #     offset: int | None = None,
    #     order_by: str | None = None,
    #     distinct: str | None = None,
    #     **filters
    # ) -> tuple:
    #     async def _read_internal(cur_session):
    #         model = self._registry.get_model(domain_cls)
    #         options = []
    #         query = select(model)
    #         if loaded:
    #             for loaded_attr in set(loaded):
    #                 if hasattr(model, loaded_attr):
    #                     options.append(selectinload(getattr(model, loaded_attr)))
    #
    #         if options: query = query.options(*options)
    #
    #         conditions = []
    #         for field, value in filters.items():
    #             attr = getattr(model, field)
    #             if isinstance(value, Collection) and not isinstance(value, str):
    #                 conditions.append(attr.in_(value))
    #             else:
    #                 conditions.append(attr == value)
    #
    #         query = query.where(*conditions)
    #
    #         if distinct: query = query.distinct(getattr(model, distinct))
    #         if order_by: query = query.order_by(getattr(model, order_by))
    #         if offset is not None: query = query.offset(offset)
    #         if limit: query = query.limit(limit)
    #
    #         result = (await cur_session.execute(query)).scalars()
    #         return tuple(self._registry.to_domain(r) for r in result)
    #
    #     if session is not None:
    #         return await _read_internal(session)
    #     async with self.session_factory.begin() as session_ctx:
    #         return await _read_internal(session_ctx)
    async def read(
        self,
        domain_cls,
        *,
        session=None,
        loaded: Collection[str] | None = None,
        domain_filters: Collection[DomainFilter] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        distinct: str | None = None,
        **filters
    ) -> tuple:
        async def _read_internal(cur_session):
            base_orm_model = self._registry.get_model(domain_cls)
            options = []
            query = select(base_orm_model)
            if loaded:
                for loaded_attr in set(loaded):
                    if hasattr(base_orm_model, loaded_attr):
                        options.append(selectinload(getattr(base_orm_model, loaded_attr)))
            if options:
                query = query.options(*options)
            joined_models = set()
            if domain_filters:
                for d_filter in domain_filters:
                    filter_orm_model = self._registry.get_model(d_filter.model)
                    if filter_orm_model is not base_orm_model:
                        if filter_orm_model not in joined_models:
                            query = query.join(filter_orm_model)
                            joined_models.add(filter_orm_model)
                    attr = getattr(filter_orm_model, d_filter.field)

                    if isinstance(d_filter.value, list):
                        query = query.where(attr.in_(d_filter.value))
                    else:
                        query = query.where(attr == d_filter.value)

            conditions = []
            for field, value in filters.items():
                attr = getattr(base_orm_model, field)
                if isinstance(value, Collection) and not isinstance(value, str):
                    conditions.append(attr.in_(value))
                else:
                    conditions.append(attr == value)

            query = query.where(*conditions)

            if distinct: query = query.distinct(getattr(base_orm_model, distinct))
            if order_by: query = query.order_by(getattr(base_orm_model, order_by))
            if offset is not None: query = query.offset(offset)
            if limit: query = query.limit(limit)

            result = (await cur_session.execute(query)).scalars().unique()
            return tuple(self._registry.to_domain(r) for r in result)

        if session is not None:
            return await _read_internal(session)
        async with self.session_factory.begin() as session_ctx:
            return await _read_internal(session_ctx)

    async def count(self, domain_cls, **filters) -> int:
        base_orm_model = self._registry.get_model(domain_cls)
        query = select(func.count()).select_from(base_orm_model)

        conditions = []
        for field, value in filters.items():
            attr = getattr(base_orm_model, field)
            conditions.append(attr == value)

        if conditions:
            query = query.where(*conditions)

        async with self.session_factory.begin() as session:
            result = await session.execute(query)
            return result.scalar()

def build_crud(session_factory) -> Crud:
    return Crud(
        session_factory=session_factory,
        registry=rg
    )
