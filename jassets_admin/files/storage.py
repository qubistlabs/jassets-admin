import boto3
import mimetypes

from django.conf import settings
from pathlib import Path
from botocore.exceptions import ClientError
from loguru import logger


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

    def fetch_file(self, name: str) -> Path:
        """ Get remote file and return local path """
        result = Path()
        if name:
            file_path = Path(settings.MEDIA_ROOT, name)
            if file_path.exists():
                result = file_path
            else:
                if not file_path.parent.exists():
                    file_path.parent.mkdir()
                with open(file_path, 'wb+') as f:
                    try:
                        self.s3.download_fileobj(self.bucket_name, name, f)
                    except ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            logger.error(f"File {name} does not exist")
                            pass
                        else:
                            raise
                    else:
                        result = file_path
        return result

    def upload(self, local: str, remote: str):
        self.s3.upload_file(
            local,
            self.bucket_name,
            remote,
            ExtraArgs={
                "ContentType": mimetypes.guess_type(local)[0],
            },
        )
