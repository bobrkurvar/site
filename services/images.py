import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

log = logging.getLogger(__name__)

IMAGE_PRESETS = {
    "catalog": (480, 300),
    "tile": (320, 200),
    "collection": (640, 400),
}


def generate_image_variant(
    input_path: Path,
    upload_root: Path,
    target_dir: str,
    quality: int = 82,
):
    """
    Создаёт миниатюру изображения в static/images/{target_dir}
    с тем же именем файла, что и оригинал.

    Функция идемпотентна — если файл уже существует, ничего не делает.
    """

    if target_dir not in IMAGE_PRESETS:
        raise ValueError(f"Unknown image preset: {target_dir}")

    output_dir = upload_root / "static" / "images" / target_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / input_path.name

    if output_path.exists():
        log.debug("Image already exists: %s", output_path)
        return output_path

    width, height = IMAGE_PRESETS[target_dir]

    with Image.open(input_path) as img:
        img = img.convert("RGB")
        resized = img.resize((width, height), Image.LANCZOS)
        output_format = output_path.suffix.lower().replace(".", "")
        resized.save(
            output_path,
            output_format.upper(),
            quality=quality,
            optimize=True,
            progressive=True,
        )

    log.info("Generated %s image: %s", target_dir, output_path)
    return output_path


async def get_image_path(my_path: str, directory: str | None, upload_root=None):
    if directory:
        upload_dir = upload_root or Path(__name__).parent.parent
        my_path_name = Path(my_path).name
        path = upload_dir / "static" / "images" / directory / my_path_name
        str_path = str(path)
        log.debug("Path: %s", str_path)
        if path.exists():
            log.debug("MINI Path: %s", str_path)
            return str_path
    return my_path


executor = ThreadPoolExecutor(max_workers=4)


async def generate_image_variant_bg(
    input_path: Path, upload_root: Path, target_dir: str, quality: int = 82
):
    """
    Асинхронная обёртка для генерации миниатюры в фоне.
    Возвращает путь к файлу (Future), но не блокирует основной поток.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor, generate_image_variant, input_path, upload_root, target_dir, quality
    )




@pytest.mark.asyncio
async def test_generate_image_variant_mocked():
    input_path = Path("/fake/path/1-0.png")
    upload_root = Path("/fake/upload")

    with patch("your_module.Image.open") as mock_open:
        mock_img = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_img

        mock_img.convert.return_value = mock_img
        mock_img.resize.return_value = mock_img

        with patch.object(Path, "mkdir") as mock_mkdir:
            # вызываем функцию
            result = generate_image_variant(
                input_path, upload_root, "catalog", quality=82
            )

        # Проверяем, что mkdir создал папку
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Проверяем, что resize вызван с правильными размерами
        mock_img.resize.assert_called_once_with((480, 300), mock_img.LANCZOS)

        # Проверяем, что save вызван
        mock_img.save.assert_called_once()
