from fastapi import UploadFile
from typing import List, Tuple

from app.storage.s3 import s3_service
from app.hepler.enum import AttachmentType, ImageType, FolderBucket
from app.schema.file import FileInfo
from app.hepler.common import CommonHelper


class FileHelper:
    async def upload_file(self, file: UploadFile, bucket: FolderBucket) -> FileInfo:
        filename = file.filename
        key = CommonHelper.generate_file_name(bucket, filename)
        url = await s3_service.upload_file(file, key)
        return FileInfo(
            name=filename,
            url=url,
            size=file.size,
            type=AttachmentType(file.content_type),
        )

    async def delete_file(self, key: str):
        await s3_service.delete_file(key)

    async def get_file_url(self, key: str) -> str:
        return await s3_service.get_file_url(key)

    async def get_file(self, key: str) -> bytes:
        return await s3_service.get_file(key)

    def filter_images(sefl, attachments: List[FileInfo]) -> List[FileInfo]:
        return [
            attachment
            for attachment in attachments
            if attachment.type in ImageType.__members__.values()
        ]


file_helper = FileHelper()
