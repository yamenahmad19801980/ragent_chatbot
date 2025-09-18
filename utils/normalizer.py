"""
Message normalization utilities.
Centralized message processing to eliminate duplication.
"""

from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, messages_from_dict

class MessageNormalizer:
    """Centralized utility class for normalizing messages."""
    
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
    
    @staticmethod
    def normalize_gradio_history(history: list) -> List[BaseMessage]:
        """Normalize Gradio chat history to LangChain messages."""
        messages = []
        
        # Handle both tuple format (old) and dict format (new with type="messages")
        for item in history:
            if isinstance(item, dict):
                # New format: {"role": "user/assistant", "content": "message"}
                if item.get("role") == "user":
                    messages.append(HumanMessage(content=item.get("content", "")))
                elif item.get("role") == "assistant":
                    messages.append(AIMessage(content=item.get("content", "")))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                # Old format: (user_message, bot_message)
                user, bot = item
                if user:
                    messages.append(HumanMessage(content=user))
                if bot:
                    messages.append(AIMessage(content=bot))
            elif isinstance(item, str):
                # Single string message
                messages.append(HumanMessage(content=item))
        
        return messages
    
    @staticmethod
    def find_user_message(messages: List[BaseMessage]) -> Optional[str]:
        """Find the latest user message from a list of messages."""
        for msg in reversed(messages):
            if msg.type == "human" and msg.content:
                return msg.content
        return None
    
    @staticmethod
    def filter_tool_call_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
        """Filter out incomplete tool call sequences from chat history."""
        filtered_messages = []
        i = 0
        while i < len(messages):
            msg = messages[i]
            
            # If this is an AI message with tool calls, check if it has responses
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_call_ids = {tc['id'] for tc in msg.tool_calls}
                
                # Look ahead for tool response messages
                j = i + 1
                found_responses = set()
                while j < len(messages) and hasattr(messages[j], 'tool_call_id'):
                    found_responses.add(messages[j].tool_call_id)
                    j += 1
                
                # Only include if all tool calls have responses
                if tool_call_ids == found_responses:
                    filtered_messages.extend(messages[i:j])
                    i = j
                else:
                    i += 1
            else:
                filtered_messages.append(msg)
                i += 1
        
        return filtered_messages
