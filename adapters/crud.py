import logging
from collections.abc import Collection

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

import domain
from core import conf
from db import models
from domain.exceptions import (AlreadyExistsError, ForeignKeyViolationError,
                               NotFoundError)

log = logging.getLogger(__name__)




class Crud:

    def __init__(self, url, domain_with_orm: dict | None = None):
        self.url = url
        self._engine = None
        self.session_factory = None
        self._mapper = domain_with_orm if domain_with_orm else {}

    def connect(self):
        if self._engine is None:
            self._engine = create_async_engine(self.url)
        if self.session_factory is None:
            self.session_factory = async_sessionmaker(self._engine)

    async def close_and_dispose(self):
        log.debug("подключение к движку %s закрывается", self._engine)
        await self._engine.dispose()
        self.session_factory = None
        self._engine = None

    def register(self, domain_cls, orm_cls):
        self._mapper[domain_cls] = orm_cls

    async def create(
        self, domain_model, seq_data: list | None = None, session=None, **kwargs
    ) -> tuple[dict, ...] | dict:
        model = self._mapper[domain_model]

        async def _create_internal(cur_session):
            if seq_data:
                log.debug("создание нескольких объектов")
                objs = [model(**data) for data in seq_data]
                cur_session.add_all(objs)
                await cur_session.flush()
                return tuple(obj.model_dump() for obj in objs)
            else:
                log.debug(
                    "%s: параметры для создания %s",
                    domain_model,
                    kwargs,
                )
                obj = model(**kwargs)
                cur_session.add(obj)
                await cur_session.flush()
                return obj.model_dump()

        try:

            if session is not None:
                return await _create_internal(session)

            else:
                async with self.session_factory.begin() as session_ctx:
                    return await _create_internal(session_ctx)

        except IntegrityError as err:
            pgcode = getattr(err.orig, "pgcode", None)

            if pgcode == "23505":
                constraint_name = (
                    getattr(err.orig.diag, "constraint_name", "unknown")
                    if hasattr(err.orig, "diag")
                    else "unknown"
                )
                raise AlreadyExistsError(model.__name__, constraint_name)

            elif pgcode == "23503":
                detail = (
                    getattr(err.orig.diag, "message_detail", str(err))
                    if hasattr(err.orig, "diag")
                    else str(err)
                )
                raise ForeignKeyViolationError(model.__name__, detail)

            raise

    async def delete(self, domain_model, session=None, **filters) -> tuple[dict, ...]:
        async def _delete_internal(cur_session) -> tuple[dict, ...]:
            log.debug("%s filter for delete: %s", domain_model, filters)
            model = self._mapper[domain_model]

            conditions = [
                getattr(model, field) == value for field, value in filters.items()
            ]

            delete_query = delete(model).where(*conditions).returning(model)

            result = await cur_session.execute(delete_query)
            deleted_records = result.scalars()
            result = tuple(record.model_dump() for record in deleted_records)
            if not result:
                raise NotFoundError(model.__name__, **filters)

            log.debug(
                "Удалено %d записей из %s с фильтрами: %s",
                len(result),
                model.__name__,
                filters,
            )

            return result

        if session is not None:
            return await _delete_internal(session)
        else:
            async with self.session_factory.begin() as session:
                return await _delete_internal(session)

    async def update(self, domain_model, filters: dict, session=None, **values):

        async def _update_internal(cur_session):
            model = self._mapper[domain_model]
            query = update(model)

            conditions = [getattr(model, field) == value for field, value in filters.items()]
            # for field, value in filters.items():
            #     query = query.where(getattr(model, field) == value)
            query = query.where(*conditions)

            query = query.values(**values)

            await cur_session.execute(query)

        if session is not None:
            return await _update_internal(session)
        else:
            async with self.session_factory.begin() as session:
                return await _update_internal(session)

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
    ) -> tuple[dict, ...]:

        async def _read_internal(cur_session):
            model = self._mapper[domain_model]

            options = []

            if to_join:

                join_attrs = set(to_join)
                log.debug("to_join: %s", to_join)
                for join_attr in join_attrs:
                    if hasattr(model, join_attr):
                        options.append(selectinload(getattr(model, join_attr)))

            query = select(model)

            if options:
                query = query.options(*options)

            conditions = []
            for field, value in filters.items():
                attr = getattr(model, field)
                if isinstance(value, Collection) and not isinstance(value, str):
                    conditions.append(attr.in_(value))
                else:
                    conditions.append(attr == value)

            query = query.where(*conditions)

            if distinct:
                query = query.distinct(getattr(model, distinct))

            if order_by:
                query = query.order_by(getattr(model, order_by))

            if offset:
                query = query.offset(offset)

            if limit:
                query = query.limit(limit)
            result = (await cur_session.execute(query)).scalars()
            return tuple(r.model_dump() for r in result)

        if session is not None:
            return await _read_internal(session)
        else:
            async with self.session_factory.begin() as session:
                return await _read_internal(session)


_db_manager: Crud | None = None


def get_db_manager(test=False) -> Crud:
    db_host = conf.db_url if not test else conf.test_db_url
    domain_with_orm = {
        domain.Tile: models.Catalog,
        domain.TileSize: models.TileSize,
        domain.TileColor: models.TileColor,
        domain.TileSurface: models.TileSurface,
        domain.Producer: models.Producer,
        domain.Box: models.Box,
        domain.TileImages: models.TileImages,
        domain.Categories: models.Categories,
        domain.Collections: models.Collections,
        domain.Admin: models.Admins,
        domain.Slug: models.Slug,
        domain.CollectionCategory: models.CollectionCategory,
    }
    global _db_manager
    if _db_manager is None:
        _db_manager = Crud(db_host, domain_with_orm)

    return _db_manager
