from contracts.layers import ImageLayer, COLLECTIONS, SLIDES, PRODUCTS, DETAILS
from services.dto import GeneratedImage, GeneratedVariants



class FakeImageGenerator:
    async def _generate_images(
        self,
        img: bytes,
        targets: tuple[ImageLayer, ...],
    ) -> GeneratedVariants:
        return GeneratedVariants(
            GeneratedImage(
                layer=target,
                data=b"fake-image-data",
            )
            for target in targets
        )

    async def generate_product_variants(
        self,
        img: bytes,
    ) -> GeneratedVariants:
        return await self._generate_images(
            img,
            (PRODUCTS, DETAILS),
        )

    async def generate_collection_variants(
        self,
        img: bytes,
    ) -> GeneratedVariants:
        return await self._generate_images(
            img,
            (COLLECTIONS,),
        )

    async def generate_slide_variant(
        self,
        img: bytes,
    ) -> GeneratedVariants:
        return await self._generate_images(
            img,
            (SLIDES,),
        )

