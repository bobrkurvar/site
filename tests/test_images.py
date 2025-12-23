# import logging
#
# import pytest
#
# from services.images import get_image_path
#
# from .fakes import FakeFileSystem, FakePath
#
# log = logging.getLogger(__name__)
#
#
# @pytest.fixture
# def fs():
#     return FakeFileSystem()
#
#
# @pytest.mark.asyncio
# async def test_get_image_path_returns_catalog_image(fs):
#     upload_root = FakePath("", fs=fs)
#
#     base_image = "/static/images/tiles/1-0"
#
#     catalog_image_path = "/static/images/catalog/1-0"
#     fs.files[catalog_image_path] = b"thumbnail"
#
#     result = await get_image_path(
#         my_path=base_image,
#         directory="catalog",
#         upload_root=upload_root,
#     )
#
#     assert result == catalog_image_path
#
#
# @pytest.mark.asyncio
# async def test_get_image_path_returns_tiles_image(fs):
#     upload_root = FakePath("", fs=fs)
#
#     base_image = "/static/images/tiles/1-0"
#
#     result = await get_image_path(
#         my_path=base_image,
#         directory="catalog",
#         upload_root=upload_root,
#     )
#
#     assert result == base_image
