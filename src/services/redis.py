import hashlib
import json

from aioredis import Redis
from fastapi import Depends

from src.db.redis import get_redis


class RedisBaseClass:
    def __init__(self, redis: Redis = Depends(get_redis)):
        self.redis = redis

    async def put_data_to_cache(self, data, s_key: str, index: str, expire: int = 20):
        hash_key = hashlib.md5(s_key.encode()).hexdigest()
        key = f'{index}::{hash_key}'
        data = json.dumps(data)
        await self.redis.set(key, data, expire=expire)

    async def get_data_from_cache(self, s_key: str, index: str):
        hash_key = hashlib.md5(s_key.encode()).hexdigest()
        key = f'{index}::{hash_key}'
        data = await self.redis.get(key)
        if not data:
            return None
        data = json.loads(data)
        return data
