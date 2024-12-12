import typing as t
import boto3
from bskydata.storage.cloud.base import CloudDataWriter
from bskydata.storage.base import JsonFileHandler

class S3DataWriter(CloudDataWriter):
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket_name: str):

        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

    def authenticate(self, **kwargs):
        """AWS authentication is handled via the boto3 client initialization."""
        pass

    def upload(self, file_path: str, destination: str, **kwargs):
        """Upload a file to an S3 bucket."""
        with open(file_path, "rb") as data:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=destination, Body=data)

class S3JsonDataWriter(S3DataWriter):
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket_name: str, indent: int = 4, sort_keys: bool = True):
        super().__init__(aws_access_key, aws_secret_key, bucket_name)
        self.json_handler = JsonFileHandler(indent=indent, sort_keys=sort_keys)

    def write(self, data: t.Any, destination: str = None, **kwargs):
        """
        Write data to an S3 bucket as a JSON file.
        
        :param data: The data to write.
        :param destination: Cloud storage path (e.g., S3 key).
        :param kwargs: Additional options for upload.
        """
        temp_file_path = self.json_handler.write_to_temp_file(data)
        self.upload(temp_file_path, destination, **kwargs)
