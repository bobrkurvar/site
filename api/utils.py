# from decimal import Decimal
#
# def api_input_to_params(**input_params):
#     if not input_params:
#         return {}
#     params = {}
#     for k, v in input_params.items():
#         if k == "size":
#             length, width, height = v.split()
#             params["size"] = {
#                 "length": Decimal(length),
#                 "width": Decimal(width),
#                 "height": Decimal(height),
#             }
#         elif k in {"box_area", "box_weight"}:
#             box = params.get("box", {})
#             box[k] = v
#             params.update(box)
#         elif k in {"color_name", "feature_name"}:
#             color = params.get("color", {})
#             color[k] = v
#             params.update(color)
#         else:
#             params.update({k: v})
#
#     return params
#
#
# def strip_input_params(**params):
#     for k, v in params.items():
#         params[k] = v.strip()
#     return params

from decimal import Decimal
from typing import Annotated

from fastapi import Form

from .schemas import CreateTile, UpdateTile


def create_tile_form(
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color_name: Annotated[str, Form()],
    producer_name: Annotated[str, Form()],
    box_weight: Annotated[Decimal, Form()],
    box_area: Annotated[Decimal, Form()],
    boxes_count: Annotated[int, Form()],
    category_name: Annotated[str, Form()],
    feature_name: Annotated[str | None, Form()] = None,
    surface_name: Annotated[str | None, Form()] = None,
) -> CreateTile:
    return CreateTile(
        name=name,
        size=size,
        color_name=color_name,
        producer_name=producer_name,
        box_weight=box_weight,
        box_area=box_area,
        boxes_count=boxes_count,
        category_name=category_name,
        feature_name=feature_name,
        surface_name=surface_name,
    )


def update_tile_form(
    article: Annotated[int, Form()],
    name: Annotated[str, Form()],
    size: Annotated[str, Form()],
    color_name: Annotated[str, Form()],
    producer_name: Annotated[str, Form()],
    box_weight: Annotated[Decimal | str, Form()],
    box_area: Annotated[Decimal | str, Form()],
    boxes_count: Annotated[int | str, Form()],
    category_name: Annotated[str, Form()],
    feature_name: Annotated[str, Form()],
    surface_name: Annotated[str, Form()],
) -> UpdateTile:
    return UpdateTile(
        article=article,
        name=name,
        size=size,
        color_name=color_name,
        producer_name=producer_name,
        box_weight=box_weight,
        box_area=box_area,
        boxes_count=boxes_count,
        category_name=category_name,
        feature_name=feature_name,
        surface_name=surface_name,
    )
