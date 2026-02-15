import asyncio
from adapters.crud import get_db_manager
from domain import Collections
from pathlib import Path

async def main():
    manager = get_db_manager()
    manager.connect()
    collections = await manager.read(Collections)
    all_paths = "static/images/base/collections/"
    for col in collections:
        collection_id = str(col["id"])
        path = all_paths + collection_id
        collection_name = col["name"]
        await manager.update(Collections, {"name": collection_name}, image_path=path)
        old_paths = (
            Path("static/images/base/collections") / collection_name,
            Path("static/images/collections/catalog") / collection_name,
        )
        new_paths = [
            Path("static/images/base/collections") / collection_id,
            Path("static/images/collections/catalog") / collection_id,
        ]
        for old, new in zip(old_paths, new_paths):
            try:
                old.rename(new)
            except FileExistsError:
                print(f"Папка {new} уже существует. Пропускаем.")
            except FileNotFoundError:
                print(f"Папка {old} не найдена.")

if __name__ == "__main__":
    asyncio.run(main())