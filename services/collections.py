import logging

from domain import Collections, Slug, CollectionCategory
from services.UoW import UnitOfWork
from slugify import slugify

log = logging.getLogger(__name__)


async def add_collection(
    name: str,
    image: bytes,
    category_name: str,
    manager,
    generate_images,
    file_manager,
    uow_class=UnitOfWork,
):

    async with uow_class(manager._session_factory) as uow:
        image_path = file_manager.base_collection_path(name)
        collection_record = await manager.read(Collections, name=name, session=uow.session)
        if not collection_record:
            collection_record = await manager.create(
                Collections,
                name=name,
                image_path=str(image_path),
                session=uow.session,
            )
            try:
                async with file_manager.session() as files:
                    await files.save(image_path, image)
                    miniatures = await generate_images(image)
                    for layer, miniature in miniatures.items():
                        await files.save_by_layer(image_path, miniature, layer)
            except TypeError:
                log.debug(
                    "generate_image_variant_callback  или save_files не получили нужную функцию"
                )
                raise
            except FileExistsError:
                log.debug("путь %s уже занять", image_path)
                raise
        await manager.create(CollectionCategory, collection_name=name, category_name=category_name, session=uow.session)
        await manager.create(Slug, name=name, slug=slugify(name))
        return collection_record


async def delete_collection(
    collection_name: str,
    manager,
    file_manager,
    uow_class=UnitOfWork,
):
    async with uow_class(manager._session_factory) as uow:
        collection = await manager.delete(
            Collections,
            name=collection_name,
            session=uow.session,
        )
        await manager.delete(Slug, name=collection_name, session=uow.session)
        collection = collection[0]
        await file_manager.delete_collection(collection["image_path"])
