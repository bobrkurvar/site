# import logging
# from collections.abc import Collection
#
# from sqlalchemy import delete, select, update
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.ext.asyncio import async_sessionmaker
# from sqlalchemy.orm import selectinload
#
# import domain
# from db import models
# from domain.exceptions import (
#     AlreadyExistsError,
#     ForeignKeyViolationError,
#     NotFoundError,
# )
#
# log = logging.getLogger(__name__)
#
#
# class Crud:
#
#     def __init__(self, session_factory, domain_with_orm):
#         self._session_factory = session_factory
#         self._mapper = domain_with_orm or {}
#
#     @property
#     def session_factory(self) -> async_sessionmaker:
#         if self._session_factory is None:
#             raise RuntimeError("Not connected")
#         return self._session_factory
#
#     def register(self, domain_cls, orm_cls):
#         self._mapper[domain_cls] = orm_cls
#
#     async def create(
#         self, domain_model, seq_data: list | None = None, session=None, **kwargs
#     ) -> tuple[dict, ...] | dict:
#         model = self._mapper[domain_model]
#
#         async def _create_internal(cur_session):
#             if seq_data:
#                 log.debug("создание нескольких объектов")
#                 objs = [model(**data) for data in seq_data]
#                 cur_session.add_all(objs)
#                 await cur_session.flush()
#                 return tuple(obj.model_dump() for obj in objs)
#             else:
#                 log.debug(
#                     "%s: параметры для создания %s",
#                     domain_model,
#                     kwargs,
#                 )
#                 obj = model(**kwargs)
#                 cur_session.add(obj)
#                 await cur_session.flush()
#                 return obj.model_dump()
#
#         try:
#             if session is not None:
#                 return await _create_internal(session)
#
#             else:
#                 async with self.session_factory.begin() as session_ctx:
#                     return await _create_internal(session_ctx)
#
#         except IntegrityError as err:
#             pgcode = getattr(err.orig, "pgcode", None)
#
#             if pgcode == "23505":
#                 constraint_name = (
#                     getattr(err.orig.diag, "constraint_name", "unknown")  # type: ignore
#                     if hasattr(err.orig, "diag")
#                     else "unknown"
#                 )
#                 raise AlreadyExistsError(model.__name__, constraint_name)
#
#             elif pgcode == "23503":
#                 detail = (
#                     getattr(err.orig.diag, "message_detail", str(err))  # type: ignore
#                     if hasattr(err.orig, "diag")
#                     else str(err)
#                 )  # type: ignore
#                 raise ForeignKeyViolationError(model.__name__, detail)
#
#             raise
#
#     async def delete(self, domain_model, session=None, **filters) -> tuple[dict, ...]:
#         async def _delete_internal(cur_session) -> tuple[dict, ...]:
#             log.debug("%s filter for delete: %s", domain_model, filters)
#             model = self._mapper[domain_model]
#
#             conditions = [
#                 getattr(model, field) == value for field, value in filters.items()
#             ]
#
#             delete_query = delete(model).where(*conditions).returning(model)
#
#             result = await cur_session.execute(delete_query)
#             deleted_records = result.scalars()
#             result = tuple(record.model_dump() for record in deleted_records)
#             if not result:
#                 raise NotFoundError(model.__name__, **filters)
#
#             log.debug(
#                 "Удалено %d записей из %s с фильтрами: %s",
#                 len(result),
#                 model.__name__,
#                 filters,
#             )
#
#             return result
#
#         if session is not None:
#             return await _delete_internal(session)
#         else:
#             async with self.session_factory.begin() as session:
#                 return await _delete_internal(session)
#
#     async def update(self, domain_model, filters: dict, session=None, **values):
#
#         async def _update_internal(cur_session):
#             model = self._mapper[domain_model]
#             query = update(model)
#
#             conditions = [
#                 getattr(model, field) == value for field, value in filters.items()
#             ]
#             query = query.where(*conditions)
#
#             query = query.values(**values)
#
#             await cur_session.execute(query)
#
#         if session is not None:
#             return await _update_internal(session)
#         else:
#             async with self.session_factory.begin() as session:
#                 return await _update_internal(session)
#
#     async def read(
#         self,
#         domain_model,
#         *,
#         session=None,
#         loaded=None,
#         limit: int | None = None,
#         offset: int | None = None,
#         order_by: str | None = None,
#         distinct: str | None = None,
#         **filters
#     ) -> tuple[dict, ...]:
#
#         async def _read_internal(cur_session):
#             model = self._mapper[domain_model]
#
#             options = []
#
#             if loaded:
#                 loaded_attrs = set(loaded)
#                 for loaded_attr in loaded_attrs:
#                     if hasattr(model, loaded_attr):
#                         options.append(selectinload(getattr(model, loaded_attr)))
#
#             query = select(model)
#
#             if options:
#                 query = query.options(*options)
#
#             conditions = []
#             for field, value in filters.items():
#                 attr = getattr(model, field)
#                 if isinstance(value, Collection) and not isinstance(value, str):
#                     conditions.append(attr.in_(value))
#                 else:
#                     conditions.append(attr == value)
#
#             query = query.where(*conditions)
#
#             if distinct:
#                 query = query.distinct(getattr(model, distinct))
#
#             if order_by:
#                 query = query.order_by(getattr(model, order_by))
#
#             if offset is not None:
#                 query = query.offset(offset)
#
#             if limit:
#                 query = query.limit(limit)
#             result = (await cur_session.execute(query)).scalars()
#             return tuple(r.model_dump() for r in result)
#
#         if session is not None:
#             return await _read_internal(session)
#         else:
#             async with self.session_factory.begin() as session:
#                 return await _read_internal(session)
#
#
# DOMAIN_WITH_ORM = {
#     domain.Tile: models.Catalog,
#     domain.TileSize: models.TileSize,
#     domain.TileColor: models.TileColor,
#     domain.TileSurface: models.TileSurface,
#     domain.Producer: models.Producer,
#     domain.Box: models.Box,
#     domain.TileImage: models.TileImage,
#     domain.Category: models.Category,
#     domain.Collection: models.Collection,
#     domain.Admin: models.Admin,
#     domain.Slug: models.Slug,
#     domain.CollectionCategory: models.CollectionCategory,
# }
#
#
# def build_crud(session_factory) -> Crud:
#     return Crud(
#         session_factory=session_factory,
#         domain_with_orm=DOMAIN_WITH_ORM,
#     )


import logging
from collections.abc import Collection

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload
from db.mapper import registry as rg

from domain.exceptions import (AlreadyExistsError, ForeignKeyViolationError,
                               NotFoundError)

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

    async def read(
            self,
            domain_cls,
            *,
            session=None,
            loaded=None,
            limit: int | None = None,
            offset: int | None = None,
            order_by: str | None = None,
            distinct: str | None = None,
            **filters
    ) -> tuple:
        async def _read_internal(cur_session):
            model = self._registry.get_model(domain_cls)
            options = []

            if loaded:
                for loaded_attr in set(loaded):
                    if hasattr(model, loaded_attr):
                        options.append(selectinload(getattr(model, loaded_attr)))

            query = select(model)
            if options: query = query.options(*options)

            conditions = []
            for field, value in filters.items():
                attr = getattr(model, field)
                if isinstance(value, Collection) and not isinstance(value, str):
                    conditions.append(attr.in_(value))
                else:
                    conditions.append(attr == value)

            query = query.where(*conditions)

            if distinct: query = query.distinct(getattr(model, distinct))
            if order_by: query = query.order_by(getattr(model, order_by))
            if offset is not None: query = query.offset(offset)
            if limit: query = query.limit(limit)

            result = (await cur_session.execute(query)).scalars()
            return tuple(self._registry.to_domain(r) for r in result)

        if session is not None:
            return await _read_internal(session)
        async with self.session_factory.begin() as session_ctx:
            return await _read_internal(session_ctx)


def build_crud(session_factory) -> Crud:
    return Crud(
        session_factory=session_factory,
        registry=rg
    )
