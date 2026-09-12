from pydantic import BaseModel, ConfigDict

from .layers import ImageLayer


conf_dict = ConfigDict(
    ser_json_bytes="base64",
    val_json_bytes="base64",
    extra="forbid",
)


class ImageVariant(BaseModel):
    model_config = conf_dict
    target: ImageLayer
    data: bytes
    extension: str



class GenerateImagesRequest(BaseModel):
    model_config = conf_dict

    data: bytes
    targets: tuple[ImageLayer, ...]

