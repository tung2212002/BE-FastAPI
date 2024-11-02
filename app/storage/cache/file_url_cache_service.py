from redis.asyncio import Redis
import json

from app.storage.base_cache import BaseCache
from app.schema.file import FileInfo


class FileUrlCacheService(BaseCache):
    def __init__(self):
        super().__init__("file_url_cache_", 86400)
        self.image_url_message_key = "image_url_message"

    async def cache_file_url(
        self,
        redis: Redis,
        *,
        user_id: int,
        file_info: FileInfo,
        flex_key: int,
        key: str,
        expire_time: int,
    ):
        value = json.dumps(file_info.model_dump())
        await self.set(
            redis,
            f"{key}:{user_id}:{flex_key}:{file_info.name}",
            value,
            expire_time,
        )

    async def get_cache_file_url(
        self, redis: Redis, *, upload_filename, user_id: int, flex_key: str
    ) -> FileInfo:
        response = await self.get(
            redis,
            f"{self.image_url_message_key}:{user_id}:{flex_key}:{upload_filename}",
        )
        return response if response else None

    async def get_cache_file_url_message(
        self, redis: Redis, *, upload_filename, user_id: int, conversation_id: int
    ) -> FileInfo:
        flex_key = str(conversation_id)
        response = await self.get_cache_file_url(
            redis,
            upload_filename=upload_filename,
            user_id=user_id,
            conversation_id=flex_key,
        )
        return FileInfo(**json.loads(response)) if response else None

    async def delete_cache_file_url(
        self,
        redis: Redis,
        *,
        upload_filenames: list[str],
        user_id: int,
        flex_key: str,
        upload_filename: str,
    ):
        for upload_filename in upload_filenames:
            await self.delete(
                redis,
                f"{self.image_url_message_key}:{str(user_id)}:{flex_key}:{upload_filename}",
            )

    async def delete_cache_file_url_message(
        self,
        redis: Redis,
        *,
        upload_filenames: list[str],
        user_id: int,
        conversation_id: int,
    ):
        flex_key: str = str(conversation_id)
        for upload_filename in upload_filenames:
            await self.delete_cache_file_url(
                redis,
                upload_filenames=upload_filenames,
                user_id=user_id,
                flex_key=flex_key,
                upload_filename=upload_filename,
            )

    async def cache_file_url_message(
        self, redis: Redis, *, user_id: int, file_info: FileInfo, conversation_id: int
    ):
        expire_time = 60 * 60 * 24 * 30
        flex_key = str(conversation_id)
        await self.cache_file_url(
            redis,
            user_id=user_id,
            file_info=file_info,
            flex_key=flex_key,
            key=self.image_url_message_key,
            expire_time=expire_time,
        )


file_url_cache_service = FileUrlCacheService()
