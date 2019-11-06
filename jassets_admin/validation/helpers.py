import json


def asset_properties_to_dict(asset):
    result = {}
    if isinstance(asset.properties, dict):
        result = asset.properties
    elif isinstance(asset.properties, str):
        try:
            result = json.loads(asset.properties)
        except (TypeError, json.JSONDecodeError):
            pass
    return result


def create_bidirectional_dict(*args, **kwargs) -> dict:
    d = dict(*args, **kwargs)
    for k, v in list(d.items()):
        if v in d and k != v:
            raise ValueError(f"Value {v!r} already present as key")
        d[v] = k
    return d
