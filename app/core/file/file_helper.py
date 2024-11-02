from fastapi import UploadFile
from typing import List, Tuple

from app.storage.s3 import s3_service
from app.hepler.enum import AttachmentType, ImageExtension, DocumentExtension
from app.schema.file import FileInfo


class FileHelper:
    async def upload_file(self, file: UploadFile) -> FileInfo:
        key = file.filename
        url = await s3_service.upload_file(file, key)
        return FileInfo(
            name=key, url=url, size=file.size, type=AttachmentType(file.content_type)
        )

    async def delete_file(self, key: str):
        await s3_service.delete_file(key)

    async def get_file_url(self, key: str) -> str:
        return await s3_service.get_file_url(key)

    async def get_file(self, key: str) -> bytes:
        return await s3_service.get_file(key)

    def get_list_image(sefl, attachments: List[str]) -> List[str]:
        return [
            attachment
            for attachment in attachments
            if attachment.endswith(Tuple(format for format in ImageExtension))
        ]


file_helper = FileHelper()
