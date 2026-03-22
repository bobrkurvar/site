import pytest
from tests.fakes import FakeStorage
from infrastructure.images import ProductImagesManager


@pytest.mark.asyncio
async def test_files_session_remove_exists_files_when_raises():
    fs = {}
    file_manager = ProductImagesManager(root="tests/images", storage=FakeStorage(fs))
    try:
        async with file_manager.session() as files:
            await files.save("image1", b"1")
            await files.save("image2", b"2")
            await files.save_by_layer("image3", b"3", "products")
            assert len(fs) == 3
            raise Exception
    except Exception:
        assert not fs