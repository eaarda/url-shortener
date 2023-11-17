import aioredis
from core.config import settings


class RedisService():
    def __init__(self):
        self.redis_client = aioredis.from_url(f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}', encoding="utf8", decode_responses=True)


redis_pool = RedisService().redis_client