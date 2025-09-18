"""
Centralized prompt templates for the ragent_chatbot project.
Eliminates code duplication by providing reusable prompt templates.
"""

import os
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate


class PromptTemplates:
    """Centralized prompt templates for all chatbot operations."""
    
    @staticmethod
    def get_intent_detection_prompt(user_message: str, devices: List[Dict]) -> str:
        """Generate intent detection prompt with user message and available devices."""
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "intent_prompt.txt"), "r") as f:
            intent_prompt = f.read()
        
        return f"""
{intent_prompt}

### USER INPUT:
"{user_message}"

### AVAILABLE DEVICES:
{devices}
"""
    
    @staticmethod
    def get_device_control_prompt(user_messages: List[Dict], descriptions: List[str], original_prompt: str = None) -> str:
        """Generate device control prompt for LLM function calling."""
        base_prompt = """You are an IoT assistant. 
Your job is to take the human command and turn it into a structured object that should align with the possible value of the API.
If the user`s prompt does not align with the possible values then you should set them to None and the status to Failure.
Don't do the mistake of setting the value as a dictionary when the datatype is not dictionary, for example don't do this:
['value': 'True'] when the datatype is boolean, it should be only this ---> True

<user_messages>
{user_messages}
</user_messages>

This is an explanation for how to control product types:
<descriptions>
{descriptions}
</descriptions>
"""
        
        if original_prompt:
            base_prompt += f"""

The following is the original prompt before being decomposed into user_messages:
<original_prompt>
{original_prompt}
</original_prompt>
"""
        
        return base_prompt
    
    @staticmethod
    def get_device_control_single_prompt(user_message: str, device_uuid: str, product_type: str, 
                                       descriptions: List[str], possible_values: List[Dict]) -> str:
        """Generate device control prompt for single device."""
        return f"""You are an IoT assistant. 
Your job is to take the human command and turn it into a structured object that should align with the possible value of the API.
If the user`s prompt does not align with the possible values then you should set them to None and the status to Failure.
Don't do the mistake of setting the value as a dictionary when the datatype is not dictionary, for example don't do this:
['value': 'True'] when the datatype is boolean, it should be only this ---> True

User message: {user_message}
Device UUID: {device_uuid}
Product Type: {product_type}

This is an explanation for how to control product types:
<descriptions>
{descriptions}
</descriptions>

Available functions for this device:
{possible_values}
"""
    
    @staticmethod
    def get_schedule_prompt(user_messages: List[Dict], descriptions: List[str]) -> str:
        """Generate device scheduling prompt."""
        return f"""You are an IoT assistant for scheduling devices.
Your job is to extract scheduling parameters from the user message including time, days, and device function.

The dictionary of devices with corresponding possible values are mentioned below:
<user_messages>
{user_messages}
</user_messages>

Each possible value correspond to a certain device ID. The device IDs are in the same order of the user`s prompt. 

The following is a description for the codes:
<descriptions>
{descriptions}
</descriptions>
"""
    
    @staticmethod
    def get_scene_prompt(user_message: str, available_scenes: List[Dict]) -> str:
        """Generate scene activation prompt."""
        return f"""
You are an IoT assistant that determines which scene to trigger based on user prompt.
If the scene is not available then just set the field uuid to None.

User message: {user_message}
Available scenes: {available_scenes}
"""
    
    @staticmethod
    def get_enhancement_prompt(response: str) -> str:
        """Generate response enhancement prompt."""
        return f"""
You are a friendly smart-home assistant.
Rewrite the following response in a concise, user-friendly way.
Do NOT invent actions or change their outcome. Keep all technical facts intact.

Response:
{response}
"""
    
    @staticmethod
    def get_clarification_prompt(user_message: str, reason: str) -> str:
        """Generate clarification request prompt."""
        return f"""I'm having trouble understanding your request.
Failed to handle the following instruction: {user_message}
Reason: {reason}
Could you please clarify what you meant?"""
    
    @staticmethod
    def get_confirmation_prompt() -> str:
        """Generate high-risk action confirmation prompt."""
        return "⚠️ This is a high-risk action. Please reply 'confirm' or 'cancel'."


class ChatPromptTemplates:
    """LangChain ChatPromptTemplate instances for agent usage."""
    
    @staticmethod
    def get_agent_prompt() -> ChatPromptTemplate:
        """Get the main agent prompt template."""
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "agent_prompt.txt"), "r") as f:
            system_prompt = f.read()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])
    
    @staticmethod
    def get_intent_classifier_prompt() -> ChatPromptTemplate:
        """Get intent classifier prompt template."""
        return ChatPromptTemplate.from_messages([
            ("system", "You are an intent classifier"),
            ("human", "{prompt}")
        ])
    
    @staticmethod
    def get_response_enhancer_prompt() -> ChatPromptTemplate:
        """Get response enhancer prompt template."""
        return ChatPromptTemplate.from_messages([
            ("system", "You are a response enhancer that improves tone only."),
            ("human", "{prompt}")
        ])
