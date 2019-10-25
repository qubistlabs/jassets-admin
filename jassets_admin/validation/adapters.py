import datetime
import json

from abc import ABC, abstractmethod
from typing import Dict, Type

from .enums import ValidationMethodEnum
from .helpers import asset_properties_to_dict
from .models import AssetHistory


class AssetValidationAdapter(ABC):

    def __init__(self, asset):
        self.asset = asset
        self.properties = asset_properties_to_dict(asset)

    @classmethod
    @abstractmethod
    def get_validation_method(cls):
        pass

    @abstractmethod
    def get_data(self):
        """ Get data for validation service """

    def store_result(self, is_valid, message):
        """ Save result from validation service """
        last_history_item = AssetHistory.get_last(self.asset)
        validation_results = last_history_item.validation_results_dict if last_history_item else {}
        history_entry = AssetHistory.from_asset(self.asset)
        history_entry.result_message = message
        history_entry.validation_time = datetime.datetime.now()
        self.modify_validation_results_dict(validation_results, is_valid)
        history_entry.is_valid = all((v is True for v in validation_results.values()))
        history_entry.validation_results = json.dumps(validation_results)
        history_entry.save()
        if self.asset.is_active != history_entry.is_valid:
            self.asset.is_active = history_entry.is_valid
            self.asset.save()

    def modify_validation_results_dict(self, validation_results, is_valid):
        validation_results[self.get_validation_method().value] = is_valid


class GasAmountAssetValidationAdapter(AssetValidationAdapter):
    @classmethod
    def get_validation_method(cls):
        return ValidationMethodEnum.GAS_AMOUNT

    def get_data(self):
        return [
            'https://main-node.jwallet.network',
            self.asset.address,
            self.properties.get('deployment_block'),
            self.properties.get('static_gas_amount'),
        ]


class TotalSupplyAssetValidationAdapter(AssetValidationAdapter):

    @classmethod
    def get_validation_method(cls):
        return ValidationMethodEnum.TOTAL_SUPPLY

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('total_supply'),
        ]


class MaxSupplyAssetValidationAdapter(AssetValidationAdapter):

    @classmethod
    def get_validation_method(cls):
        return ValidationMethodEnum.MAX_SUPPLY

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('max_supply'),
        ]


class CirculatingSupplyAssetValidationAdapter(AssetValidationAdapter):
    @classmethod
    def get_validation_method(cls):
        return ValidationMethodEnum.CIRCULATING_SUPPLY

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('circulating_supply'),
        ]


class AllSupplyTypesAssetValidationAdapter(AssetValidationAdapter):
    @classmethod
    def get_validation_method(cls):
        return ValidationMethodEnum.ALL_SUPPLY_TYPES

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('total_supply'),
            self.properties.get('max_supply'),
            self.properties.get('circulating_supply'),
        ]

    def modify_validation_results_dict(self, validation_results, is_valid):
        if isinstance(is_valid, bool):
            is_valid = [is_valid, is_valid, is_valid]
        validation_results[ValidationMethodEnum.TOTAL_SUPPLY.value] = is_valid[0]
        validation_results[ValidationMethodEnum.MAX_SUPPLY.value] = is_valid[1]
        validation_results[ValidationMethodEnum.CIRCULATING_SUPPLY.value] = is_valid[2]


ADAPTER_MAP: Dict[ValidationMethodEnum, Type[AssetValidationAdapter]] = {
    ValidationMethodEnum.GAS_AMOUNT: GasAmountAssetValidationAdapter,
    ValidationMethodEnum.TOTAL_SUPPLY: TotalSupplyAssetValidationAdapter,
    ValidationMethodEnum.MAX_SUPPLY: MaxSupplyAssetValidationAdapter,
    ValidationMethodEnum.CIRCULATING_SUPPLY: CirculatingSupplyAssetValidationAdapter,
    ValidationMethodEnum.ALL_SUPPLY_TYPES: AllSupplyTypesAssetValidationAdapter,
}
