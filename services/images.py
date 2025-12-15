# from PIL import Image
# from pathlib import Path
#
# IMAGE_SIZES = {
#     "tile": [
#         (320, 200),
#         (480, 300),
#         (640, 400),
#     ]
# }
#
# def resize_image(
#     input_path: Path,
#     output_dir: Path,
#     image_type: str = "tile",
#     quality: int = 82
# ):
#     output_dir.mkdir(parents=True, exist_ok=True)
#
#     with Image.open(input_path) as img:
#         img = img.convert("RGB")
#
#         for w, h in IMAGE_SIZES[image_type]:
#             resized = img.resize((w, h), Image.LANCZOS)
#
#             out_path = output_dir / f"{input_path.stem}_{w}x{h}.jpg"
#             resized.save(
#                 out_path,
#                 "JPEG",
#                 quality=quality,
#                 optimize=True,
#                 progressive=True,
#             )
#
#             print(f"✔ saved {out_path}")
