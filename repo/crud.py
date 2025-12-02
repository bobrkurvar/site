import logging

from sqlalchemy import and_, delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from repo.exceptions import (AlreadyExistsError,
                             CustomForeignKeyViolationError, NotFoundError)

log = logging.getLogger(__name__)


class Crud:
    _engine = None
    _session_factory = None

    def __init__(self, url, domain_with_orm: dict | None = None):
        if self.__class__._engine is None:
            self.__class__._engine = create_async_engine(url)
        if self.__class__._session_factory is None:
            self.__class__._session_factory = async_sessionmaker(self._engine)
        self._mapper = domain_with_orm if domain_with_orm else {}

    def register(self, domain_cls, orm_cls):
        self._mapper[domain_cls] = orm_cls

    async def create(
        self, domain_model, seq_data: list | None = None, session=None, **kwargs
    ):
        model = self._mapper[domain_model]

        async def _create_internal(session):
            if seq_data:
                log.debug("создание нескольких объектов")
                objs = [model(**data) for data in seq_data]
                session.add_all(objs)
                await session.flush()
                return [obj.model_dump() for obj in objs]
            else:
                log.debug(
                    "%s: параметры для создания %s",
                    domain_model,
                    kwargs,
                )
                obj = model(**kwargs)
                session.add(obj)
                await session.flush()
                return obj.model_dump()

        try:

            if session is not None:
                return await _create_internal(session)

            else:
                async with self._session_factory.begin() as session_ctx:
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
                raise CustomForeignKeyViolationError(model.__name__, detail)

            raise

    async def delete(self, domain_model, session=None, **filters):
        async def _delete_internal(session):
            log.debug("%s filter for delete: %s", domain_model, filters)
            model = self._mapper[domain_model]

            conditions = [
                getattr(model, field) == value for field, value in filters.items()
            ]

            delete_query = delete(model).where(*conditions).returning(model)

            result = await session.execute(delete_query)
            deleted_records = result.scalars().all()

            if not deleted_records:
                raise NotFoundError(model.__name__, str(filters))

            log.debug(
                "Удалено %d записей из %s с фильтрами: %s",
                len(deleted_records),
                model.__name__,
                filters,
            )

            return [record.model_dump() for record in result]

        if session is not None:
            return await _delete_internal(session)
        else:
            async with self._session_factory.begin() as session:
                return await _delete_internal(session)

    async def update(self, domain_model, filters: dict, session=None, **values):

        async def _update_internal(session):
            model = self._mapper[domain_model]
            query = update(model)

            for field, value in filters.items():
                query = query.where(getattr(model, field) == value)

            query = query.values(**values)

            await session.execute(query)

        if session is not None:
            return await _update_internal(session)
        else:
            async with self._session_factory.begin() as session:
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
    ):

        async def _read_internal(session):
            model = self._mapper[domain_model]

            options = []

            if to_join:

                join_attrs = set(to_join)
                log.debug("to_join: %s", to_join)
                for join_attr in join_attrs:
                    if hasattr(model, join_attr):
                        options.append(selectinload(getattr(model, join_attr)))

            query = select(model)

            if distinct:
                query.distinct(getattr(model, distinct))

            if options:
                query = query.options(*options)

            for field, value in filters.items():
                query = query.where(getattr(model, field) == value)

            if order_by:
                query = query.order_by(getattr(model, order_by))

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = (await session.execute(query)).unique().scalars().all()
            return [r.model_dump() for r in result]

        if session is not None:
            return await _read_internal(session)
        else:
            async with self._session_factory.begin() as session:
                return await _read_internal(session)

    async def close_and_dispose(self):
        log.debug("подключение к движку %s закрывается", self._engine)
        await self._engine.dispose()
