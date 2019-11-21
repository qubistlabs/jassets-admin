from datetime import datetime, timezone

from django.contrib.postgres.fields import JSONField
from django.db import models
from typing import Union
from uuid import UUID

from .enums import AssetType, AssetLinkType


class JAssetsModel(models.Model):

    class Meta:
        abstract = True


class Platform(JAssetsModel):
    id = models.UUIDField(primary_key=True, unique=True)
    name = models.CharField(max_length=30)
    symbol = models.CharField(max_length=10, unique=True)
    main_asset_obj = models.ForeignKey(
        "Asset", db_column='main_asset',
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name='main_for_platform', to_field='uuid')

    def __str__(self):
        return f'{self.name} - {self.symbol}'

    class Meta:
        db_table = 'platforms'
        managed = False


class BaseAsset(JAssetsModel):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True)
    symbol = models.CharField(max_length=30, unique=True)
    type = models.CharField(max_length=50, choices=AssetType.choices())
    is_active = models.BooleanField(default=True)
    address = models.CharField(max_length=42, unique=True, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.type} - {self.name} - {self.symbol}'

    class Meta:
        abstract = True


class Asset(BaseAsset):
    platform_obj = models.ForeignKey(
        "Platform", db_column='platform', null=True, blank=True, on_delete=models.SET_NULL)
    properties = JSONField(null=True, blank=True)

    class Meta:
        db_table = 'assets'
        managed = False

    @property
    def validation_status(self):
        from .validation.api import get_asset_validation_status

        return get_asset_validation_status(self)

    @classmethod
    def set_active(cls, uuid: Union[str, UUID], is_active: bool):
        cls.objects.filter(uuid=uuid).update(is_active=is_active)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.updated = datetime.now(tz=timezone.utc)
        super().save(force_insert, force_update, using, update_fields)


class Exchange(JAssetsModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=20, unique=True)
    url = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.name} - {self.slug}'

    class Meta:
        db_table = 'exchange'
        managed = False


class TradingPair(JAssetsModel):
    id = models.AutoField(primary_key=True)
    base_asset_obj = models.ForeignKey(
        "Asset", db_column='base_asset', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='base_for_pair')
    quote_asset_obj = models.ForeignKey(
        "Asset", db_column='quote_asset', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='quote_for_pair')
    exchange_obj = models.ForeignKey(
        "Exchange", db_column='exchange', on_delete=models.CASCADE)
    symbol = models.CharField(max_length=15)

    class Meta:
        db_table = 'trading_pairs'
        unique_together = ('base_asset_obj', 'quote_asset_obj', 'exchange_obj')
        managed = False

    def __str__(self):
        return f'{self.symbol}'


class AssetAttachment(JAssetsModel):
    """ File associated with asset """
    id = models.UUIDField(primary_key=True)
    asset = models.ForeignKey(
        "Asset", db_column='asset_id', on_delete=models.CASCADE)
    name = models.TextField(blank=True, null=True)
    version = models.TextField()
    path = models.TextField()
    metadata = JSONField(blank=True, null=True, default=dict)

    class Meta:
        db_table = 'asset_attachment'
        managed = False

    def __str__(self):
        return f'File {self.name or ""} {self.path}'


class AssetLink(JAssetsModel):
    """
    External asset link model.
    Used to display external links on asset page/screen.
    """
    id = models.AutoField(primary_key=True)
    asset_obj = models.ForeignKey('Asset', on_delete=models.CASCADE, db_column='asset')
    type = models.CharField(max_length=50, choices=AssetLinkType.choices())
    url = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'asset_links'

    def __str__(self):
        return f'Asset link {self.type} {self.url}'
