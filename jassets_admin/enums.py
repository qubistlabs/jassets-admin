from enum import Enum


class AssetType(Enum):
    FIAT = 'fiat'
    COIN = 'coin'
    TOKEN = 'token'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.name) for i in cls)
