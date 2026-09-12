from dataclasses import dataclass
from collections.abc import Iterator, Iterable
from contracts.layers import ImageLayer


@dataclass(frozen=True, slots=True)
class GeneratedImage:
    layer: ImageLayer
    data: bytes
    #extension: str


class GeneratedVariants:
    __slots__ = ("_images",)

    def __init__(self, images: Iterable[GeneratedImage]):
        self._images = tuple(images)

    def __iter__(self) -> Iterator[GeneratedImage]:
        return iter(self._images)