import json


class AssetValidationProxy:

    def __init__(self, asset):
        self.asset = asset
        try:
            self.properties = json.loads(asset.properties)
        except (TypeError, json.JSONDecodeError):
            self.properties = {}

    def get_data(self):
        raise NotImplementedError()


class GasAmountAssetValidationProxy(AssetValidationProxy):

    def get_data(self):
        return [
            'https://main-node.jwallet.network',
            str(self.asset.uuid),
            self.properties.get('deployment_block'),
            self.properties.get('static_gas_amount'),
        ]


class TotalSupplyAssetValidationProxy(AssetValidationProxy):

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('total_supply'),
        ]


class MaxSupplyAssetValidationProxy(AssetValidationProxy):

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('max_supply'),
        ]


class CirculatingSupplyAssetValidationProxy(AssetValidationProxy):

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('circulating_supply'),
        ]


class AllSupplyTypesAssetValidationProxy(AssetValidationProxy):

    def get_data(self):
        return [
            self.asset.symbol,
            self.properties.get('total_supply'),
            self.properties.get('max_supply'),
            self.properties.get('circulating_supply'),
        ]
