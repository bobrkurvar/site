from pathlib import Path

import pytest

from shared import COLLECTIONS, DETAILS, PRODUCTS


@pytest.mark.asyncio
async def test_files_session_remove_exists_files_when_raises(product_images):
    file_manager, fs, _ = product_images
    try:
        async with file_manager.session() as files:
            await files.save("image1", b"1")
            await files.save("image2", b"2")
            await files.save_by_layer("image3", b"3", PRODUCTS)
            assert len(fs) == 3
            raise Exception
    except Exception:
        assert not fs


def test_base_collection_path(collection_images):
    images_manager, _, root = collection_images
    file_name = "abcdef123456.jpg"
    path = images_manager.base_collection_path(file_name)
    expected_path = Path(f"{root}/base/collections/{file_name}")
    assert path == expected_path


def test_resolve_path_for_collection_catalog_layer(collection_images):
    images_manager, _, root = collection_images
    file_name = "abcdef123456.jpg"
    layer = COLLECTIONS  # Имитируем название слоя
    path = images_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{root}/collections/catalog/{file_name}")
    assert path == expected_path


@pytest.mark.asyncio
async def test_save_file_collection_catalog_path(collection_images):
    images_manager, fs, root = collection_images
    file_name, img, layer = "abcdef123456.jpg", b"aaa", COLLECTIONS
    await images_manager.save_by_layer(file_name, img, layer)
    expected_path = Path(f"{root}/collections/catalog/{file_name}").as_posix()
    assert expected_path in fs


def test_base_product_path(product_images):
    images_manager, _, root = product_images
    file_name = "abcdef123456.jpg"
    path = images_manager.base_product_path(file_name)
    expected_path = Path(f"{root}/base/products/{file_name}")
    assert path == expected_path


def test_resolve_path_for_product_catalog_layer(product_images):
    images_manager, _, root = product_images
    file_name = "abcdef123456.jpg"
    layer = PRODUCTS  # Имитируем название слоя
    path = images_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{root}/products/catalog/{file_name}")
    assert path == expected_path


def test_resolve_path_for_product_details_layer(product_images):
    images_manager, _, root = product_images
    file_name = "abcdef123456.jpg"
    layer = DETAILS  # Имитируем название слоя
    path = images_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{root}/products/details/{file_name}")
    assert path == expected_path


@pytest.mark.asyncio
async def test_save_file_product_catalog_path(product_images):
    images_manager, fs, root = product_images
    file_name, img, layer = "abcdef123456.jpg", b"aaa", PRODUCTS
    await images_manager.save_by_layer(file_name, img, layer)
    expected_path = Path(f"{root}/products/catalog/{file_name}").as_posix()
    assert expected_path in fs


@pytest.mark.asyncio
async def test_save_file_product_details_path(product_images):
    images_manager, fs, root = product_images
    file_name, img, layer = "abcdef123456.jpg", b"aaa", DETAILS
    await images_manager.save_by_layer(file_name, img, layer)
    expected_path = Path(f"{root}/products/details/{file_name}").as_posix()
    assert expected_path in fs
