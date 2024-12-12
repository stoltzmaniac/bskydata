import typing as t
from bskydata.storage.base_writers import CloudDataWriter


class AzureBlobWriter(CloudDataWriter):
    def __init__(self, account_name: str, account_key: str, container_name: str):
        from azure.storage.blob import BlobServiceClient

        self.container_name = container_name
        self.blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)

    def authenticate(self, **kwargs):
        """Azure authentication is handled via the BlobServiceClient initialization."""
        pass

    def upload(self, data: t.Any, destination: str, **kwargs):
        """Upload data to an Azure Blob Storage container."""
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=destination)
        blob_client.upload_blob(data, overwrite=True)


class S3Writer(CloudDataWriter):
    def __init__(self, aws_access_key: str, aws_secret_key: str, bucket_name: str):
        import boto3

        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

    def authenticate(self, **kwargs):
        """AWS authentication is handled via the boto3 client initialization."""
        pass

    def upload(self, data: t.Any, destination: str, **kwargs):
        """Upload data to an S3 bucket."""
        self.s3_client.put_object(Bucket=self.bucket_name, Key=destination, Body=data)


class GCPCloudStorageWriter(CloudDataWriter):
    def __init__(self, credentials_json: str, bucket_name: str):
        from google.cloud import storage

        self.bucket_name = bucket_name
        self.storage_client = storage.Client.from_service_account_json(credentials_json)

    def authenticate(self, **kwargs):
        """GCP authentication is handled via the storage client initialization."""
        pass

    def upload(self, data: t.Any, destination: str, **kwargs):
        """Upload data to a Google Cloud Storage bucket."""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination)
        blob.upload_from_string(data)
