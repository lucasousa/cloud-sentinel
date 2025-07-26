import ssl
from functools import lru_cache
from typing import Optional

import redis.asyncio as redis
from pydantic import AnyUrl

from src.settings import REDIS_URL


class RedisClient:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url: AnyUrl = redis_url or REDIS_URL
        self.redis: Optional[redis.Redis] = None

    def get_ssl_context(self) -> Optional[ssl.SSLContext]:
        if self.redis_url.startswith("rediss://"):
            return ssl.create_default_context()
        return None

    def connect(self) -> redis.Redis:
        params = self.get_params_from_url()
        if not self.redis:
            self.redis = redis.Redis(
                host=params.get("host", "localhost"),
                port=params.get("port", 6379),
                ssl=True,
                ssl_ca_certs=None,
            )
        return self.redis

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    def get_params_from_url(self) -> dict:
        url = AnyUrl(self.redis_url)
        params = {
            "host": url.host,
            "port": url.port
        }
        return {k: v for k, v in params.items() if v is not None}


@lru_cache()
def get_redis_client() -> RedisClient:
    return RedisClient().connect()
