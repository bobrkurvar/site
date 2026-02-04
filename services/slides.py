import logging
from core import logger

log = logging.getLogger(__name__)

async def add_slides(images: list[bytes], generate_images, file_manager):
    extra_num = file_manager.slides_file_count
    for i, image in enumerate(images):
        file_name = str(extra_num + i)
        try:
            await file_manager.save_slide_original(file_name, image)
            miniatures = await generate_images(image)
            for layer, miniature in miniatures.items():
                await file_manager.save_by_layer(file_name, miniature, layer)
        except TypeError:
            log.debug("generate_image_variant_callback  или save_files не получили нужную функцию")
            raise
        except FileExistsError:
            log.debug("путь уже занять")
            pass

async def delete_slides(file_manager):
    # upload_dirs = [BASE_DIR / "slides", BASE_DIR / "base" / "slides"]
    # log.debug("deleted slite dir: %s", upload_dirs)
    # for upload_dir in upload_dirs:
    #     for f in upload_dir.iterdir():
    #         if f.is_file() and f.exists():
    #             f.unlink()
    file_manager.delete_all_slides()