
from azure.storage.blob import BlobServiceClient, ContentSettings
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

def upload_image_to_azure(image_bytes, filename, content_type, manual_folder='default-manual'):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        unique_key = f"manual-images/{manual_folder}/{uuid.uuid4()}_{filename}"
        blob_client = container_client.get_blob_client(unique_key)
        content_settings = ContentSettings(content_type=content_type)
        blob_client.upload_blob(image_bytes, overwrite=True, content_settings=content_settings)
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{unique_key}"
        return blob_url
    except Exception as e:
        print(f"Error uploading to Azure Blob Storage: {e}")
        return None

def delete_manual_images_from_azure(manual_name):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        prefix = f"manual-images/{manual_name}/"
        blobs_to_delete = container_client.list_blobs(name_starts_with=prefix)
        deleted = False
        for blob in blobs_to_delete:
            container_client.delete_blob(blob.name)
            print(f"Deleted: {blob.name}")
            deleted = True
        if not deleted:
            print(f"No images found in Azure for manual: {manual_name}")
    except Exception as e:
        print(f"Error deleting from Azure Blob Storage: {e}")
