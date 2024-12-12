import typing as t
import json
from abc import abstractmethod
from bskydata.storage.base import DataWriter


class CloudDataWriter(DataWriter):
    @abstractmethod
    def authenticate(self, **kwargs):
        """
        Authenticate with the cloud service.
        
        :param kwargs: Authentication parameters specific to the service.
        """
        pass

    @abstractmethod
    def upload(self, file_path: str, destination: str, **kwargs):
        """
        Upload a file to the cloud.
        
        :param file_path: The path of the file to upload.
        :param destination: The cloud storage path (e.g., blob name, S3 key).
        :param kwargs: Additional parameters for customization.
        """
        pass


class CloudJsonDataWriter(CloudDataWriter):
    def __init__(self, indent: int = 4, sort_keys: bool = True):
        """
        :param indent: Number of spaces to use for JSON indentation (default is 4).
        :param sort_keys: Whether to sort JSON keys alphabetically (default is True).
        """
        self.indent = indent
        self.sort_keys = sort_keys

    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write JSON data to a temporary file and upload it to the cloud.

        :param data: The data to write.
        :param destination: Cloud storage path (e.g., blob name, S3 key).
        :param kwargs: Additional options like 'indent' for pretty printing.
        """
        import tempfile

        # Write data to a temporary JSON file
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as temp_file:
            json.dump(
                data,
                temp_file,
                indent=self.indent,
                sort_keys=self.sort_keys,
                separators=(',', ': ')  # Add spaces after commas and colons
            )
            temp_file_path = temp_file.name

        # Upload the temporary file
        self.upload(temp_file_path, destination, **kwargs)
