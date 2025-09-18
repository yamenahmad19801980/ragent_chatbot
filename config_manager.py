"""
Configuration management system for the ragent_chatbot project.
Provides environment-specific configurations, validation, and runtime updates.
"""

import os
import json
import yaml
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
from config import Config
from utils.logger import get_logger


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    name: str
    user: str
    password: str
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class APIConfig:
    """API configuration."""
    timeout: int
    retry_attempts: int
    retry_delay: float
    rate_limit: int = 100
    rate_limit_window: int = 60


@dataclass
class CacheConfig:
    """Cache configuration."""
    enabled: bool
    ttl: int
    backend: str = "memory"  # memory, redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str
    file: Optional[str] = None
    structured: bool = False
    colored: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class LLMConfig:
    """LLM configuration."""
    model_name: str
    api_key: str
    max_tokens: int
    timeout: Optional[int] = None
    max_retries: int = 2
    temperature: float = 0.7


@dataclass
class SecurityConfig:
    """Security configuration."""
    secret_key: str
    jwt_expiry: int = 3600  # 1 hour
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes


@dataclass
class PerformanceConfig:
    """Performance configuration."""
    enable_async: bool
    max_workers: int = 4
    connection_pool_size: int = 20
    request_timeout: int = 30
    enable_compression: bool = True


class ConfigurationManager:
    """Centralized configuration management system."""
    
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
        self.environment = self._detect_environment()
        self._config = {}
        self._config_file = None
        self._initialized = True
        
        # Load configuration
        self._load_configuration()
    
    def _detect_environment(self) -> Environment:
        """Detect the current environment."""
        env = os.getenv("ENVIRONMENT", "development").lower()
        
        try:
            return Environment(env)
        except ValueError:
            self.logger.warning(f"Unknown environment '{env}', defaulting to development")
            return Environment.DEVELOPMENT
    
    def _load_configuration(self):
        """Load configuration from various sources."""
        # Load from environment variables first
        self._load_from_env()
        
        # Load from config files
        self._load_from_files()
        
        # Apply environment-specific overrides
        self._apply_environment_overrides()
        
        # Validate configuration
        self._validate_configuration()
        
        self.logger.info(f"Configuration loaded for environment: {self.environment.value}")
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        self._config = {
            "environment": self.environment.value,
            
            # Database
            "database": DatabaseConfig(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                name=os.getenv("DB_NAME", "ragent_chatbot"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
                ssl_mode=os.getenv("DB_SSL_MODE", "prefer"),
                pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20"))
            ),
            
            # API
            "api": APIConfig(
                timeout=int(os.getenv("API_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("API_RETRY_ATTEMPTS", "3")),
                retry_delay=float(os.getenv("API_RETRY_DELAY", "1.0")),
                rate_limit=int(os.getenv("API_RATE_LIMIT", "100")),
                rate_limit_window=int(os.getenv("API_RATE_LIMIT_WINDOW", "60"))
            ),
            
            # Cache
            "cache": CacheConfig(
                enabled=os.getenv("ENABLE_CACHING", "true").lower() == "true",
                ttl=int(os.getenv("CACHE_TTL", "300")),
                backend=os.getenv("CACHE_BACKEND", "memory"),
                redis_host=os.getenv("REDIS_HOST", "localhost"),
                redis_port=int(os.getenv("REDIS_PORT", "6379")),
                redis_db=int(os.getenv("REDIS_DB", "0")),
                redis_password=os.getenv("REDIS_PASSWORD")
            ),
            
            # Logging
            "logging": LoggingConfig(
                level=os.getenv("LOG_LEVEL", "INFO"),
                file=os.getenv("LOG_FILE"),
                structured=os.getenv("LOG_STRUCTURED", "false").lower() == "true",
                colored=os.getenv("LOG_COLORED", "true").lower() == "true",
                max_file_size=int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024))),
                backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5"))
            ),
            
            # LLM
            "llm": LLMConfig(
                model_name=os.getenv("LLM_MODEL_NAME", "qwen-plus-2025-04-28"),
                api_key=os.getenv("QWEN_API_KEY", ""),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "3000")),
                timeout=int(os.getenv("LLM_TIMEOUT", "0")) or None,
                max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
            ),
            
            # Security
            "security": SecurityConfig(
                secret_key=os.getenv("SECRET_KEY", "your-secret-key-here"),
                jwt_expiry=int(os.getenv("JWT_EXPIRY", "3600")),
                password_min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
                max_login_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
                lockout_duration=int(os.getenv("LOCKOUT_DURATION", "900"))
            ),
            
            # Performance
            "performance": PerformanceConfig(
                enable_async=os.getenv("ENABLE_ASYNC", "true").lower() == "true",
                max_workers=int(os.getenv("MAX_WORKERS", "4")),
                connection_pool_size=int(os.getenv("CONNECTION_POOL_SIZE", "20")),
                request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
                enable_compression=os.getenv("ENABLE_COMPRESSION", "true").lower() == "true"
            )
        }
    
    def _load_from_files(self):
        """Load configuration from YAML/JSON files."""
        config_files = [
            f"config/{self.environment.value}.yaml",
            f"config/{self.environment.value}.json",
            "config/default.yaml",
            "config/default.json",
            "config.yaml",
            "config.json"
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                            file_config = yaml.safe_load(f)
                        else:
                            file_config = json.load(f)
                    
                    self._merge_config(file_config)
                    self._config_file = config_file
                    self.logger.info(f"Loaded configuration from {config_file}")
                    break
                    
                except Exception as e:
                    self.logger.error(f"Failed to load configuration from {config_file}: {e}")
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """Merge file configuration with existing config."""
        for section, values in file_config.items():
            if section in self._config and isinstance(self._config[section], dict):
                self._config[section].update(values)
            else:
                self._config[section] = values
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        if self.environment == Environment.DEVELOPMENT:
            # Development overrides
            self._config["logging"]["level"] = "DEBUG"
            self._config["cache"]["enabled"] = True
            self._config["performance"]["enable_async"] = True
            
        elif self.environment == Environment.STAGING:
            # Staging overrides
            self._config["logging"]["level"] = "INFO"
            self._config["cache"]["enabled"] = True
            self._config["cache"]["backend"] = "redis"
            
        elif self.environment == Environment.PRODUCTION:
            # Production overrides
            self._config["logging"]["level"] = "WARNING"
            self._config["cache"]["enabled"] = True
            self._config["cache"]["backend"] = "redis"
            self._config["performance"]["enable_async"] = True
            
        elif self.environment == Environment.TESTING:
            # Testing overrides
            self._config["logging"]["level"] = "ERROR"
            self._config["cache"]["enabled"] = False
            self._config["database"]["name"] = f"{self._config['database']['name']}_test"
    
    def _validate_configuration(self):
        """Validate the configuration."""
        required_fields = [
            ("llm.api_key", "QWEN_API_KEY"),
            ("database.host", "DB_HOST"),
            ("database.name", "DB_NAME"),
            ("database.user", "DB_USER"),
            ("database.password", "DB_PASSWORD")
        ]
        
        missing_fields = []
        for field_path, env_var in required_fields:
            if not self._get_nested_value(field_path):
                missing_fields.append(f"{field_path} (from {env_var})")
        
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
        
        self.logger.info("Configuration validation passed")
    
    def _get_nested_value(self, path: str) -> Any:
        """Get a nested value from configuration using dot notation."""
        keys = path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._get_nested_value(key) or default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section."""
        return self._config.get(section, {})
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value at runtime."""
        keys = key.split('.')
        config = self._config
        
        for key_part in keys[:-1]:
            if key_part not in config:
                config[key_part] = {}
            config = config[key_part]
        
        config[keys[-1]] = value
        self.logger.info(f"Configuration updated: {key} = {value}")
    
    def reload(self) -> None:
        """Reload configuration from files."""
        self.logger.info("Reloading configuration...")
        self._load_configuration()
    
    def save_to_file(self, file_path: str) -> None:
        """Save current configuration to a file."""
        try:
            with open(file_path, 'w') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    yaml.dump(self._config, f, default_flow_style=False)
                else:
                    json.dump(self._config, f, indent=2)
            
            self.logger.info(f"Configuration saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {file_path}: {e}")
    
    def get_environment(self) -> Environment:
        """Get the current environment."""
        return self.environment
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING
    
    def get_database_url(self) -> str:
        """Get the database URL."""
        db = self._config["database"]
        return f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}"
    
    def get_redis_url(self) -> str:
        """Get the Redis URL."""
        cache = self._config["cache"]
        if cache.redis_password:
            return f"redis://:{cache.redis_password}@{cache.redis_host}:{cache.redis_port}/{cache.redis_db}"
        return f"redis://{cache.redis_host}:{cache.redis_port}/{cache.redis_db}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {}
        for key, value in self._config.items():
            if hasattr(value, '__dict__'):
                result[key] = asdict(value)
            else:
                result[key] = value
        return result


# Global configuration manager instance
config_manager = ConfigurationManager()

# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value."""
    return config_manager.get(key, default)


def get_section(section: str) -> Dict[str, Any]:
    """Get a configuration section."""
    return config_manager.get_section(section)


def set_config(key: str, value: Any) -> None:
    """Set a configuration value."""
    config_manager.set(key, value)


def reload_config() -> None:
    """Reload configuration."""
    config_manager.reload()


def is_development() -> bool:
    """Check if running in development."""
    return config_manager.is_development()


def is_production() -> bool:
    """Check if running in production."""
    return config_manager.is_production()


def is_testing() -> bool:
    """Check if running in testing."""
    return config_manager.is_testing()
