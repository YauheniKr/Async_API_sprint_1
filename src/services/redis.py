import hashlib
import json
from typing import Optional

from aioredis import Redis
from fastapi import Depends

from src.db.redis import get_redis


class RedisBaseClass:
    def __init__(self, redis: Redis = Depends(get_redis)):
        self.redis = redis

    async def put_data_to_cache(self, data: dict, s_key: str, index: str, expire: int = 20):
        hash_key = hashlib.md5(s_key.encode()).hexdigest()
        key = f'{index}::{hash_key}'
        data = json.dumps(data)
        await self.redis.set(self._format_redis_key(s_key, index), data, expire=expire)

    async def get_data_from_cache(self, s_key: str, index: str) -> Optional[dict]:
        data = await self.redis.get(self._format_redis_key(s_key, index))
        if not data:
            return None
        data = json.loads(data)
        return data

    def _format_redis_key(self, s_key: str, index: str) -> str:
        hash_key = hashlib.md5(s_key.encode()).hexdigest()
        return f'{index}::{hash_key}'
