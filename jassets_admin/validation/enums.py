
from enum import Enum

from .adapters import (
    GasAmountAssetValidationAdapter,
    TotalSupplyAssetValidationAdapter,
    MaxSupplyAssetValidationAdapter,
    CirculatingSupplyAssetValidationAdapter,
    AllSupplyTypesAssetValidationAdapter,
)


class TaskState(Enum):
    queued = "queued"
    running = "running"
    failed = "failed"
    done = "done"


class ValidationMethodEnum(Enum):
    GAS_AMOUNT = 'gas_amount'
    TOTAL_SUPPLY = 'total_supply'
    MAX_SUPPLY = 'max_supply'
    CIRCULATING_SUPPLY = 'circulating_supply'
    ALL_SUPPLY_TYPES = 'all_supply_types'


VALIDATION_METHOD_VERBOSE_NAMES = {
    ValidationMethodEnum.GAS_AMOUNT: 'gas amount',
    ValidationMethodEnum.TOTAL_SUPPLY: 'total supply',
    ValidationMethodEnum.MAX_SUPPLY: 'max supply',
    ValidationMethodEnum.CIRCULATING_SUPPLY: 'circulating supply',
    ValidationMethodEnum.ALL_SUPPLY_TYPES: 'all supply types',
}

VALIDATION_METHODS_FOR_STATUS = [
    ValidationMethodEnum.GAS_AMOUNT,
    ValidationMethodEnum.TOTAL_SUPPLY,
    ValidationMethodEnum.MAX_SUPPLY,
    ValidationMethodEnum.CIRCULATING_SUPPLY,
]

ADAPTER_MAP = {
    ValidationMethodEnum.GAS_AMOUNT: GasAmountAssetValidationAdapter,
    ValidationMethodEnum.TOTAL_SUPPLY: TotalSupplyAssetValidationAdapter,
    ValidationMethodEnum.MAX_SUPPLY: MaxSupplyAssetValidationAdapter,
    ValidationMethodEnum.CIRCULATING_SUPPLY: CirculatingSupplyAssetValidationAdapter,
    ValidationMethodEnum.ALL_SUPPLY_TYPES: AllSupplyTypesAssetValidationAdapter,
}


class ValidationResultEnum(Enum):
    VALID = 'VALID'
    NOT_VALID = 'NOT VALID'
    UNKNOWN = 'UNKNOWN'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

