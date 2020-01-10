import json

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Type
from django.conf import settings

from ..enums import AssetLinkType
from ..models import AssetLink
from ..exceptions import ShowError

from .api import is_asset_valid
from .enums import ValidationMethodEnum, VALIDATION_METHODS_FOR_STATUS
from .helpers import asset_properties_to_dict, create_bidirectional_dict
from .models import AssetHistory


class AssetValidationAdapter(ABC):

    def __init__(self, asset, *args, **kwargs):
        self.asset = asset
        self.properties = asset_properties_to_dict(asset)
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    @abstractmethod
    def get_validation_method():
        pass

    @abstractmethod
    def get_data(self):
        """ Get data for validation service """

    def store_result(self, result, message):
        """ Save result from validation service """
        self._create_history_entry(result, message)
        is_modified = self.modify_asset(result, message)
        if is_modified:
            self.asset.save()

    def _create_history_entry(self, result, message):
        last_history_item = AssetHistory.get_last(self.asset)
        validation_results = last_history_item.validation_results_dict if last_history_item else {}
        history_entry = AssetHistory.from_asset(self.asset)
        history_entry.result_message = message
        history_entry.validation_time = datetime.now(tz=timezone.utc)
        self.modify_validation_results_dict(validation_results, result)
        history_entry.is_valid = all(
            v is True for k, v in validation_results.items()
            if ValidationMethodEnum(k) in VALIDATION_METHODS_FOR_STATUS
        )
        history_entry.validation_results = json.dumps(validation_results)
        history_entry.save()
        return history_entry

    def modify_validation_results_dict(self, validation_results, result):
        validation_results[self.get_validation_method().value] = result

    def modify_asset(self, result, message) -> bool:
        """ Make changes in asset and if asset need to be saved return True """
        return False


class GasAmountAssetValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.GAS_AMOUNT

    def get_data(self):
        return [
            settings.ETH_NODE,
            self.asset.address,
            self.properties.get('deployment_block'),
            self.properties.get('static_gas_amount'),
        ]


class TotalSupplyAssetValidationAdapter(AssetValidationAdapter):

    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.TOTAL_SUPPLY

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('total_supply'),
        ]


class MaxSupplyAssetValidationAdapter(AssetValidationAdapter):

    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.MAX_SUPPLY

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('max_supply'),
        ]


class CirculatingSupplyAssetValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.CIRCULATING_SUPPLY

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('circulating_supply'),
        ]


class AllSupplyTypesAssetValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.ALL_SUPPLY_TYPES

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('total_supply'),
            self.properties.get('max_supply'),
            self.properties.get('circulating_supply'),
        ]

    def modify_validation_results_dict(self, validation_results, results):
        if not isinstance(results, list):
            results = [results] * 3
        methods = (
            ValidationMethodEnum.TOTAL_SUPPLY,
            ValidationMethodEnum.MAX_SUPPLY,
            ValidationMethodEnum.CIRCULATING_SUPPLY,
        )
        for result, method in zip(results, methods):
            validation_results[method.value] = result


class DeploymentBlockValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.DEPLOYMENT_BLOCK

    def get_data(self):
        return [
            settings.ETH_NODE,
            self.asset.address,
            self.properties.get('deployment_block'),
        ]


class DeploymentTimestampValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.DEPLOYMENT_TIMESTAMP

    def get_data(self):
        return [
            settings.ETH_NODE,
            self.asset.address,
            self.properties.get('deployment_timestamp'),
        ]


class TransfersStartedTimestampValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP

    def get_data(self):
        if not is_asset_valid(self.asset, ValidationMethodEnum.DEPLOYMENT_BLOCK):
            raise ShowError('Deployment block number must be valid to perform this validation')
        return [
            settings.ETH_NODE,
            self.asset.address,
            self.properties.get('transfers_started_timestamp'),
            self.properties.get('deployment_block'),
        ]


class TransfersStartedTimestampGetterAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP_GETTER

    def get_data(self):
        if not is_asset_valid(self.asset, ValidationMethodEnum.DEPLOYMENT_BLOCK):
            raise ShowError('Deployment block number must be valid to perform this action')
        return [
            settings.ETH_NODE,
            self.asset.address,
            self.properties.get('deployment_block'),
        ]

    def modify_asset(self, result, message) -> bool:
        self.asset.properties['transfers_started_timestamp'] = result
        return True


class LinksGetterAdapter(AssetValidationAdapter, ABC):

    link_slugs_dict: Dict = {}

    def get_data(self):
        link_types = (AssetLinkType(t) for t in self.args)
        link_slugs = [self.link_slugs_dict[k] for k in link_types if k in self.link_slugs_dict]
        return [
            self.get_asset_identifier(),
            link_slugs,
        ]

    def modify_asset(self, result, message) -> bool:
        if result is None:
            return False
        objs = []
        for key, values in result.items():
            link_type = self.link_slugs_dict.get(key)
            if not isinstance(link_type, AssetLinkType):
                continue
            for v in values:
                objs.append(
                    AssetLink(
                        asset_obj=self.asset,
                        type=link_type.value,
                        url=v,
                    )
                )
        AssetLink.objects.bulk_create(objs)
        return False

    @abstractmethod
    def get_asset_identifier(self):
        """ Asset identifier """


class CoinMarketCapLinksGetterAdapter(LinksGetterAdapter):

    link_slugs_dict = create_bidirectional_dict(
        website=AssetLinkType.SITE,
        source_code=AssetLinkType.GITHUB,
    )

    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.COINMARKETCAP_LINK_GETTER

    def get_asset_identifier(self):
        return self.asset.symbol


class EtherscanLinksGetterAdapter(LinksGetterAdapter):

    link_slugs_dict = create_bidirectional_dict(
        site=AssetLinkType.SITE,
        Binance=AssetLinkType.BINANCE,
        CoinMarketCap=AssetLinkType.COINMARKETCAP,
        Github=AssetLinkType.GITHUB,
    )

    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.ETHERSCAN_LINK_GETTER

    def get_asset_identifier(self):
        return self.asset.address


class SymbolAndAddressValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.SYMBOL_AND_ADDRESS

    def get_data(self):
        return [
            self.asset.symbol,
            self.asset.address,
        ]


class ContractMethodsValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.CONTRACT_METHODS

    def get_data(self):
        return [
            settings.ETH_NODE,
            self.asset.address,
        ]


class DecimalsValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.DECIMALS

    def get_data(self):
        return [
            settings.ETH_NODE,
            self.asset.address,
            self.properties.get('decimals'),
        ]


class NameValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.NAME

    def get_data(self):
        return [
            self.asset.symbol,
            self.asset.name,
        ]


class DescriptionValidationAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.DESCRIPTION

    def get_data(self):
        return [
            self.asset.symbol,
            self.asset.description,
        ]


class AllSupplyTypesGetterAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.ALL_SUPPLY_TYPES_GETTER

    def get_data(self):
        return [
            self.asset.symbol,
        ]

    def modify_asset(self, result, message) -> bool:
        default_value = None
        if not isinstance(result, dict):
            default_value = result
            result = {}
        if self.asset.properties is None:
            self.asset.properties = {}
        for attr in ('total_supply', 'max_supply', 'circulating_supply'):
            self.asset.properties[attr] = result.get(attr, default_value)
        return True


class GasAmountGetterAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.GAS_AMOUNT_GETTER

    def get_data(self):
        return [
            settings.ETH_NODE,
            self.asset.address,
            self.properties.get('deployment_block'),
        ]

    def modify_asset(self, result, message) -> bool:
        if self.asset.properties is None:
            self.asset.properties = {}
        self.asset.properties['static_gas_amount'] = result
        return True


ADAPTER_MAP: Dict[ValidationMethodEnum, Type[AssetValidationAdapter]] = {
    ValidationMethodEnum.GAS_AMOUNT: GasAmountAssetValidationAdapter,
    ValidationMethodEnum.GAS_AMOUNT_GETTER: GasAmountGetterAdapter,
    ValidationMethodEnum.TOTAL_SUPPLY: TotalSupplyAssetValidationAdapter,
    ValidationMethodEnum.MAX_SUPPLY: MaxSupplyAssetValidationAdapter,
    ValidationMethodEnum.CIRCULATING_SUPPLY: CirculatingSupplyAssetValidationAdapter,
    ValidationMethodEnum.ALL_SUPPLY_TYPES: AllSupplyTypesAssetValidationAdapter,
    ValidationMethodEnum.DEPLOYMENT_BLOCK: DeploymentBlockValidationAdapter,
    ValidationMethodEnum.DEPLOYMENT_TIMESTAMP: DeploymentTimestampValidationAdapter,
    ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP: TransfersStartedTimestampValidationAdapter,
    ValidationMethodEnum.TRANSFERS_STARTED_TIMESTAMP_GETTER: TransfersStartedTimestampGetterAdapter,
    ValidationMethodEnum.COINMARKETCAP_LINK_GETTER: CoinMarketCapLinksGetterAdapter,
    ValidationMethodEnum.ETHERSCAN_LINK_GETTER: EtherscanLinksGetterAdapter,
    ValidationMethodEnum.SYMBOL_AND_ADDRESS: SymbolAndAddressValidationAdapter,
    ValidationMethodEnum.CONTRACT_METHODS: ContractMethodsValidationAdapter,
    ValidationMethodEnum.DECIMALS: DecimalsValidationAdapter,
    ValidationMethodEnum.NAME: NameValidationAdapter,
    ValidationMethodEnum.DESCRIPTION: DescriptionValidationAdapter,
    ValidationMethodEnum.ALL_SUPPLY_TYPES_GETTER: AllSupplyTypesGetterAdapter,
}
