"""
LangSmith configuration and setup for tracking and debugging.
"""

import os
from typing import Optional
from config import Config

def setup_langsmith() -> bool:
    """
    Setup LangSmith for tracking and debugging.
    
    Returns:
        bool: True if LangSmith is configured, False otherwise
    """
    if not Config.LANGSMITH_API_KEY:
        print("LangSmith API key not found. LangSmith tracking will be disabled.")
        return False
    
    try:
        import langsmith
        
        # Set environment variables for LangSmith
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = Config.LANGSMITH_ENDPOINT
        os.environ["LANGCHAIN_API_KEY"] = Config.LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = Config.LANGSMITH_PROJECT
        
        # Optional: Set additional LangSmith settings
        os.environ["LANGCHAIN_VERBOSE"] = "true"  # Enable verbose logging
        
        print(f"LangSmith configured successfully for project: {Config.LANGSMITH_PROJECT}")
        return True
        
    except ImportError:
        print("LangSmith not installed. Please install with: pip install langsmith")
        return False
    except Exception as e:
        print(f"Error setting up LangSmith: {e}")
        return False

def get_langsmith_client():
    """Get LangSmith client if available."""
    try:
        import langsmith
        return langsmith.Client()
    except ImportError:
        return None
    except Exception as e:
        print(f"Error getting LangSmith client: {e}")
        return None

def create_run_name(user_message: str) -> str:
    """
    Create a descriptive run name for LangSmith tracking.
    
    Args:
        user_message: The user's input message
        
    Returns:
        str: A descriptive run name
    """
    # Truncate long messages for better readability
    if len(user_message) > 50:
        user_message = user_message[:47] + "..."
    
    return f"Smart Home Assistant - {user_message}"
