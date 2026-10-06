import logging

from httpx import ASGITransport, AsyncClient
from contracts.images import GenerateImagesRequest, ImageVariant
from contracts.layers import ImageLayer, COLLECTIONS, SLIDES, PRODUCTS, DETAILS
from services.dto import GeneratedImage, GeneratedVariants

log = logging.getLogger(__name__)

class ImageHttpClient:

    def __init__(self, base_url, app=None):
        self._client = (
            AsyncClient(
                transport=ASGITransport(app=app),
                base_url=base_url,
            )
            if app
            else AsyncClient(base_url=base_url)
        )


    async def _generate_images(
        self,
        img: bytes,
        targets: tuple[ImageLayer, ...],
    ) -> GeneratedVariants:
        request = GenerateImagesRequest(
            data=img,
            targets=targets,
        )

        response = await self._client.post(
            "/generate-images",
            json=request.model_dump(mode="json"),
        )
        response.raise_for_status()

        variants = (
            ImageVariant.model_validate(item)
            for item in response.json()
        )

        return GeneratedVariants(
            GeneratedImage(
                layer=variant.target,
                data=variant.data,
            )
            for variant in variants
        )

    async def generate_product_variants(self, img: bytes):
        return await self._generate_images(img, (PRODUCTS, DETAILS))


    async def generate_collection_variants(self, img: bytes):
        return await self._generate_images(img, (COLLECTIONS,))


    async def generate_slide_variant(self, img: bytes):
        return await self._generate_images(img,(SLIDES,))


    async def close(self):
        await self._client.aclose()
