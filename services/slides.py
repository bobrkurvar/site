from pathlib import Path
import aiofiles
import logging

BASE_DIR = Path("static/images")
log = logging.getLogger(__name__)

async def add_slides(images: list[bytes], fs=aiofiles, generate_image_variant_callback=None):
    upload_dir = BASE_DIR / "slides"
    if not upload_dir.exists():
        upload_dir.mkdir(parents=True, exist_ok=True)
    extra_num = len([f for f in upload_dir.iterdir() if f.is_file()])
    for i, image in enumerate(images):
        image_path = upload_dir / str(extra_num + i)
        try:
            async with fs.open(image_path, "xb") as fw:
                await fw.write(image)
            if generate_image_variant_callback:
                await generate_image_variant_callback(image_path, "slides")
        except FileExistsError:
            log.debug("путь %s уже занять", image_path)

async def delete_slides():
    upload_dirs = [BASE_DIR / "slides", BASE_DIR / "base" / "slides"]
    log.debug("deleted slite dir: %s", upload_dirs)
    for upload_dir in upload_dirs:
        for f in upload_dir.iterdir():
            if f.is_file() and f.exists():
                f.unlink()