
import boto3
import datetime
from datetime import timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile


class S3Storage:
    def __init__(self, bucket_name: str, aws_access_key: str, aws_secret_key: str, region: str):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

    async def upload_file(self, file: UploadFile, destination: str) -> str:
        try:
            self.s3_client.upload_fileobj(file.file, self.bucket_name, destination)
            return destination
            # return f"https://{self.bucket_name}.s3.{self.s3_client.meta.region_name}.amazonaws.com/{destination}"
        except NoCredentialsError:
            raise Exception("AWS credentials not found")


    async def generate_read_url(self, key: str, expires_in: int = 3600) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in
        )


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
            raise Exception(f"Azure Blob upload error: {str(e)}")
    
    async def generate_read_url(self, blob_name: str, expires_in: int = 3600) -> str:
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        blob_client = self.container_client.get_blob_client(blob_name)
        return f"{blob_client.url}?{sas_token}"