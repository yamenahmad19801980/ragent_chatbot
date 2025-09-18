"""
Base tool interface for the ragent_chatbot project.
Optional abstract base class for tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """Abstract base class for all tools."""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get description of what this tool does."""
        pass
