"""
Tool registry for the ragent_chatbot project.
Centralized registration and management of all tools.
"""

from typing import List
from langchain.agents import Tool
from langchain_core.prompts import ChatPromptTemplate

from config import Config
from domain.api_client import SyncrowAPIClient
from tools import create_web_search_tool
from llm import get_qwen_llm
from prompts.prompt_manager import prompt_manager

class ToolRegistry:
    """Registry for all tools used in the chatbot."""
    
    def __init__(self):
        self.api_client = SyncrowAPIClient()
        self.llm = get_qwen_llm()
        self._initialize_api_client()
    
    def _initialize_api_client(self):
        """Initialize the API client with login credentials."""
        if not Config.validate():
            raise ValueError("Configuration validation failed")
        
        token = self.api_client.login(Config.EMAIL, Config.PASSWORD)
        if not token:
            raise ValueError("Failed to login to Syncrow API")
    
    def get_all_tools(self) -> List[Tool]:
        """Get all available tools."""
        tools = []
        
        # Add web search tool
        tools.append(create_web_search_tool())
        
        return tools
    
    def get_web_search_tool(self) -> Tool:
        """Get web search tool."""
        return create_web_search_tool()
    
    def get_agent_prompt(self) -> ChatPromptTemplate:
        """Get the agent prompt template."""
        return prompt_manager.get_chat_prompt_template()
    
    def get_api_client(self) -> SyncrowAPIClient:
        """Get the initialized API client."""
        return self.api_client
