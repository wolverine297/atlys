# app/cache/redis_cache.py
import redis
import logging
from ..core.config import settings
import time

class RedisCache:
    """Redis cache implementation with robust connection handling and authentication"""
    
    def __init__(self):
        self.connection_params = {
            'host': 'localhost',
            'port': 6379,
            # 'password': 'Jordan297',
            'decode_responses': True,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'db': 0 
        }
        self.redis_client = None
        self._connect()

    def _connect(self, max_retries=3):
        """Establish connection to Redis with retries"""
        for attempt in range(max_retries):
            try:
                self.redis_client = redis.Redis(**self.connection_params)
                self.redis_client.ping()
                logging.info("Successfully connected to Redis")
                return
            except redis.AuthenticationError as e:
                logging.error(f"Redis authentication failed: {str(e)}")
                raise
            except redis.ConnectionError as e:
                logging.warning(f"Redis connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
            except Exception as e:
                logging.error(f"Unexpected Redis error: {str(e)}")
                raise

    async def ensure_connection(self):
        """Ensure Redis connection is active"""
        try:
            if self.redis_client is None or not self.redis_client.ping():
                self._connect()
        except Exception as e:
            logging.error(f"Failed to ensure Redis connection: {str(e)}")
            self.redis_client = None

    async def get_product_price(self, product_title: str) -> float:
        """Get cached product price with connection retry logic"""
        await self.ensure_connection()
        if not self.redis_client:
            return None
            
        try:
            key = f"product:price:{product_title}"
            value = self.redis_client.get(key)
            return float(value) if value else None
        except Exception as e:
            logging.error(f"Error getting price from Redis: {str(e)}")
            return None

    async def set_product_price(self, product_title: str, price: float) -> None:
        """Set product price in cache with connection retry logic"""
        await self.ensure_connection()
        if not self.redis_client:
            return
            
        try:
            key = f"product:price:{product_title}"
            self.redis_client.setex(
                key,
                3600,  # 1 hour expiration
                str(float(price))
            )
        except Exception as e:
            logging.error(f"Error setting price in Redis: {str(e)}")