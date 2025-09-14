"""
Web search tool using Tavily API.
"""

from langchain.agents import Tool
from langchain_community.tools import TavilySearchResults
from config import Config

def create_web_search_tool() -> Tool:
    """Create web search tool using Tavily."""
    if not Config.TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not found in environment variables")
    
    tavily_search = TavilySearchResults(max_results=3)
    
    return Tool(
        name="search_web",
        func=tavily_search.invoke,
        description="Useful for searching the web to answer general knowledge questions, look up current events, or help with open-ended queries. Input should be a search query in natural language."
    )
