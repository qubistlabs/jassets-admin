from typing import Optional, Union, List
from uuid import UUID
from django.db import models

from ..models import BaseAsset, Asset

from .enums import ValidationMethodEnum


class AssetHistory(BaseAsset):
    uuid = models.UUIDField()
    symbol = models.CharField(max_length=30)
    address = models.CharField(max_length=42)
    platform = models.UUIDField(null=True, blank=True)
    properties = models.TextField(null=True, blank=True)

    is_valid = models.BooleanField(verbose_name='Validation result')
    validation_time = models.DateTimeField(verbose_name='What time did the result come')
    result_message = models.TextField(
        blank=True, null=True, verbose_name='Error or information message from validator')
    user = models.ForeignKey(
        "auth.User", verbose_name='Who requested validation',
        on_delete=models.SET_NULL, null=True, blank=True,
    )

    @classmethod
    def from_asset(cls, uuid) -> Optional['AssetHistory']:
        values = Asset.objects.filter(uuid=uuid).values().first()
        if values is None:
            result = None
        else:
            values.pop('id')
            values['platform'] = values.pop('platform_obj_id')
            result = AssetHistory(**values)
        return result

    class Meta:
        db_table = 'asset_history'
        verbose_name = 'Asset history'
        verbose_name_plural = 'Asset history'


class ValidationQueue(models.Model):
    task_uuid = models.UUIDField(primary_key=True)
    asset_uuid = models.UUIDField()
    method = models.CharField(max_length=100)

    @classmethod
    def add(cls,
            task_uuid: Union[str, UUID],
            uuid: Union[str, UUID],
            method: ValidationMethodEnum):
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

    class Meta:
        db_table = 'validation_queue'
        verbose_name = 'Validation queue'
        verbose_name_plural = 'Validation queue'
