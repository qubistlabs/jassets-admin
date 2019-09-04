from enum import Enum


class AssetType(Enum):
    FIAT = 'FIAT'
    COIN = 'COIN'
    TOKEN = 'TOKEN'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
