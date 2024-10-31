from redis.asyncio import Redis

from app.storage.base_cache import BaseCache


class FileUrlCacheService(BaseCache):
    def __init__(self):
        super().__init__("file_url_cache_", 86400)
        self.image_url_message_key = "image_url_message"

    async def cache_file_url_message(
        self, redis: Redis, *, user_id: int, upload_filename: str, conversation_id: int
    ):
        expire_time = 60 * 60 * 24 * 30
        await self.set(
            redis,
            f"{self.image_url_message_key}:{user_id}:{conversation_id}:{upload_filename}",
            upload_filename,
            expire_time,
        )

    async def get_cache_file_url_message(
        self, redis: Redis, *, upload_filename: str, user_id: int, conversation_id: int
    ) -> str:
        response = await self.get(
            redis,
            f"{self.image_url_message_key}:{user_id}:{conversation_id}:{upload_filename}",
        )
        return response if response else None

    async def delete_cache_file_url_message(
        self,
        redis: Redis,
        *,
        upload_filenames: list[str],
        user_id: int,
        conversation_id: int,
    ):
        for upload_filename in upload_filenames:
            print(
                f"{self.image_url_message_key}:{user_id}:{conversation_id}:{upload_filename}"
            )
            await self.delete(
                redis,
                f"{self.image_url_message_key}:{user_id}:{conversation_id}:{upload_filename}",
            )


file_url_cache_service = FileUrlCacheService()
