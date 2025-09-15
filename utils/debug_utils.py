"""
Debug utilities for the ragent_chatbot project.
"""

import json
from typing import Any, Dict, List
from datetime import datetime

def log_conversation_turn(user_message: str, assistant_response: str, metadata: Dict[str, Any] = None):
    """
    Log a conversation turn for debugging purposes.
    
    Args:
        user_message: The user's input message
        assistant_response: The assistant's response
        metadata: Additional metadata about the conversation turn
    """
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "timestamp": timestamp,
        "user_message": user_message,
        "assistant_response": assistant_response,
        "metadata": metadata or {}
    }
    
    print(f"[CONVERSATION LOG] {timestamp}")
    print(f"User: {user_message}")
    print(f"Assistant: {assistant_response}")
    if metadata:
        print(f"Metadata: {json.dumps(metadata, indent=2)}")
    print("-" * 50)

def log_intent_detection(intents: List[Dict[str, Any]]):
    """
    Log intent detection results for debugging.
    
    Args:
        intents: List of detected intents
    """
    print(f"[INTENT DETECTION] Found {len(intents)} intent(s):")
    for i, intent in enumerate(intents):
        print(f"  {i+1}. Intent: {intent.get('Intent', 'unknown')}")
        print(f"     Device: {intent.get('device_uuid', 'none')}")
        print(f"     Message: {intent.get('user_message', 'none')}")
        print(f"     Reason: {intent.get('reason', 'none')}")
    print("-" * 50)

def log_device_control(device_uuid: str, action: str, result: Dict[str, Any]):
    """
    Log device control actions for debugging.
    
    Args:
        device_uuid: The device being controlled
        action: The action being performed
        result: The result of the action
    """
    print(f"[DEVICE CONTROL] Device: {device_uuid}")
    print(f"Action: {action}")
    print(f"Result: {json.dumps(result, indent=2)}")
    print("-" * 50)

def log_error(error: Exception, context: str = ""):
    """
    Log errors for debugging.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    timestamp = datetime.now().isoformat()
    print(f"[ERROR] {timestamp}")
    if context:
        print(f"Context: {context}")
    print(f"Error: {type(error).__name__}: {str(error)}")
    print("-" * 50)
