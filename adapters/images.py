import asyncio
import logging
from pathlib import Path

from PIL import Image

from shared_queue import get_task_queue

log = logging.getLogger(__name__)



def save_image(
    image: Image.Image,
    path: Path,
    form: str,
    quality: int
):
    image.save(
        path,
        form,
        quality=quality,
        optimize=True,
        progressive=True,
    )


async def get_image_path(my_path: str, *directories, upload_root=None):
    if directories:
        upload_dir = upload_root or Path(__name__).parent.parent
        my_path_name = Path(my_path).name
        path = upload_dir / "static" / "images"
        for directory in directories:
            path /= directory
        path /= my_path_name
        str_path = str(path)
        # log.debug("Path: %s", str_path)
        if path.exists():
            # log.debug("MINI Path: %s", str_path)
            log.debug("Path: %s", str_path)
            return str_path
    return my_path


def enqueue_resize_task(input_path: Path, target: str, quality: int = 82):
    task_queue = get_task_queue()
    task = (str(input_path), target, quality, 0)
    task_queue.put(task)
    log.info("Task queued: %s", task)


async def generate_image_variant_bg(input_path: Path, target: str, quality: int = 82):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, enqueue_resize_task, input_path, target, quality)
