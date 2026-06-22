import redis
from typing import Optional

from .config import settings


class RedisClient:
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        return self.redis_client.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600) -> bool:
        """Set key-value pair with expiration"""
        return self.redis_client.setex(key, expire, value)
    
    async def delete(self, key: str) -> bool:
        """Delete key"""
        return self.redis_client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.redis_client.exists(key)
    
    async def incr(self, key: str) -> int:
        """Increment value"""
        return self.redis_client.incr(key)
    
    async def decr(self, key: str) -> int:
        """Decrement value"""
        return self.redis_client.decr(key)
    
    async def set_hash(self, key: str, mapping: dict) -> bool:
        """Set hash"""
        return self.redis_client.hset(key, mapping=mapping)
    
    async def get_hash(self, key: str) -> dict:
        """Get hash"""
        return self.redis_client.hgetall(key)
    
    async def publish(self, channel: str, message: str) -> int:
        """Publish message to channel"""
        return self.redis_client.publish(channel, message)
    
    def get_pubsub(self):
        """Get pubsub object"""
        return self.redis_client.pubsub()


# Global Redis client
redis_client = RedisClient()