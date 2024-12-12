import typing as t
from abc import ABC, abstractmethod


class DataWriter(ABC):
    @abstractmethod
    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write data to a destination.
        
        :param data: The data to write.
        :param destination: Optional dynamic destination (e.g., file name, database table).
        :param kwargs: Additional parameters for customization.
        """
        pass


class CloudDataWriter(DataWriter):
    @abstractmethod
    def authenticate(self, **kwargs):
        """
        Authenticate with the cloud service.
        
        :param kwargs: Authentication parameters specific to the service.
        """
        pass

    @abstractmethod
    def upload(self, data: t.Any, destination: str, **kwargs):
        """
        Upload data to the cloud.
        
        :param data: The data to upload.
        :param destination: The cloud storage path (e.g., blob name, S3 key).
        :param kwargs: Additional parameters for customization.
        """
        pass

    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write data to the cloud.
        
        :param data: The data to write.
        :param destination: Cloud storage path (e.g., blob name, S3 key).
        :param kwargs: Additional options.
        """
        if not destination:
            raise ValueError("No destination specified for CloudDataWriter.")
        
        self.upload(data, destination, **kwargs)





