import json

from aioredis import Redis
from fastapi import Depends

from src.db.redis import get_redis


class RedisBaseClass:
    def __init__(self, redis: Redis = Depends(get_redis)):
        self.redis = redis

    async def _put_data_to_cache(self, data, s: str, expire: int = 20):
        data = json.dumps(data)
        await self.redis.set(s, data, expire=expire)

    async def _get_data_from_cache(self, s: str):
        data = await self.redis.get(s)
        if not data:
            return None
        data = json.loads(data)
        return data
