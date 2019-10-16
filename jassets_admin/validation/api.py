from django.utils.safestring import mark_safe

from .enums import (
    ValidationResultEnum,
    VALIDATION_METHODS_FOR_STATUS,
    VALIDATION_METHOD_VERBOSE_NAMES,
)
from .models import AssetHistory


def get_asset_validation_status(asset) -> str:
    """ Get string to show results of validation in assets table UI """

    result = []
    history_entry = AssetHistory.get_last(asset)
    results_dict = history_entry.validation_results_dict if history_entry else {}
    for method in VALIDATION_METHODS_FOR_STATUS:
        if method.value in results_dict:
            if results_dict[method.value] is True:
                status = ValidationResultEnum.VALID
            else:
                status = ValidationResultEnum.NOT_VALID
        else:
            status = ValidationResultEnum.UNKNOWN
        result.append((
            f'{VALIDATION_METHOD_VERBOSE_NAMES[method].capitalize()} '
            f'validation status is {status.value}'
        ))
    return mark_safe('<br/><hr/>'.join(result))

