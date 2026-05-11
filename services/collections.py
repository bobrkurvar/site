import logging

from domain import Collection, Slug, CollectionCategory, AlreadyExistsError
from infra.UoW import UnitOfWork

log = logging.getLogger(__name__)


async def add_collection(
    collection: Collection,
    manager,
    images_generator,
    file_manager,
    uow_class=UnitOfWork,
):

    async with uow_class(manager) as uow:
        collection_record = await manager.read_one(
            Collection, name=collection.name, session=uow.session, loaded="categories"
        )
        if not collection_record:
            collection_record = await manager.create(
                collection,
                session=uow.session,
            )
            coll_id = collection_record.id
            file_name = str(coll_id)
            image_path = file_manager.base_collection_path(file_name)
            await manager.update(
                Collection,
                {"id": coll_id},
                image_path=str(image_path),
                session=uow.session,
            )
            slug = Slug(name=collection.name)
            await manager.create(slug)
            try:
                async with file_manager.session() as files:
                    await files.save(image_path, collection.image_bytes)
                    miniatures = await images_generator.generate_collection_variants(collection.image_bytes)
                    for layer, miniature in miniatures.items():
                        await files.save_by_layer(file_name, miniature, layer)
            except TypeError:
                log.debug(
                    "generate_image_variant_callback  или save_files не получили нужную функцию"
                )
                raise
            except FileExistsError:
                log.debug("путь %s уже занять", image_path)
                raise
        else:
            coll_id = collection_record.id

        for category in collection.categories:
            try:
                await manager.create(
                    CollectionCategory(
                        collection_id=coll_id,
                        category_name=category.name
                    ),
                    session=uow.session
                )
                log.debug("Явно создана связь: Collection %s -> Category %s", coll_id, category.name)
            except AlreadyExistsError:
                log.debug("Связь уже существует, пропускаем")
                pass

        return collection_record


async def delete_collection(
    collection_name: str,
    manager,
    file_manager,
    uow_class=UnitOfWork,
):
    async with uow_class(manager) as uow:
        collection = await manager.delete(
            Collection,
            name=collection_name,
            session=uow.session,
        )
        await manager.delete(Slug, name=collection_name, session=uow.session)
        collection = collection[0]
        await file_manager.delete_collection(collection.image_path)
