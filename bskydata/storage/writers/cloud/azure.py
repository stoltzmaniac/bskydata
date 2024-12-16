import typing as t
import json
from azure.storage.blob import BlobServiceClient
from bskydata.storage.handlers.json import JsonFileHandler
from bskydata.storage.writers.cloud.base import CloudDataWriter


class AzureDataWriter(CloudDataWriter):
    def __init__(self, connection_string: str, container_name: str):

        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def authenticate(self, **kwargs):
        """Azure authentication is handled via the BlobServiceClient initialization."""
        pass

    def upload(self, file_path: str, destination: str, **kwargs):
        """Upload a file to an Azure Blob Storage container."""
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=destination)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

class AzureJsonDataWriter(AzureDataWriter):
    def __init__(self, connection_string: str, container_name: str, indent: int = 4, sort_keys: bool = True):
        super().__init__(connection_string, container_name)
        self.json_handler = JsonFileHandler(indent=indent, sort_keys=sort_keys)

    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write data to Azure Blob Storage as a JSON file.
        
        :param data: The data to write.
        :param destination: Cloud storage path (e.g., blob name).
        :param kwargs: Additional options for upload.
        """
        temp_file_path = self.json_handler.write_to_temp_file(data)
        self.upload(temp_file_path, destination, **kwargs)
