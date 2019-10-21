import hashlib

from pathlib import Path
from typing import Optional, Tuple
from uuid import uuid4
from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models.fields.files import FieldFile

from ..models import AssetAttachment

from .storage import JassetsStaticStorage


def get_file_hash(filename):
    hash = hashlib.new('sha1')
    with open(filename, 'rb') as fp:
        hash.update(fp.read())
    return hash.hexdigest()


def get_attachment(obj: AssetAttachment):
    """ Load file from remote storage and prepare for assignment to field """
    storage = JassetsStaticStorage()
    storage.fetch_file(obj.path)
    field = models.FileField()
    return FieldFile(
        instance=obj,
        field=field,
        name=obj.path,
    )


def save_attachment(attachment_obj: Optional[File]) -> Optional[Tuple[str, str]]:
    """ Save file to local and remote storage """
    if attachment_obj is not None:
        filename = uuid4().hex
        ext = Path(attachment_obj.name).suffix
        remote_path = f'assets/{filename}{ext}'
        local_path = str(Path(settings.MEDIA_ROOT, remote_path))

        with open(local_path, 'wb+') as f:
            f.write(attachment_obj.file.read())

        storage = JassetsStaticStorage()
        storage.upload(local_path, remote_path)
        return local_path, remote_path
    else:
        return None
