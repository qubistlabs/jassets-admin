from enum import Enum

from jassets_admin.enums import EnumWithChoices


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
    DEPLOYMENT_TIMESTAMP = 'deployment_timestamp'
    TRANSFERS_STARTED_TIMESTAMP = 'transfers_started_timestamp'
    TRANSFERS_STARTED_TIMESTAMP_GETTER = 'transfers_started_timestamp_getter'
    COINMARKETCAP_LINK_GETTER = 'coinmarketcap_link_getter'
    SYMBOL_AND_ADDRESS = 'symbol_and_address'
    CONTRACT_METHODS = 'contract_methods'
    DECIMALS = 'decimals'
    NAME = 'name'
    DESCRIPTION = 'description'


VALIDATION_METHOD_ACTION_NAME = {
    ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP_GETTER: 'Fill transfers started timestamp',
    ValidationMethodEnum.GAS_AMOUNT: 'Validate gas amount',
    ValidationMethodEnum.TOTAL_SUPPLY: 'Validate total supply',
    ValidationMethodEnum.MAX_SUPPLY: 'Validate max supply',
    ValidationMethodEnum.CIRCULATING_SUPPLY: 'Validate circulating supply',
    ValidationMethodEnum.ALL_SUPPLY_TYPES: 'Validate all supply types',
    ValidationMethodEnum.DEPLOYMENT_BLOCK: 'Validate deployment block number',
    ValidationMethodEnum.DEPLOYMENT_TIMESTAMP: 'Validate deployment timestamp',
    ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP: 'Validate transfers started timestamp',
    ValidationMethodEnum.SYMBOL_AND_ADDRESS: 'Validate asset symbol and address',
    ValidationMethodEnum.CONTRACT_METHODS: 'Validate contract methods and their signatures',
    ValidationMethodEnum.DECIMALS: 'Validate asset decimals',
    ValidationMethodEnum.NAME: 'Validate asset name',
    ValidationMethodEnum.DESCRIPTION: 'Validate asset description',
}

VALIDATION_METHODS_FOR_STATUS = {
    ValidationMethodEnum.GAS_AMOUNT: 'Gas amount',
    ValidationMethodEnum.TOTAL_SUPPLY: 'Total supply',
    ValidationMethodEnum.MAX_SUPPLY: 'Max supply',
    ValidationMethodEnum.CIRCULATING_SUPPLY: 'Circulating supply',
    ValidationMethodEnum.DEPLOYMENT_BLOCK: 'Deployment block number',
    ValidationMethodEnum.DEPLOYMENT_TIMESTAMP: 'Deployment timestamp',
    ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP: 'Transfers started timestamp',
    ValidationMethodEnum.SYMBOL_AND_ADDRESS: 'Symbol and address',
    ValidationMethodEnum.CONTRACT_METHODS: 'Contract methods',
    ValidationMethodEnum.DECIMALS: 'Decimals',
    ValidationMethodEnum.NAME: 'Name',
    ValidationMethodEnum.DESCRIPTION: 'Description',
}


class ValidationResultEnum(Enum):
    VALID = 'VALID'
    NOT_VALID = 'NOT VALID'
    UNKNOWN = 'UNKNOWN'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class AssetLinkSource(EnumWithChoices):
    COINMARKETCAP = 'coinmarketcap'


ASSET_LINK_SOURCE_TO_METHOD = {
    AssetLinkSource.COINMARKETCAP: ValidationMethodEnum.COINMARKETCAP_LINK_GETTER,
}
