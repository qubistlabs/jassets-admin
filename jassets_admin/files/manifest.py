import json

from dataclasses import dataclass, asdict, field
from typing import List, Dict


@dataclass
class FileManifest:
    asset_id: str = field(compare=False, default=None)
    id: str = field(compare=False, default=None)
    name: str = field(compare=False, default=None)
    version: str = field(compare=False, default=1)
    path: str = field(compare=False, default=None)
    metadata: Dict = field(compare=False, default_factory=dict)


class Manifest:

    """
    Jassets static manifest.
    Process jassets manifest format.

    Manifest content example:
        {
            "version": 1,
            "content": [
                {
                    "path": "icx.xml",
                    "version": "asd7sadjasd",
                    "metadata": {
                        "somemeta": "value",
                    }
                }
            ]
        }
    """

    version: int
    content: List[FileManifest]

    def __init__(self, content: List[FileManifest], version=1):
        self.version = version
        self.content = content

    def update(self, file: FileManifest):
        """Update manifest with `FileManifest` record.

        Add file if it doesn't exist or update existent record.

        Return `True` if updated or `False` if new record added.
        """
        for obj in self.content:
            if obj.id == file.id:
                obj.name = file.name
                obj.asset_id = file.asset_id
                obj.path = file.path
                obj.metadata.update(file.metadata)
                return

        # create new file
        self.content.append(file)

    def merge(self, other: 'Manifest'):
        """Merge other manifest in this one.

        Replace matched records from `other` and append new.
        """
        for item in other.content:
            self.update(item)

    def get(self, key, default=None):
        for obj in self.content:
            if obj.path == key:
                return obj
        return default

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise KeyError
        return value

    def __contains__(self, key):
        return self.get(key) is not None

    @classmethod
    def load(cls, data: Dict):

        """Create Manifest instance from manifest file data

        :param data:
        :return:
        """

        version = data.get('version')
        assert version == 1, f"Unsupported manifest version {version}"

        content = data.get('content')
        assert content, "`content` key missed in manifest"
        assert isinstance(content, list), "`content` must be a list"

        file_manifest_list = []
        for item in content:
            file_manifest_list.append(FileManifest(**item))

        return cls(file_manifest_list, version=version)

    @classmethod
    def load_fp(cls, fp):
        data = json.load(fp)
        return cls.load(data)

    @classmethod
    def load_file(cls, filename):
        with open(filename) as fp:
            return cls.load_fp(fp)

    def serialize(self) -> Dict:
        content = []
        for item in self.content:
            d = asdict(item)
            content.append(d)
        return {
            'version': self.version,
            'content': content
        }
