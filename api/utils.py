from decimal import Decimal


def api_input_to_params(**input_params):
    if not input_params:
        return {}
    params = {}
    for k, v in input_params.items():
        if k == "size":
            length, width, height = v.split()
            params["size"] = {
                "length": Decimal(length),
                "width": Decimal(width),
                "height": Decimal(height),
            }
        elif k in {"box_area", "box_weight"}:
            box = params.get("box", {})
            box[k] = v
            params.update(box)
        elif k in {"color_name", "feature_name"}:
            color = params.get("color", {})
            color[k] = v
            params.update(color)
        else:
            params.update({k:v})

    return params


def strip_input_params(**params):
    for k, v in params.items():
        params[k] = v.strip()
    return params