
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

    @classmethod
    def get_verbose_name(cls, value: 'ValidationMethodEnum') -> str:
        names = {
            cls.GAS_AMOUNT: 'gas amount',
            cls.TOTAL_SUPPLY: 'total supply',
            cls.MAX_SUPPLY: 'max supply',
            cls.CIRCULATING_SUPPLY: 'circulating supply',
            cls.ALL_SUPPLY_TYPES: 'all supply types',
        }
        return 'Validate {}'.format(names.get(value, ''))


class ValidationResultEnum(Enum):
    VALID = 'VALID'
    NOT_VALID = 'NOT VALID'
    UNKNOWN = 'UNKNOWN'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

