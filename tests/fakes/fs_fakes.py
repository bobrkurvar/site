from pathlib import Path
import logging
import core.logger

log = logging.getLogger(__name__)

BASE_DIR = Path("static/images")
OUTPUT_DIRS = {
    "products": BASE_DIR / "products" / "catalog",
    "collections": BASE_DIR / "collections" / "catalog",
    "details": BASE_DIR / "products" / "details",
    "slides": BASE_DIR / 'slides'
}

class FakeFileManager:
    def __init__(self, upload_dir: str | None = None, fs = None):
        self.upload_dir = Path(upload_dir) if upload_dir else None
        self.fs = fs

    def set_path(self, upload_dir: str):
        if self.upload_dir is None:
            self.upload_dir = Path(upload_dir)

    async def save(self, image_path, img):
        if self.fs is not None:
            self.fs[str(image_path)] = img

    def delete(self, paths):
        fake_deleted = 0
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            del self.fs[str(path)]
            fake_deleted += 1
        return fake_deleted

    def path(self, str_name):
        name = Path(str_name).name
        return self.upload_dir / name

# def get_fake_save_files_function_with_fs(fs: dict):
#     async def fake_save_files(upload_dir, image_path, img):
#         fs[str(image_path)] = img
#     return fake_save_files
#
# def get_fake_delete_files_function_with_fs(fs: dict):
#     def fake_delete_files(paths):
#         for path in paths:
#             del fs[str(path)]
#     return fake_delete_files

def get_fake_save_bg_products_and_details_with_fs(fs: dict):
    async def fake_save_bg(image_path):
        for target in ("products", "details"):
            input_path = Path(image_path)
            output_dir = OUTPUT_DIRS[target]
            output_path = output_dir / input_path.name
            fs[str(output_path)] = ""
    return fake_save_bg

def get_fake_save_bg_collections_with_fs(fs: dict):
    async def fake_save_bg(image_path):
        target = "collections"
        input_path = Path(image_path)
        output_dir = OUTPUT_DIRS[target]
        output_path = output_dir / input_path.name
        fs[str(output_path)] = ""
    return fake_save_bg