from enum import Enum


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
    DEPLOYMENT_BLOCK = 'deployment_block'
    TRANSFERS_STARTED_TIMESTAMP = 'transfers_started_timestamp'
    TRANSFERS_STARTED_TIMESTAMP_GETTER = 'transfers_started_timestamp_getter'


VALIDATION_METHOD_ACTION_NAME = {
    ValidationMethodEnum.GAS_AMOUNT: 'Validate gas amount',
    ValidationMethodEnum.TOTAL_SUPPLY: 'Validate total supply',
    ValidationMethodEnum.MAX_SUPPLY: 'Validate max supply',
    ValidationMethodEnum.CIRCULATING_SUPPLY: 'Validate circulating supply',
    ValidationMethodEnum.ALL_SUPPLY_TYPES: 'Validate all supply types',
    ValidationMethodEnum.DEPLOYMENT_BLOCK: 'Validate deployment block number',
    ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP: 'Validate transfers started timestamp',
    ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP_GETTER: 'Fill transfers started timestamp',
}

VALIDATION_METHODS_FOR_STATUS = {
    ValidationMethodEnum.GAS_AMOUNT: 'Gas amount',
    ValidationMethodEnum.TOTAL_SUPPLY: 'Total supply',
    ValidationMethodEnum.MAX_SUPPLY: 'Max supply',
    ValidationMethodEnum.CIRCULATING_SUPPLY: 'Circulating supply',
    ValidationMethodEnum.DEPLOYMENT_BLOCK: 'Deployment block number',
    ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP: 'Transfers started timestamp',
}


class ValidationResultEnum(Enum):
    VALID = 'VALID'
    NOT_VALID = 'NOT VALID'
    UNKNOWN = 'UNKNOWN'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
