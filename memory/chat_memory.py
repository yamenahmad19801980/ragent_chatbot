"""
Chat memory management for the ragent_chatbot project.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from typing import Dict, Any

class ChatMemory:
    """Manages chat memory and storage for the chatbot."""
    
    def __init__(self):
        self.memory_saver = MemorySaver()
        self.base_store = InMemoryStore()
    
    def get_memory_saver(self) -> MemorySaver:
        """Get the memory saver instance."""
        return self.memory_saver
    
    def get_base_store(self) -> InMemoryStore:
        """Get the base store instance."""
        return self.base_store
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory configuration for the graph."""
        return {
            "checkpointer": self.memory_saver,
            "store": self.base_store
        }
