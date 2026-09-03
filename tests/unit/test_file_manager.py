from pathlib import Path

import pytest

from shared import COLLECTIONS, DETAILS, PRODUCTS


@pytest.mark.asyncio
async def test_files_session_remove_exists_files_when_raises(products_env):
    env = products_env
    try:
        async with env.file_manager.session() as files:
            await files.save("image1", b"1")
            await files.save("image2", b"2")
            await files.save_by_layer("image3", b"3", PRODUCTS)
            assert len(env.fs) == 3
            raise Exception
    except Exception:
        assert not env.fs


def test_base_collection_path(collections_env):
    env = collections_env
    root = env.file_manager._root
    file_name = "abcdef123456.jpg"
    path = env.file_manager.base_collection_path(file_name)
    expected_path = Path(f"{root}/base/collections/{file_name}")
    assert path == expected_path


def test_resolve_path_for_collection_catalog_layer(collections_env):
    env = collections_env
    root = env.file_manager._root
    file_name = "abcdef123456.jpg"
    layer = COLLECTIONS  # Имитируем название слоя
    path = env.file_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{root}/collections/catalog/{file_name}")
    assert path == expected_path


@pytest.mark.asyncio
async def test_save_file_collection_catalog_path(collections_env):
    env = collections_env
    root = env.file_manager._root
    file_name, img, layer = "abcdef123456.jpg", b"aaa", COLLECTIONS
    await env.file_manager.save_by_layer(file_name, img, layer)
    expected_path = Path(f"{root}/collections/catalog/{file_name}").as_posix()
    assert expected_path in env.fs


def test_base_product_path(products_env):
    env = products_env
    root = env.file_manager._root
    file_name = "abcdef123456.jpg"
    path = env.file_manager.base_product_path(file_name)
    expected_path = Path(f"{root}/base/products/{file_name}")
    assert path == expected_path


def test_resolve_path_for_product_catalog_layer(products_env):
    env = products_env
    root = env.file_manager._root
    file_name = "abcdef123456.jpg"
    layer = PRODUCTS  # Имитируем название слоя
    path = env.file_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{root}/products/catalog/{file_name}")
    assert path == expected_path


def test_resolve_path_for_product_details_layer(products_env):
    env = products_env
    root = env.file_manager._root
    file_name = "abcdef123456.jpg"
    layer = DETAILS  # Имитируем название слоя
    path = env.file_manager.resolve_path(file_name, layer)
    expected_path = Path(f"{root}/products/details/{file_name}")
    assert path == expected_path


@pytest.mark.asyncio
async def test_save_file_product_catalog_path(products_env):
    env = products_env
    root = env.file_manager._root
    file_name, img, layer = "abcdef123456.jpg", b"aaa", PRODUCTS
    await env.file_manager.save_by_layer(file_name, img, layer)
    expected_path = Path(f"{root}/products/catalog/{file_name}").as_posix()
    assert expected_path in env.fs


@pytest.mark.asyncio
async def test_save_file_product_details_path(products_env):
    env = products_env
    root = env.file_manager._root
    file_name, img, layer = "abcdef123456.jpg", b"aaa", DETAILS
    await env.file_manager.save_by_layer(file_name, img, layer)
    expected_path = Path(f"{root}/products/details/{file_name}").as_posix()
    assert expected_path in env.fs
