"""
Message normalization utilities.
"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, messages_from_dict

class MessageNormalizer:
    """Utility class for normalizing messages."""
    
    @staticmethod
    def normalize_messages(raw_messages: List[Any]) -> List[BaseMessage]:
        """Normalize messages to LangChain format."""
        messages = []
        
        for m in raw_messages:
            if isinstance(m, BaseMessage):
                messages.append(m)
            elif isinstance(m, dict):
                # Convert role-based dicts to LangChain format
                if "role" in m and "content" in m:
                    role_to_type = {"user": "human", "assistant": "ai", "system": "system"}
                    message_type = role_to_type.get(m["role"], "human")
                    messages.extend(messages_from_dict([{
                        "type": message_type,
                        "data": {"content": m["content"]}
                    }]))
                elif "type" in m and "data" in m:
                    messages.extend(messages_from_dict([m]))
                else:
                    print(f"[WARN] Skipping unrecognized message format: {m}")
            else:
                print(f"[WARN] Invalid message object: {m}")
        
        return messages
