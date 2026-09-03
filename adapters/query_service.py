from sqlalchemy import text

from services.read_models import CatalogFiltersDTO, FilterColorDTO, FilterSizeDTO


class CatalogQueryService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_catalog_filters(
        self,
        category_name: str | None = None,
        collection_name: str | None = None,
    ) -> CatalogFiltersDTO:
        sql = """
            WITH filtered_tiles AS (
                SELECT * FROM catalog
                WHERE
                    (CAST(:category_name AS VARCHAR) IS NULL OR category_name = :category_name)
                    AND (
                        CAST(:collection_name AS VARCHAR) IS NULL
                        OR name ILIKE '%' || '"' || :collection_name || '"' || '%'
                    )
            )
            SELECT
                (SELECT json_agg(DISTINCT jsonb_build_object(
                    'id', ts.id,
                    'length', ts.length,
                    'width', ts.width,
                    'height', ts.height
                ))
                 FROM filtered_tiles ft
                 JOIN tile_sizes ts ON ft.size_id = ts.id) as sizes,

                (SELECT json_agg(DISTINCT jsonb_build_object(
                    'name', color_name,
                    'feature', feature_name
                ))
                 FROM filtered_tiles) as colors,

                (SELECT array_agg(DISTINCT producer_name)
                 FROM filtered_tiles) as producers;
        """

        async with self.session_factory.begin() as session:
            result = await session.execute(
                text(sql),
                {
                    "category_name": category_name,
                    "collection_name": collection_name,
                },
            )
            raw_sizes, raw_colors, raw_producers = result.tuples().one()

        return CatalogFiltersDTO(
            sizes=[FilterSizeDTO(**s) for s in (raw_sizes or [])],
            colors=[FilterColorDTO(**c) for c in (raw_colors or [])],
            producers=list(raw_producers or []),
        )
