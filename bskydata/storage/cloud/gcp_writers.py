import typing as t
from google.cloud import storage
from bskydata.storage.cloud.base import CloudDataWriter
from bskydata.storage.base import JsonFileHandler


class GCPDataWriter(CloudDataWriter):
    def __init__(self, credentials_json: str, bucket_name: str):

        self.bucket_name = bucket_name
        self.storage_client = storage.Client.from_service_account_json(credentials_json)

    def authenticate(self, **kwargs):
        """GCP authentication is handled via the storage client initialization."""
        pass

    def upload(self, file_path: str, destination: str, **kwargs):
        """Upload a file to a Google Cloud Storage bucket."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination)
        blob.upload_from_filename(file_path)

class GCPJsonDataWriter(GCPDataWriter):
    def __init__(self, credentials_json: str, bucket_name: str, indent: int = 4, sort_keys: bool = True):
        super().__init__(credentials_json, bucket_name)
        self.json_handler = JsonFileHandler(indent=indent, sort_keys=sort_keys)

    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write data to Google Cloud Storage as a JSON file.
        
        :param data: The data to write.
        :param destination: Cloud storage path (e.g., blob name).
        :param kwargs: Additional options for upload.
        """
        temp_file_path = self.json_handler.write_to_temp_file(data)
        self.upload(temp_file_path, destination, **kwargs)
