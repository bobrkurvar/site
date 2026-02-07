import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine

from core import conf, logger
from db.models import Base


async def create_tables():
    # 2. Импортируем Base

    # 3. Создаем движок
    engine = create_async_engine(conf.test_db_url)

    # 4. Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await engine.dispose()


# 5. Запускаем
if __name__ == "__main__":
    asyncio.run(create_tables())
