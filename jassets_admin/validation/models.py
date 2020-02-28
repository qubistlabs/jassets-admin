import json

from typing import Optional, Union, List
from uuid import UUID
from django.db import models

from ..models import BaseAsset, Asset


class AssetHistory(BaseAsset):
    DRAFT = 'draft'
    PENDING = 'pending'
    APPLIED = 'applied'
    DISCARDED = 'discarded'
    STATE_CHOICES = (
        (DRAFT, 'Draft'),
        (PENDING, 'Pending'),
        (APPLIED, 'Applied'),
        (DISCARDED, 'Discarded'),
    )

    uuid = models.UUIDField()
    symbol = models.CharField(max_length=30)
    address = models.CharField(max_length=42, null=True)
    platform = models.UUIDField(null=True, blank=True)
    properties = models.TextField(null=True, blank=True)

    is_valid = models.BooleanField(verbose_name='Overall validation result', null=True)
    validation_results = models.TextField(null=True, blank=True)
    validation_time = models.DateTimeField(verbose_name='What time did the result come', null=True)
    result_message = models.TextField(
        blank=True, null=True, verbose_name='Error or information message from validator')
    user = models.ForeignKey(
        "auth.User", verbose_name='Who requested validation',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    validation_method = models.CharField(max_length=100, null=True)
    task_uuid = models.UUIDField(null=True)
    state = models.CharField(choices=STATE_CHOICES, max_length=100, default=APPLIED)

    @property
    def validation_results_dict(self):
        try:
            result = json.loads(self.validation_results)
        except (TypeError, json.JSONDecodeError):
            result = {}
        return result

    @classmethod
    def get_last(cls, asset: Asset) -> Optional['AssetHistory']:
        return cls.objects.filter(
            uuid=asset.uuid,
            state__in=(cls.APPLIED, cls.DISCARDED),
        ).order_by('validation_time').last()

    @classmethod
    def from_asset(cls, asset: Asset) -> 'AssetHistory':
        values = {
            'uuid': asset.uuid,
            'name': asset.name,
            'description': asset.description,
            'symbol': asset.symbol,
            'type': asset.type,
            'is_active': asset.is_active,
            'address': asset.address,
            'created': asset.created,
            'updated': asset.updated,
            'platform': asset.platform_obj_id,
            'properties': asset.properties,
            'state': AssetHistory.DRAFT,
        }
        result = AssetHistory(**values)
        return result

    class Meta:
        db_table = 'asset_history'
        verbose_name = 'Asset history'
        verbose_name_plural = 'Asset history'


class ValidationQueue(models.Model):
    """ Asset that waits for validation results """
    task_uuid = models.UUIDField(primary_key=True)
    asset_uuid = models.UUIDField()
    method = models.CharField(max_length=100)

    @classmethod
    def add(cls,
            task_uuid: Union[str, UUID],
            uuid: Union[str, UUID],
            method):
        item = cls(
            task_uuid=task_uuid,
            asset_uuid=uuid,
            method=method.value,
        )
        item.save()

    @classmethod
    def remove(cls, task_uuids: List[Union[str, UUID]]):
        cls.objects.filter(task_uuid__in=task_uuids).delete()

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def associated_assets_dict(cls):
        asset_uuids = tuple(cls.objects.values_list('asset_uuid', flat=True))
        return Asset.objects.filter(uuid__in=asset_uuids).in_bulk(field_name='uuid')

    @classmethod
    def remove_all(cls):
        cls.objects.all().delete()

    class Meta:
        db_table = 'validation_queue'
        verbose_name = 'Validation queue'
        verbose_name_plural = 'Validation queue'
