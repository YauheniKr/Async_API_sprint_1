import pickle

from aioredis import Redis
from db.redis import get_redis
from elasticsearch_dsl import Search
from fastapi import Depends


class RedisBaseClass:
    def __init__(self, redis: Redis = Depends(get_redis)):
        self.redis = redis

    async def _put_data_to_cache(self, data, s: Search, expire=5 * 60):
        data = pickle.dumps(data)
        await self.redis.set(str(s.to_dict()), data, expire=expire)

    async def _get_data_from_cache(self, s: dict):
        data = await self.redis.get(str(s))
        if not data:
            return None
        data = pickle.loads(data)
        return data