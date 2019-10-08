from typing import Optional

from jassets_admin.validation.enums import ValidationResultEnum


def is_asset_valid(uuid) -> Optional[bool]:
    from .models import AssetHistory

    result = AssetHistory.objects.filter(
        uuid=uuid
    ).order_by(
        'validation_time'
    ).values_list(
        'is_valid', flat=True
    ).last()
    return result


def get_asset_validation_status(uuid) -> str:
    validity = is_asset_valid(uuid)
    if validity is True:
        result = ValidationResultEnum.VALID
    elif validity is False:
        result = ValidationResultEnum.NOT_VALID
    else:
        result = ValidationResultEnum.UNKNOWN
    return str(result.value)

