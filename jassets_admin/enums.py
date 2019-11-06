from enum import Enum


class EnumWithChoices(Enum):
    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)


class AssetType(EnumWithChoices):
    FIAT = 'FIAT'
    COIN = 'COIN'
    TOKEN = 'TOKEN'


class AssetLinkType(EnumWithChoices):

    #: main asset website
    SITE = 'SITE'
    #: asset page on binance
    BINANCE = 'BINANCE'
    #: asset page on coinmarketcap
    COINMARKETCAP = 'COINMARKETCAP'
    #: asset github page
    GITHUB = 'GITHUB'
