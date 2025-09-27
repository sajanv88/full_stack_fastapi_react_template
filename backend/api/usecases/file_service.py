from api.infrastructure.externals.file_retrieval import FileRetrieval
from api.infrastructure.externals.file_upload import FileUpload


class FileService(FileUpload, FileRetrieval):
    def __init__(self):
        super().__init__()

    async def get_file_url(self, file_key: str) -> str:
        return await self.generate_read_url(file_key)