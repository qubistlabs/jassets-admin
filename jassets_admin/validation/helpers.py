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
