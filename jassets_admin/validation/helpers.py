
from .enums import ValidationMethodEnum
from .proxies import (
    GasAmountAssetValidationProxy,
    TotalSupplyAssetValidationProxy,
    MaxSupplyAssetValidationProxy,
    CirculatingSupplyAssetValidationProxy,
    AllSupplyTypesAssetValidationProxy,
)


PROXY_MAP = {
    ValidationMethodEnum.GAS_AMOUNT: GasAmountAssetValidationProxy,
    ValidationMethodEnum.TOTAL_SUPPLY: TotalSupplyAssetValidationProxy,
    ValidationMethodEnum.MAX_SUPPLY: MaxSupplyAssetValidationProxy,
    ValidationMethodEnum.CIRCULATING_SUPPLY: CirculatingSupplyAssetValidationProxy,
    ValidationMethodEnum.ALL_SUPPLY_TYPES: AllSupplyTypesAssetValidationProxy,
}


def get_proxy(value: 'ValidationMethodEnum'):
    return PROXY_MAP[value]
