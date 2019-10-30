from django.utils.safestring import mark_safe

from .enums import (
    ValidationResultEnum,
    VALIDATION_METHODS_FOR_STATUS,
)
from .models import AssetHistory


def get_asset_validation_status(asset) -> str:
    """ Get string to show results of validation in assets table UI """

    result = []
    history_entry = AssetHistory.get_last(asset)
    results_dict = history_entry.validation_results_dict if history_entry else {}
    for method, name in VALIDATION_METHODS_FOR_STATUS.items():
        if method.value in results_dict:
            if results_dict[method.value] is True:
                status = ValidationResultEnum.VALID
            else:
                status = ValidationResultEnum.NOT_VALID
        else:
            status = ValidationResultEnum.UNKNOWN
        result.append((
            f'{name}: {status.value}'
        ))
    return mark_safe('<br/><hr/>'.join(result))


def is_asset_valid(asset, method) -> str:
    """ Is asset valid for one for one validation method """
    history_entry = AssetHistory.get_last(asset)
    results_dict = history_entry.validation_results_dict if history_entry else {}
    return results_dict.get(method.value, False)
