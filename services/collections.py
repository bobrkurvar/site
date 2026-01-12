import logging
from pathlib import Path

import aiofiles

from domain import Collections
from repo.Uow import UnitOfWork
from services.images import generate_image_variant_bg

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
        upload_dir = upload_dir / "static" / "images" / "base" /"collections"
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
        generate_image_variant_bg(image_path, "collections")

        return collection_record
