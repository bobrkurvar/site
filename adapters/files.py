import aiofiles
from pathlib import Path
import logging

log = logging.getLogger(__name__)

async def save_files(upload_dir: str, image_path, img, fs=aiofiles):
    upload_dir = Path(upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    async with fs.open(image_path, "xb") as fw:
        await fw.write(img)

def delete_files(paths: list[Path]):
    files_deleted = 0
    for path in paths:
        log.debug("for delete collection_path: %s", str(path))
        path.unlink(missing_ok=True)
        files_deleted += 1
        log.info(f"Удален файл: {path}")
