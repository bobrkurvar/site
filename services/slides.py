import logging
from .ports import SlideImagesPort

from core import logger

log = logging.getLogger(__name__)


async def add_slides(images: list[bytes], generate_images, file_manager: SlideImagesPort):
    extra_num = file_manager.slides_file_count
    for i, image in enumerate(images):
        file_name = str(extra_num + i)
        try:
            base_slide_path = file_manager.base_slide_path(file_name)
            image_path = base_slide_path / file_name
            async with file_manager.session() as files:
                await files.save(image_path, image)
                miniatures = await generate_images(image)
                for layer, miniature in miniatures.items():
                    await files.save_by_layer(file_name, miniature, layer)
        except TypeError:
            log.debug(
                "generate_image_variant_callback  или save_files не получили нужную функцию"
            )
            raise
        except FileExistsError:
            log.debug("путь уже занять")
            pass


async def delete_slides(file_manager: SlideImagesPort):
    await file_manager.delete_all_slides()
