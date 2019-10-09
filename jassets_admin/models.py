from django.contrib.postgres.fields import JSONField
from django.db import models
from typing import Union
from uuid import UUID

from .validation.api import get_asset_validation_status
from .enums import AssetType


class JAssetsModel(models.Model):

    class Meta:
        abstract = True


class Platform(JAssetsModel):
    id = models.UUIDField(primary_key=True, unique=True)
    name = models.CharField(max_length=30)
    symbol = models.CharField(max_length=10, unique=True)
    main_asset_obj = models.ForeignKey(
        "Asset", db_column='main_asset',
        null=True, on_delete=models.SET_NULL,
        related_name='main_for_platform', to_field='uuid')

    def __str__(self):
        return f'{self.name} - {self.symbol}'

    class Meta:
        db_table = 'platforms'


class BaseAsset(JAssetsModel):
    id = models.IntegerField(primary_key=True)
    uuid = models.UUIDField(unique=True)
    name = models.CharField(max_length=50, null=True)
    description = models.TextField(blank=True)
    symbol = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=50, choices=AssetType.choices())
    is_active = models.BooleanField(default=True)
    address = models.CharField(max_length=42, unique=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.type} - {self.name} - {self.symbol}'

    class Meta:
        abstract = True


class Asset(BaseAsset):
    platform_obj = models.ForeignKey(
        "Platform", db_column='platform', null=True, on_delete=models.SET_NULL)
    properties = JSONField(null=True, blank=True)

    @property
    def validation_status(self):
        return get_asset_validation_status(self)

    @classmethod
    def set_active(cls, uuid: Union[str, UUID], is_active: bool):
        cls.objects.filter(uuid=uuid).update(is_active=is_active)

    class Meta:
        db_table = 'assets'


class Exchange(JAssetsModel):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=20, unique=True)
    url = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.name} - {self.slug}'

    class Meta:
        db_table = 'exchange'


class TradingPair(JAssetsModel):
    id = models.IntegerField(primary_key=True)
    base_asset_obj = models.ForeignKey(
        "Asset", db_column='base_asset', null=True, on_delete=models.SET_NULL,
        related_name='base_for_pair')
    quote_asset_obj = models.ForeignKey(
        "Asset", db_column='quote_asset', null=True, on_delete=models.SET_NULL,
        related_name='quote_for_pair')
    exchange_obj = models.ForeignKey(
        "Exchange", db_column='exchange', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=15)

    class Meta:
        db_table = 'trading_pairs'
        unique_together = ('base_asset_obj', 'quote_asset_obj', 'exchange_obj')

    def __str__(self):
        return f'{self.symbol}'
