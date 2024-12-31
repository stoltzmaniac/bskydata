import asyncio
import os
from google.cloud import storage


def upload_bulk_to_gcs(bucket_name: str, folder_path: str):
    """Upload all files in the local folder to GCS and delete them after upload."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            blob = bucket.blob(f"hashtag_data/{file_name}")
            print(f"[INFO] Uploading {file_name} to GCS...")
            blob.upload_from_filename(file_path)
            print(f"[INFO] Successfully uploaded {file_name}. Deleting local file...")
            os.remove(file_path)


async def schedule_bulk_upload(bucket_name: str, folder_path: str, interval: int):
    """Schedule bulk uploads at regular intervals."""
    while True:
        print(f"[INFO] Running bulk upload from folder: {folder_path}")
        await asyncio.get_event_loop().run_in_executor(None, upload_bulk_to_gcs, bucket_name, folder_path)
        await asyncio.sleep(interval)
