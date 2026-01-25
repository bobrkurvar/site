
def get_fake_save_files_function_with_fs(fs: dict):
    async def fake_save_files(upload_dir, image_path, img):
        fs[str(image_path)] = img
    return fake_save_files

def get_fake_delete_files_function_with_fs(fs: dict):
    async def fake_delete_files(paths):
        for path in paths:
            del fs[str(path)]
    return fake_delete_files