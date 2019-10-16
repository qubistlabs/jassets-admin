from pathlib import Path
from typing import List
from uuid import uuid4
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.fields.files import FieldFile
from django.db.models.manager import BaseManager

from .helpers import get_file_hash
from .manifest import FileManifest
from .query import StaticDataQuerySet
from .storage import JassetsStaticStorage


class AssetAttachment(models.Model):
    asset = models.ForeignKey('Asset', on_delete=models.DO_NOTHING)
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    version = models.CharField(max_length=100, blank=True)
    path = models.FileField(upload_to='assets')
    metadata = JSONField(blank=True, default=dict)

    class AssetAttachmentManager(BaseManager):
        def get_queryset(self):
            return StaticDataQuerySet(data=(), model=AssetAttachment)

    objects = AssetAttachmentManager()

    @classmethod
    def get_data(cls, *args, **kwargs) -> List[models.Model]:
        result = []
        asset = kwargs.get('asset')
        if asset is not None:
            uuid = str(asset.uuid)

            storage = JassetsStaticStorage()
            manifest = storage.get_manifest()

            for file_manifest in manifest.content:
                if file_manifest.asset_id == uuid:
                    instance = AssetAttachment(
                        asset=asset,
                        id=file_manifest.id,
                        name=file_manifest.name,
                        version=file_manifest.version,
                        metadata=file_manifest.metadata,
                    )
                    storage.fetch_file(file_manifest.path)
                    file_obj = FieldFile(
                        instance=instance,
                        field=AssetAttachment._meta.get_field('path'),
                        name=file_manifest.path,
                    )
                    instance.path = file_obj
                    result.append(instance)
        return result

    @classmethod
    def save_data(cls, *instances: 'AssetAttachment'):
        storage = JassetsStaticStorage()

        manifest = storage.get_manifest()

        for instance in instances:
            instance.path.save(instance.path.name, instance.path._file.file, save=False)
            local_filename = instance.path.path
            ext = Path(local_filename).suffix
            filename = uuid4().hex
            remote_path = f'assets/{filename}{ext}'

            storage.upload(local_filename, remote_path)
            version = get_file_hash(local_filename)
            asset_id = str(instance.asset.uuid)

            manifest.update(
                FileManifest(
                    id=instance.id,
                    asset_id=asset_id,
                    version=version,
                    path=remote_path,
                    metadata=instance.metadata
                )
            )

        storage.update_manifest(manifest)
