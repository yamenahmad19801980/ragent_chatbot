"""
Qwen LLM configuration and initialization.
Centralized LLM setup for the ragent_chatbot project.
"""

from langchain_qwq import ChatQwQ
from config import Config

def get_qwen_llm() -> ChatQwQ:
    """
    Create and return a configured ChatQwQ instance.
    
    Returns:
        ChatQwQ: Configured Qwen LLM instance
    """
    if not Config.QWEN_API_KEY:
        raise ValueError("QWEN_API_KEY not found in environment variables")
    
    return ChatQwQ(
        api_key=Config.QWEN_API_KEY,
        model=Config.MODEL_NAME,
        max_tokens=Config.MAX_TOKENS,
        timeout=Config.TIMEOUT,
        max_retries=Config.MAX_RETRIES,
    )
