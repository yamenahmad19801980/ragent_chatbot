"""
Configuration loader for the ragent_chatbot project.
Handles environment variables, API keys, and project settings.
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv(dotenv_path=".env", override=True)

class Config:
    """Configuration class for the chatbot application."""
    
    # Model Configuration
    MODEL_NAME = "qwen-plus-2025-04-28"
    QWEN_API_KEY = os.getenv("QWEN_API_KEY")
    
    # API Keys
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "ragent-chatbot")
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    
    # Syncrow API Configuration
    BASE_URL = "https://syncrow-stg.azurewebsites.net"
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")
    
    # Project UUIDs
    PROJECT_UUID = "fb8777fc-58e1-4cc9-9dce-f20d39c291db"
    COMMUNITY_UUID = "5ccad8b6-7882-44e5-a6fa-38b4360cb18e"
    SPACE_UUID = "513aaeed-9a35-4729-be6b-66576f82142e"
    USER_UUID = "2a68c91d-2c63-4828-8dad-87b2b4f69395"
    
    # Database Configuration (if needed)
    SQL_DATABASE = os.getenv("SQL_DATABASE")
    SQL_USER = os.getenv("SQL_USER")
    SQL_HOST = os.getenv("SQL_HOST")
    SQL_PASSWORD = os.getenv("SQL_PASSWORD")
    SQL_PORT = os.getenv("SQL_PORT")
    
    # File Paths
    CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "device_mappings.csv")
    
    # LLM Configuration
    MAX_TOKENS = 3000
    TIMEOUT = None
    MAX_RETRIES = 2
    
    # Graph Configuration
    RECURSION_LIMIT = 7
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/ragent_chatbot.log")
    LOG_STRUCTURED = os.getenv("LOG_STRUCTURED", "false").lower() == "true"
    LOG_COLORED = os.getenv("LOG_COLORED", "true").lower() == "true"
    
    # Performance Configuration
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes default
    ENABLE_ASYNC = os.getenv("ENABLE_ASYNC", "true").lower() == "true"
    
    # API Configuration
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # 30 seconds default
    API_RETRY_ATTEMPTS = int(os.getenv("API_RETRY_ATTEMPTS", "3"))
    API_RETRY_DELAY = float(os.getenv("API_RETRY_DELAY", "1.0"))  # 1 second default
    
    # Redis Configuration (for caching)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            cls.QWEN_API_KEY,
            cls.TAVILY_API_KEY,
            cls.EMAIL,
            cls.PASSWORD,
        ]
        
        optional_vars = [
            cls.LANGSMITH_API_KEY,
        ]
        
        missing_vars = [var for var in required_vars if not var]
        if missing_vars:
            print(f"Missing required environment variables: {missing_vars}")
            return False
        
        missing_optional = [var for var in optional_vars if not var]
        if missing_optional:
            print(f"Missing optional environment variables (LangSmith will be disabled): {missing_optional}")
        
        return True
    
    @classmethod
    def get_base_store_config(cls) -> dict:
        """Get configuration for the base store and other graph config."""
        return {
            "configurable": {
                "base_store": None,  # Will be set by the memory module
                "token": None,  # Will be set after login
                "user_uuid": cls.USER_UUID,
                "project_uuid": cls.PROJECT_UUID,
                "community_uuid": cls.COMMUNITY_UUID,
                "space_uuid": cls.SPACE_UUID,
            },
            "recursion_limit": cls.RECURSION_LIMIT
        }
