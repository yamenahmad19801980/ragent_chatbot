"""
Caching system for the ragent_chatbot project.
Provides in-memory and Redis-based caching with TTL support.
"""

import time
import json
import hashlib
from typing import Any, Dict, Optional, Union, Callable
from functools import wraps
from threading import Lock
from config import Config
from utils.logger import get_logger

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheEntry:
    """Represents a cache entry with value and expiration time."""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return time.time() > self.expires_at
    
    def get_value(self) -> Any:
        """Get the value if not expired, otherwise return None."""
        if self.is_expired():
            return None
        return self.value


class InMemoryCache:
    """Thread-safe in-memory cache implementation."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
        self.logger = get_logger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self.logger.debug(f"Cache entry expired for key: {key}")
                return None
            
            self.logger.debug(f"Cache hit for key: {key}")
            return entry.get_value()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl)
            self.logger.debug(f"Cache set for key: {key} with TTL: {ttl}s")
    
    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self.logger.debug(f"Cache entry deleted for key: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self.logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries."""
        with self._lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)
    
    def size(self) -> int:
        """Get the number of cache entries."""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> list:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())


class RedisCache:
    """Redis-based cache implementation."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, 
                 password: Optional[str] = None, default_ttl: int = 300):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis is not available. Install redis-py: pip install redis")
        
        self.redis_client = redis.Redis(
            host=host, port=port, db=db, password=password, decode_responses=True
        )
        self.default_ttl = default_ttl
        self.logger = get_logger(__name__)
        
        # Test connection
        try:
            self.redis_client.ping()
            self.logger.info("Redis cache connection established")
        except redis.ConnectionError as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        try:
            value = self.redis_client.get(key)
            if value is None:
                self.logger.debug(f"Cache miss for key: {key}")
                return None
            
            # Try to deserialize JSON
            try:
                result = json.loads(value)
                self.logger.debug(f"Cache hit for key: {key}")
                return result
            except json.JSONDecodeError:
                # Return as string if not JSON
                return value
                
        except redis.RedisError as e:
            self.logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            # Serialize value to JSON if possible
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)
            
            self.redis_client.setex(key, ttl, serialized_value)
            self.logger.debug(f"Cache set for key: {key} with TTL: {ttl}s")
            
        except redis.RedisError as e:
            self.logger.error(f"Redis set error for key {key}: {e}")
    
    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        try:
            result = self.redis_client.delete(key)
            if result:
                self.logger.debug(f"Cache entry deleted for key: {key}")
            return bool(result)
        except redis.RedisError as e:
            self.logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        try:
            self.redis_client.flushdb()
            self.logger.info("Redis cache cleared")
        except redis.RedisError as e:
            self.logger.error(f"Redis clear error: {e}")


class CacheManager:
    """Centralized cache management system."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.logger = get_logger(__name__)
        self._cache = None
        self._initialized = True
        
        # Initialize cache based on configuration
        if Config.ENABLE_CACHING:
            self._initialize_cache()
    
    def _initialize_cache(self):
        """Initialize the cache backend."""
        try:
            # Try Redis first if available
            if REDIS_AVAILABLE and hasattr(Config, 'REDIS_HOST'):
                self._cache = RedisCache(
                    host=getattr(Config, 'REDIS_HOST', 'localhost'),
                    port=getattr(Config, 'REDIS_PORT', 6379),
                    db=getattr(Config, 'REDIS_DB', 0),
                    password=getattr(Config, 'REDIS_PASSWORD', None),
                    default_ttl=Config.CACHE_TTL
                )
                self.logger.info("Using Redis cache backend")
            else:
                # Fall back to in-memory cache
                self._cache = InMemoryCache(default_ttl=Config.CACHE_TTL)
                self.logger.info("Using in-memory cache backend")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize cache: {e}. Disabling caching.")
            self._cache = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if not self._cache:
            return None
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        if not self._cache:
            return
        self._cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        if not self._cache:
            return False
        return self._cache.delete(key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        if not self._cache:
            return
        self._cache.clear()
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments."""
        # Create a string representation of all arguments
        key_parts = [prefix] + [str(arg) for arg in args]
        
        # Add keyword arguments sorted by key
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])
        
        # Join and hash to create a consistent key
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


def cached(prefix: str, ttl: Optional[int] = None, key_func: Optional[Callable] = None):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = CacheManager()
            
            if not cache_manager._cache:
                # Cache disabled, just call the function
                return func(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(prefix, *args, **kwargs)
            else:
                cache_key = cache_manager.generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_key_for_device_operation(prefix: str, device_uuid: str, operation: str, **kwargs) -> str:
    """Generate cache key for device operations."""
    return f"{prefix}:device:{device_uuid}:{operation}:{hash(str(sorted(kwargs.items())))}"


def cache_key_for_api_call(prefix: str, method: str, url: str, **kwargs) -> str:
    """Generate cache key for API calls."""
    return f"{prefix}:api:{method}:{hash(url)}:{hash(str(sorted(kwargs.items())))}"


# Global cache manager instance
cache_manager = CacheManager()

# Convenience functions
def get_cache() -> Optional[Union[InMemoryCache, RedisCache]]:
    """Get the cache instance."""
    return cache_manager._cache


def cache_get(key: str) -> Optional[Any]:
    """Get a value from the cache."""
    return cache_manager.get(key)


def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """Set a value in the cache."""
    cache_manager.set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete a value from the cache."""
    return cache_manager.delete(key)


def cache_clear() -> None:
    """Clear all cache entries."""
    cache_manager.clear()
