import typing as t
import json
from abc import abstractmethod
from bskydata.storage.writers.base import DataWriter


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
