
from functools import lru_cache
from typing import Optional

import redis.asyncio as redis
from pydantic import AnyUrl

from src.settings import REDIS_URL


class RedisClient:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url: AnyUrl = redis_url or REDIS_URL
        self.redis: Optional[redis.Redis] = None

    def connect(self) -> redis.Redis:
        if self.redis_url.startswith('rediss://'):
            self.redis = redis.from_url(
                self.redis_url, ssl_cert_reqs=None)
        else:
            self.redis = redis.from_url(self.redis_url)
        return self.redis

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

@lru_cache()
def get_redis_client() -> RedisClient:
    return RedisClient().connect()
