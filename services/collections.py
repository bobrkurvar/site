import logging
from pathlib import Path

from domain import Collections
from services.Uow import UnitOfWork

log = logging.getLogger(__name__)


async def add_collection(
    name: str,
    image: bytes,
    category_name: str,
    manager,
    uow_class=UnitOfWork,
    upload_root=None,
    generate_image_variant_callback=None,
    save_files = None,
):

    async with uow_class(manager._session_factory) as uow:
        upload_dir = upload_root or Path("static/images/base/collections")
        path_name = f"{name}-{category_name}"
        image_path = upload_dir / path_name
        collection_record = await manager.create(
            Collections,
            name=name,
            category_name=category_name,
            image_path=str(image_path),
            session=uow.session,
        )
        try:
            await save_files(upload_dir, image_path, image)
            #await generate_image_variant_callback(image_path, "collections")
            await generate_image_variant_callback(image_path)
        except TypeError:
            log.debug("generate_image_variant_callback  или save_files не получили нужную функцию")
            raise
        except FileExistsError:
            log.debug("путь %s уже занять", image_path)
            raise

        return collection_record


async def delete_collection(
    name: str,
    category_name: str,
    manager,
    uow_class=UnitOfWork,
    upload_root=None,
    delete_files=None
):
    async with uow_class(manager._session_factory) as uow:
        collection = await manager.delete(Collections, name=name, category_name=category_name, session=uow.session)
        collection = collection[0]
        root = upload_root or Path("static/images")
        base_root = root / "base" / "collections"
        collection_root = root / "collections" / "catalog"
        name = f'{collection['name']}-{collection['category_name']}'
        paths = [base_root / name, collection_root / name]
        delete_files(paths)
