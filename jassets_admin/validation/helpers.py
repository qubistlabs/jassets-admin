
from .enums import ValidationMethodEnum
from .adapters import (
    GasAmountAssetValidationAdapter,
    TotalSupplyAssetValidationAdapter,
    MaxSupplyAssetValidationAdapter,
    CirculatingSupplyAssetValidationAdapter,
    AllSupplyTypesAssetValidationAdapter,
)


PROXY_MAP = {
    ValidationMethodEnum.GAS_AMOUNT: GasAmountAssetValidationAdapter,
    ValidationMethodEnum.TOTAL_SUPPLY: TotalSupplyAssetValidationAdapter,
    ValidationMethodEnum.MAX_SUPPLY: MaxSupplyAssetValidationAdapter,
    ValidationMethodEnum.CIRCULATING_SUPPLY: CirculatingSupplyAssetValidationAdapter,
    ValidationMethodEnum.ALL_SUPPLY_TYPES: AllSupplyTypesAssetValidationAdapter,
}


def get_adapter(value: 'ValidationMethodEnum'):
    return PROXY_MAP[value]
