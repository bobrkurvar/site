import aiofiles
import logging
from pathlib import Path

log = logging.getLogger(__name__)

async def save_flies(image_path, img, fs=aiofiles):
    async with fs.open(image_path, "xb") as fw:
        await fw.write(img)

async def delete_files(images_paths: list[str], upload_root=None):
    log.debug("images paths: %s", images_paths)
    upload_dir = upload_root or Path()
    files_deleted = 0
    for image in images_paths:
        image_path = upload_dir / image
        product_catalog_path = (
                (upload_root or Path("static"))
                / "images"
                / "products"
                / "catalog"
                / Path(image).name
        )
        product_details_path = (
                (upload_root or Path("static"))
                / "images"
                / "products"
                / "details"
                / Path(image).name
        )
        all_paths = [image_path, product_catalog_path, product_details_path]
        for i in all_paths:
            log.debug("for delete: %s", str(i))
            if i.exists():
                i.unlink(missing_ok=True)
                files_deleted += 1
                log.info(f"Удален файл: {i}")

        log.info("Удалено файлов: %s", files_deleted)