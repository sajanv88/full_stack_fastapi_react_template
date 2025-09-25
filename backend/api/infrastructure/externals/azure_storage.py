
import datetime
from datetime import timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from fastapi import UploadFile

from api.core.exceptions import AzureBlobStorageException


class AzureBlobStorage:
    def __init__(self, connection_string: str, container_name: str):
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)

    async def upload_file(self, file: UploadFile, destination: str) -> str:
        try:
            blob_client = self.container_client.get_blob_client(destination)
            data = await file.read()
            blob_client.upload_blob(data, overwrite=True)
            return blob_client.url
        except Exception as e:
            raise AzureBlobStorageException(str(e))
    
    async def generate_read_url(self, blob_name: str, expires_in: int = 3600) -> str:
        try:
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(seconds=expires_in)
            )
            blob_client = self.container_client.get_blob_client(blob_name)
            return f"{blob_client.url}?{sas_token}"
        except Exception as e:
            raise AzureBlobStorageException(str(e))