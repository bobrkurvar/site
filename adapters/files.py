# import aiofiles
# from pathlib import Path
# import logging
#
# log = logging.getLogger(__name__)
#
# async def save_files(upload_dir: str, image_path, img, fs=aiofiles):
#     upload_dir = Path(upload_dir)
#     upload_dir.mkdir(parents=True, exist_ok=True)
#     async with fs.open(image_path, "xb") as fw:
#         await fw.write(img)
#
# def delete_files(paths: list[Path]):
#     files_deleted = 0
#     for path in paths:
#         log.debug("for delete collection_path: %s", str(path))
#         path.unlink(missing_ok=True)
#         files_deleted += 1
#         log.info(f"Удален файл: {path}")

from pathlib import Path
import aiofiles
import logging

log = logging.getLogger(__name__)

class FileManager:
    def __init__(self, upload_dir: str | None, fs=aiofiles):
        self.upload_dir = Path(upload_dir) if upload_dir else None
        self.fs = fs

    def set_path(self, upload_dir: str):
        if self.upload_dir is None:
            self.upload_dir = Path(upload_dir)

    async def save(self, image_path, img):
        if self.upload_dir:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            async with self.fs.open(image_path, "xb") as fw:
                await fw.write(img)

    def delete(self, paths: list[Path]):
        deleted = 0
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            path.unlink(missing_ok=True)
            deleted += 1
            #log.info(f"Deleted file: {path}")
        return deleted

    def path(self, str_name):
        name = Path(str_name).name
        return self.upload_dir / name