import logging

from domain import Collection, Slug

log = logging.getLogger(__name__)



async def add_collection(
    collection: Collection,
    images_generator,
    file_manager,
    uow,
):
    async with uow:
        collection_record = await uow.db.read_one(
            Collection, name=collection.name,  loaded="categories"
        )

        if not collection_record:
            slug = await uow.db.create(Slug(name=collection.name))
            file_name = slug.slug
            image_path = file_manager.base_collection_path(file_name)
            collection.assign_image_path(str(image_path))

            try:
                async with file_manager.session() as files:
                    img_bytes = collection.image.consume_bytes()
                    await files.save(image_path, img_bytes)
                    miniatures = await images_generator.generate_collection_variants(
                        img_bytes
                    )
                    for layer, miniature in miniatures.items():
                        await files.save_by_layer(file_name, miniature, layer)
            except TypeError:
                log.debug(
                    "generate_image_variant_callback или save_files не получили нужную функцию"
                )
                raise
            except FileExistsError:
                log.debug("путь %s уже занять", image_path)
                raise
            collection_target = collection
        else:
            collection_record.merge_categories(collection.categories)

            collection_target = collection_record
        result = await uow.db.save(collection_target)

        return result


async def delete_collection(
    collection_name: str,
    file_manager,
    uow,
):
    async with uow:
        collection = await uow.db.delete(
            Collection,
            name=collection_name,
        )
        await uow.db.delete(Slug, name=collection_name)
        collection = collection[0]
        await file_manager.delete_collection(collection.image_path)
