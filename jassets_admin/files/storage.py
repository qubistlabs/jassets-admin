import boto3
import io
import json
import mimetypes

from django.conf import settings
from pathlib import Path
from botocore.exceptions import ClientError

from .manifest import Manifest


class JassetsStaticStorage:

    """Jassets static storage abstraction.

    Use S3 as jassets storage.

    Can be swapped with jassets api implementation in future.
    """

    bucket_name = settings.AWS_BUCKET_NAME
    manifest_key = 'jassets.manifest'

    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SECRET_TOKEN,
        )

    def get_manifest(self) -> Manifest:
        """Get remote manifest for this storage instance.
        """
        buf = io.BytesIO()
        try:
            self.s3.download_fileobj(self.bucket_name, self.manifest_key, buf)
            buf.seek(0)
            data = json.load(buf)
            return Manifest.load(data)
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                # manifest doesn't exist
                return Manifest([], version=1)
            else:
                raise

    def fetch_file(self, name: str) -> Path:
        """ Get remote file and return local path """
        file_path = Path(settings.MEDIA_ROOT, name)
        result = file_path
        if not file_path.exists():
            if not file_path.parent.exists():
                file_path.parent.mkdir()
            with open(file_path, 'wb+') as f:
                try:
                    self.s3.download_fileobj(self.bucket_name, name, f)
                except ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        # file doesn't exist
                        result = Path()
                    else:
                        raise
        return result

    def update_manifest(self, manifest: Manifest):
        """Update remote manifest with provided Manifest instance.
        """
        buf = json.dumps(manifest.serialize())
        buf = io.BytesIO(buf.encode())
        self.s3.upload_fileobj(buf, self.bucket_name, self.manifest_key,
                               ExtraArgs={
                                   "ContentType": "application/json"
                               })

    def upload(self, local: str, remote: str):
        self.s3.upload_file(local, self.bucket_name, remote,
                            ExtraArgs={
                                "ContentType": mimetypes.guess_type(local)[0]
                            })

    def cleanup(self, full=False):
        ignore = {'index.html'}
        if not full:
            ignore.add(self.manifest_key)

        if full:
            manifest = []
        else:
            manifest = self.get_manifest()

        content = self.s3.list_objects(Bucket=self.bucket_name)['Contents']
        for obj in content:
            key = obj['Key']
            if (full or key not in manifest) and key not in ignore:
                self.s3.delete_object(Bucket=self.bucket_name, Key=key)
                print(
                    "Obj deleted: ",
                    obj['Key'],
                    "(not in manifest)" if not full and key not in manifest else ""
                )
                continue
