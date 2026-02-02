import logging

from domain import Collections
from services.Uow import UnitOfWork

log = logging.getLogger(__name__)


async def add_collection(
    name: str,
    image: bytes,
    category_name: str,
    manager,
    generate_image_variant_callback,
    file_manager,
    uow_class=UnitOfWork,
):

    async with uow_class(manager._session_factory) as uow:
        file_manager.set_path("static/images/base/collections")
        path_name = f"{name}-{category_name}"
        image_path = file_manager.upload_dir / path_name
        collection_record = await manager.create(
            Collections,
            name=name,
            category_name=category_name,
            image_path=str(image_path),
            session=uow.session,
        )
        try:
            await file_manager.save(image_path, image)
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
    file_manager,
    uow_class=UnitOfWork
):
    async with uow_class(manager._session_factory) as uow:
        collection = await manager.delete(Collections, name=name, category_name=category_name, session=uow.session)
        collection = collection[0]
        file_manager.set_path("static/images")
        base_root = file_manager.upload_dir / "base" / "collections"
        collection_root = file_manager.upload_dir / "collections" / "catalog"
        name = f"{collection['name']}-{collection['category_name']}"
        paths = [base_root / name, collection_root / name]
        file_manager.delete(paths)
