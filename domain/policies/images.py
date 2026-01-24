from PIL import Image, ImageOps

def resize_image(
    img: Image.Image,
    target_size: tuple[int, int],
    mode: str,
) -> Image.Image:
    if mode == "fit":
        img.thumbnail(target_size, Image.LANCZOS)
        return img

    if mode == "cover":
        return ImageOps.fit(
            img,
            target_size,
            method=Image.LANCZOS,
            centering=(0.5, 0.5),
        )

    raise ValueError(f"Unknown resize mode: {mode}")