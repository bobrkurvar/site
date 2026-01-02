import logging
from pathlib import Path

import aiofiles

from domain import Collections
from repo.Uow import UnitOfWork

log = logging.getLogger(__name__)


async def add_collection(
    name: str,
    image: bytes,
    category_name: str,
    manager,
    fs=aiofiles,
    uow_class=UnitOfWork,
    upload_root=None,
):

    async with uow_class(manager._session_factory) as uow:
        upload_dir = upload_root or Path(__name__).parent.parent
        upload_dir = upload_dir / "static" / "images" / "collections"
        upload_dir.mkdir(parents=True, exist_ok=True)
        extra_num = len([f for f in upload_dir.iterdir() if f.is_file()])
        image_path = upload_dir / str(extra_num)
        collection_record = await manager.create(
            Collections,
            name=name,
            category_name=category_name,
            image_path=str(image_path),
            session=uow.session,
        )
        try:
            async with fs.open(image_path, "xb") as fw:
                await fw.write(image)
        except FileExistsError:
            log.debug("путь %s уже занять", image_path)
            raise

        return collection_record


# async def delete_tile(manager, **filters):
#
#     async with UnitOfWork(manager._session_factory) as uow:
#         tiles = await manager.read(
#             Tile, to_join=["images"], session=uow.session, **filters
#         )
#         files_deleted = 0
#         await manager.delete(Tile, session=uow.session, **filters)
#
#         for tile in tiles:
#             images_paths = tile["images_paths"]
#             project_root = Path(__file__).resolve().parent.parent
#             upload_dir_str = str(project_root).replace(r"\app", "")
#             absolute_path = Path(upload_dir_str)
#             for image in images_paths:
#                 image_str = image.lstrip("/")
#                 image_path = absolute_path / image_str
#                 log.debug("for delete image_path: %s", str(image_path))
#                 if image_path.exists():
#                     image_path.unlink(missing_ok=True)
#                     files_deleted += 1
#                     log.info(f"Удален файл: {image_path}")
#         log.info("Удалено файлов: %s", files_deleted)
