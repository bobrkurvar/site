import logging
from typing import Any, List

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from repo.exceptions import (
    AlreadyExistsError,
    CustomForeignKeyViolationError,
    NotFoundError,
)

log = logging.getLogger(__name__)


class Crud:
    _engine = None
    _session_factory = None

    def __init__(self, url):
        if self.__class__._engine is None:
            self.__class__._engine = create_async_engine(url)
        if self.__class__._session_factory is None:
            self.__class__._session_factory = async_sessionmaker(self._engine)
        self._mapper = {}

    def register(self, domain_cls, orm_cls):
        self._mapper[domain_cls] = orm_cls

    async def create(self, domain_model, seq_data: List[Any] | None = None, **kwargs):
        try:
            async with self._session_factory.begin() as session:
                model = self._mapper[domain_model]
                if seq_data:
                    log.debug("создание нескольких объектов")
                    tup_lst = [model(**new_data) for new_data in seq_data]
                    session.add_all(tup_lst)
                    await session.flush()
                    return [tup.model_dump() for tup in tup_lst]
                else:
                    log.debug("параметры для создания %s", kwargs)
                    tup = model(**kwargs)
                    log.debug("создание задачи %s", tup)
                    session.add(tup)
                    await session.flush()
                    return tup.model_dump()
        except IntegrityError as err:
            log.debug("ПЕРЕХВАТИЛ INTEGIRITYERROR С КОДОМ %s", err.orig.pgcode)
            if err.orig.pgcode == "23505":
                log.debug("ТАКАЯ СУЩНОСТЬ УЖЕ СУЩЕСТВУЕТ")
                raise AlreadyExistsError(model.__name__, "id", tup.id)
            elif err.orig.pgcode == "23503":
                log.debug("ВНЕШНИЙ КЛЮЧ НА НЕ СУЩЕСТВУЮЩЕЕ ПОЛЕ")
                raise CustomForeignKeyViolationError(model.__name__, "doer_id", 3)

    async def delete(self, domain_model, ident: str | None = None, ident_val=None):
        async with self._session_factory.begin() as session:
            model = self._mapper[domain_model]
            if not (ident_val is None):
                if ident is None:
                    log.debug("Crud получил запрос на удаление id: %s", ident_val)
                    for_remove = await session.get(model, ident_val)
                    if for_remove is not None:
                        await session.delete(for_remove)
                        return for_remove.model_dump()
                    else:
                        raise NotFoundError(model.__name__, "id", ident_val)
                else:
                    log.debug(
                        "Crud получил запрос на удаление по параметру %s: %s",
                        ident,
                        ident_val,
                    )
                    for_remove = (
                        (
                            await session.execute(
                                select(model).where(getattr(model, ident) == ident_val)
                            )
                        )
                        .scalars()
                        .all()
                    )
                    if not for_remove:
                        raise NotFoundError(model.__name__, ident, ident_val)
                    for chunk in for_remove:
                        await session.delete(chunk)
            else:
                # models = await session.execute(select(model)).scalars().all()
                # if models is None:
                #     raise NotFoundError(model.__name__)
                await session.execute(delete(model))

    async def update(self, domain_model, ident: str, ident_val: int, **kwargs):
        async with self._session_factory.begin() as session:
            model = self._mapper[domain_model]
            query = (
                update(model).where(getattr(model, ident) == ident_val).values(**kwargs)
            )
            await session.execute(query)

    async def read(
        self,
        domain_model,
        ident: str | None = None,
        ident_val: int | str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        to_join: str | None = None,
    ):
        async with self._session_factory.begin() as session:
            model = self._mapper[domain_model]
            query = select(model)
            if to_join:
                joined_table = getattr(model, to_join)
                query = query.join(joined_table)
            if ident:
                if to_join:
                    query = query.where(
                        getattr(joined_table.property.mapper.class_, ident) == ident_val
                    )
                else:
                    query = query.where(getattr(model, ident) == ident_val)
            if order_by:
                log.debug("сортировка по %s", order_by)
                query = query.order_by(getattr(model, order_by))
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            res = (await session.execute(query)).scalars().all()
            # if not res:
                # log.debug("Возвращаемый список пуст: %s", res)
                # raise NotFoundError(model.__name__, ident, ident_val)
            return res if not res else [r.model_dump() for r in res]

    async def close_and_dispose(self):
        log.debug("подключение к движку %s закрывается", self._engine)
        await self._engine.dispose()
