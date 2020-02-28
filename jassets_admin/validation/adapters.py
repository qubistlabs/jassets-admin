import json

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Type
from django.conf import settings

from ..enums import AssetLinkType
from ..models import AssetLink
from ..exceptions import ShowError

from .api import is_asset_valid
from .enums import ValidationMethodEnum, VALIDATION_METHODS_FOR_STATUS, TaskState
from .helpers import asset_properties_to_dict, create_bidirectional_dict
from .models import AssetHistory


class AssetValidationAdapter(ABC):

    need_approval = False

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

    def store_result(self, task_uuid, result, message, task_state):
        """ Save result from validation service """
        self._update_history_entry(task_uuid, result, message)
        if not self.need_approval and task_state == TaskState.done:
            is_modified = self.modify_asset(result, message)
            if is_modified:
                self.asset.save()

    def result_approval(self, history_entry, is_approved):
        """ Must be invoked when getter needs additional approval to perform modify_asset """
        assert self.need_approval
        if is_approved:
            result = self.get_result_from_validation_results_dict(
                history_entry.validation_results_dict
            )
            is_modified = self.modify_asset(result, history_entry.result_message)
            if is_modified:
                self.asset.save()
            history_entry.state = AssetHistory.APPLIED
        else:
            history_entry.state = AssetHistory.DISCARDED
        history_entry.save()

    def create_history_entry(self, task_uuid, user):
        history_entry = AssetHistory.from_asset(self.asset)
        history_entry.user = user
        history_entry.task_uuid = task_uuid
        history_entry.validation_method = self.get_validation_method().value

        last_history_item = AssetHistory.get_last(self.asset)
        if last_history_item:
            history_entry.validation_results = last_history_item.validation_results_dict
        else:
            history_entry.validation_results = {}
        history_entry.save()
        return history_entry

    @classmethod
    def get_result_from_validation_results_dict(cls, validation_results):
        return validation_results.get(cls.get_validation_method().value)

    def modify_asset(self, result, message) -> bool:
        """ Make changes in asset and if asset need to be saved return True """
        return False

    def _update_history_entry(self, task_uuid, result, message):
        try:
            history_entry = AssetHistory.objects.get(
                task_uuid=task_uuid,
                state=AssetHistory.DRAFT,
            )
        except AssetHistory.DoesNotExist:
            history_entry = self.create_history_entry(task_uuid, None)
        history_entry.result_message = message
        validation_results = history_entry.validation_results_dict

        history_entry.validation_time = datetime.now(tz=timezone.utc)
        self._modify_validation_results_dict(validation_results, result)
        history_entry.is_valid = all(
            v is True for k, v in validation_results.items()
            if ValidationMethodEnum(k) in VALIDATION_METHODS_FOR_STATUS
        )
        history_entry.validation_results = json.dumps(validation_results)
        if self.need_approval:
            history_entry.state = AssetHistory.PENDING
        else:
            history_entry.state = AssetHistory.APPLIED
        history_entry.save()
        return history_entry

    def _modify_validation_results_dict(self, validation_results, result):
        validation_results[self.get_validation_method().value] = result

    def _modify_asset_property(self, key, value) -> bool:
        """ Assign value to asset properties dict and if asset need to be saved return True """
        if value is None:
            return False

        need_to_save = False
        if self.asset.properties is None:
            self.asset.properties = {}
        if self.asset.properties.get(key) != value:
            self.asset.properties[key] = value
            need_to_save = True
        return need_to_save


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
    real_validation_methods = (
        ValidationMethodEnum.TOTAL_SUPPLY,
        ValidationMethodEnum.MAX_SUPPLY,
        ValidationMethodEnum.CIRCULATING_SUPPLY,
    )

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

    def _modify_validation_results_dict(self, validation_results, results):
        if not isinstance(results, list):
            results = [results] * 3

        for result, method in zip(results, self.real_validation_methods):
            validation_results[method.value] = result

    @classmethod
    def get_result_from_validation_results_dict(cls, validation_results):
        return tuple(validation_results.get(vm.value) for vm in cls.real_validation_methods)


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
        return self._modify_asset_property('transfers_started_timestamp', result)


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
        if not isinstance(result, dict):
            return False
        need_to_save = False
        for attr in ('total_supply', 'max_supply', 'circulating_supply'):
            need_to_save |= self._modify_asset_property(attr, result.get(attr))
        return need_to_save


class GasAmountGetterAdapter(AssetValidationAdapter):

    need_approval = True

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
        return self._modify_asset_property('static_gas_amount', result)


class CMCVolume24hGetterAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.CMC_VOLUME24H_GETTER

    def get_data(self):
        return [
            self.asset.symbol,
        ]

    def modify_asset(self, result, message) -> bool:
        return self._modify_asset_property('cmc_volume24h', result)


class DecimalsGetterAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.DECIMALS_GETTER

    def get_data(self):
        return [
            settings.ETH_NODE,
            self.asset.address,
        ]

    def modify_asset(self, result, message) -> bool:
        return self._modify_asset_property('decimals', result)


class NameGetterAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.NAME_GETTER

    def get_data(self):
        return [
            self.asset.symbol,
        ]

    def modify_asset(self, result, message) -> bool:
        if self.asset.name != result:
            self.asset.name = result
            return True
        return False


class DescriptionGetterAdapter(AssetValidationAdapter):
    @staticmethod
    def get_validation_method():
        return ValidationMethodEnum.DESCRIPTION_GETTER

    def get_data(self):
        return [
            self.asset.symbol,
        ]

    def modify_asset(self, result, message) -> bool:
        if self.asset.description != result:
            self.asset.description = result
            return True
        return False


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
    ValidationMethodEnum.CMC_VOLUME24H_GETTER: CMCVolume24hGetterAdapter,
    ValidationMethodEnum.DECIMALS_GETTER: DecimalsGetterAdapter,
    ValidationMethodEnum.NAME_GETTER: NameGetterAdapter,
    ValidationMethodEnum.DESCRIPTION_GETTER: DescriptionGetterAdapter,
}
