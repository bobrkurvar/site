import logging
import operator
from collections.abc import Collection
from contextlib import asynccontextmanager

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.exc import StaleDataError

from domain import (AlreadyExistsError, ConcurrentModificationError,
                    DomainFilter, ForeignKeyViolationError, NotFoundError,
                    Operation, Operations)

log = logging.getLogger(__name__)


@asynccontextmanager
async def handle_integrity_errors():
    try:
        yield
    except IntegrityError as err:
        diag = getattr(err.orig, "diag", None)
        table_name = (
            getattr(diag, "table_name", "unknown_table") if diag else "unknown_table"
        )
        pgcode = getattr(err.orig, "pgcode", None)

        if pgcode == "23505":
            constraint_name = (
                getattr(diag, "constraint_name", "unknown") if diag else "unknown"
            )
            raise AlreadyExistsError(table_name, constraint_name)
        elif pgcode == "23503":
            detail = getattr(diag, "message_detail", str(err)) if diag else str(err)
            raise ForeignKeyViolationError(table_name, detail)
        raise


class GenericRepository:
    def __init__(self, session, registry):
        # self._session_factory = session_factory
        self._registry = registry
        self.session = session

    @handle_integrity_errors()
    async def create(
        self, domain_obj=None, seq_data: list | None = None
    ) -> tuple | object:
        incoming_data = seq_data if seq_data is not None else [domain_obj]

        orm_objs = []
        for d_obj in incoming_data:
            orm_objs.append(self._registry.to_orm(d_obj))

        if seq_data:
            log.debug("Создание нескольких объектов")
            self.session.add_all(orm_objs)
        else:
            log.debug("Создание одного объекта")
            self.session.add(orm_objs[0])

        await self.session.flush()
        created_domains = tuple(self._registry.to_domain(o) for o in orm_objs)
        return created_domains if seq_data is not None else created_domains[0]

    async def delete(self, domain_cls, **filters) -> tuple:
        log.debug("%s filter for delete: %s", domain_cls.__name__, filters)
        model = self._registry.get_model(domain_cls)
        query = self._apply_conditions(delete(model), model, filters).returning(model)
        result = await self.session.execute(query)
        deleted_domains = tuple(
            self._registry.to_domain(record) for record in result.scalars()
        )
        log.debug("Удалено %d записей из %s", len(deleted_domains), model.__name__)
        if not deleted_domains:
            raise NotFoundError(model.__name__, **filters)
        return deleted_domains

    async def update(self, domain_cls, filters: dict, **values) -> tuple:
        if not filters:
            raise ValueError(
                "Update must have filters to prevent global table updates."
            )

        model = self._registry.get_model(domain_cls)
        query = self._apply_conditions(update(model), model, filters)
        query = query.values(**values).returning(model)

        result = await self.session.scalars(query)
        return tuple(self._registry.to_domain(record) for record in result)

    async def read_one(
        self,
        domain_cls,
        *,
        loaded=None,
        with_for_update: bool = False,
        with_raise: bool = False,
        **filters,
    ) -> object | None:
        results = await self.read(
            domain_cls,
            loaded=loaded,
            limit=1,
            with_for_update=with_for_update,
            with_raise=with_raise,
            **filters,
        )

        return results[0] if results else None

    def _apply_domain_filters(self, query, base_orm_model, domain_filters):
        """Применяет JOIN-ы и условия из доменных фильтров"""
        joined_models = set()
        if domain_filters:
            for d_filter in domain_filters:
                filter_orm_model = self._registry.get_model(d_filter.model)
                if filter_orm_model is not base_orm_model:
                    if filter_orm_model not in joined_models:
                        if getattr(d_filter, "join_on", None):
                            relationship_attr = getattr(
                                base_orm_model, d_filter.join_on
                            )
                            query = query.join(relationship_attr)
                        else:
                            query = query.join(filter_orm_model)
                        joined_models.add(filter_orm_model)

                attr = getattr(filter_orm_model, d_filter.field)
                if isinstance(d_filter.value, list):
                    query = query.where(attr.in_(d_filter.value))
                else:
                    query = query.where(attr == d_filter.value)
        return query

    def _apply_conditions(self, query, base_orm_model, filters: dict):
        """Применяет стандартные WHERE-условия с поддержкой объектов Operation"""

        def is_iterable_not_string(obj) -> bool:
            return isinstance(obj, Collection) and not isinstance(
                obj, (str, bytes, bytearray)
            )

        conditions = []
        operators_map = {
            Operations.exact: operator.eq,
            Operations.gte: operator.ge,
            Operations.lte: operator.le,
            Operations.gt: operator.gt,
            Operations.ne: operator.ne,
            Operations.lt: operator.lt,
            Operations.ilike: lambda attr, value: attr.ilike(value),
            Operations.in_: lambda attr, value: attr.in_(value),
            Operations.is_: lambda attr, _: attr.is_(value),
            Operations.is_not: lambda attr, _: attr.is_not(value),
        }
        for field, filter_data in filters.items():
            attr = getattr(base_orm_model, field)
            if isinstance(filter_data, Operation):
                value = filter_data.value
                op = filter_data.op
            else:
                value = filter_data
                op = "in" if is_iterable_not_string(value) else "exact"

            if op not in operators_map:
                raise ValueError(f"Неизвестный оператор для фильтрации: {op}")

            handler = operators_map[op]
            conditions.append(handler(attr, value))

        return query.where(*conditions)

    async def read(
        self,
        domain_cls,
        *,
        loaded: Collection[str] | None = None,
        domain_filters: Collection[DomainFilter] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        distinct: str | None = None,
        with_for_update: bool = False,
        with_raise: bool = False,
        **filters,
    ) -> tuple:
        if isinstance(loaded, str):
            loaded = [loaded]
        base_orm_model = self._registry.get_model(domain_cls)
        options = []
        query = select(base_orm_model).select_from(base_orm_model)
        if loaded:
            for loaded_attr in set(loaded):
                if hasattr(base_orm_model, loaded_attr):
                    options.append(selectinload(getattr(base_orm_model, loaded_attr)))
        if options:
            query = query.options(*options)
        query = self._apply_domain_filters(query, base_orm_model, domain_filters)
        query = self._apply_conditions(query, base_orm_model, filters)

        if distinct:
            query = query.distinct(getattr(base_orm_model, distinct))
        if order_by:
            query = query.order_by(getattr(base_orm_model, order_by))
        if offset is not None:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        if with_for_update:
            query = query.with_for_update()

        result = (await self.session.execute(query)).scalars().unique()
        tup_res = tuple(self._registry.to_domain(r) for r in result)
        if not tup_res and with_raise:
            raise NotFoundError(domain_cls.__name__, **filters)
        return tup_res

    async def count(
        self,
        domain_cls,
        *,
        domain_filters: Collection[DomainFilter] | None = None,
        **filters,
    ) -> int:
        base_orm_model = self._registry.get_model(domain_cls)
        query = select(func.count()).select_from(base_orm_model)
        query = self._apply_domain_filters(query, base_orm_model, domain_filters)
        query = self._apply_conditions(query, base_orm_model, filters)

        result = await self.session.execute(query)
        return result.scalar()

    async def save(self, domain_obj) -> object:
        async with handle_integrity_errors():
            try:
                log.debug(
                    "Сохранение агрегата через merge: %s", domain_obj.__class__.__name__
                )
                orm_obj = self._registry.to_orm(domain_obj)
                merged_orm = await self.session.merge(orm_obj)
                await self.session.flush()
                return self._registry.to_domain(merged_orm)
            except StaleDataError as e:
                log.warning(
                    "Конфликт версий при сохранении %s: %s",
                    domain_obj.__class__.__name__,
                    e,
                )
                raise ConcurrentModificationError(
                    "Данные были изменены другим пользователем"
                )

