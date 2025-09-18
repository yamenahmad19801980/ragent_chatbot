"""
Prompt template manager using LangChain PromptTemplate.
Loads prompts from MD files and provides easy access with variable substitution.
"""

import os
from typing import Dict, Any, Optional
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from utils.logger import get_logger


class PromptManager:
    """Centralized prompt template management using LangChain PromptTemplate."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.prompts_dir = os.path.join(os.path.dirname(__file__))
        self._templates = {}
        self._load_all_templates()
    
    def _load_all_templates(self):
        """Load all prompt templates from MD files."""
        template_files = {
            "intent_detection": {
                "file": "intent_detection.md",
                "variables": ["user_message", "available_devices"]
            },
            "device_control": {
                "file": "device_control.md", 
                "variables": ["user_messages", "descriptions", "original_prompt"]
            },
            "device_schedule": {
                "file": "device_schedule.md",
                "variables": ["user_messages", "descriptions"]
            },
            "scene_activation": {
                "file": "scene_activation.md",
                "variables": ["user_message", "available_scenes"]
            },
            "response_enhancement": {
                "file": "response_enhancement.md",
                "variables": ["response"]
            },
            "clarification_request": {
                "file": "clarification_request.md",
                "variables": ["failed_instruction", "reason"]
            },
            "confirmation_request": {
                "file": "confirmation_request.md",
                "variables": ["action_summary", "risk_level"]
            },
            "agent_system": {
                "file": "agent_system.md",
                "variables": []
            }
        }
        
        for template_name, config in template_files.items():
            try:
                file_path = os.path.join(self.prompts_dir, config["file"])
                template = PromptTemplate.from_file(
                    file_path,
                    input_variables=config["variables"]
                )
                self._templates[template_name] = template
                self.logger.debug(f"Loaded prompt template: {template_name}")
            except Exception as e:
                self.logger.error(f"Failed to load prompt template {template_name}: {e}")
    
    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name."""
        return self._templates.get(template_name)
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with the given variables."""
        template = self.get_template(template_name)
        if not template:
            self.logger.error(f"Template {template_name} not found")
            return ""
        
        try:
            return template.format(**kwargs)
        except Exception as e:
            self.logger.error(f"Failed to format template {template_name}: {e}")
            return ""
    
    def get_intent_detection_prompt(self, user_message: str, available_devices: str) -> str:
        """Get formatted intent detection prompt."""
        return self.format_prompt(
            "intent_detection",
            user_message=user_message,
            available_devices=available_devices
        )
    
    def get_device_control_prompt(self, user_messages: str, descriptions: str, original_prompt: str = "") -> str:
        """Get formatted device control prompt."""
        return self.format_prompt(
            "device_control",
            user_messages=user_messages,
            descriptions=descriptions,
            original_prompt=original_prompt
        )
    
    def get_device_schedule_prompt(self, user_messages: str, descriptions: str) -> str:
        """Get formatted device schedule prompt."""
        return self.format_prompt(
            "device_schedule",
            user_messages=user_messages,
            descriptions=descriptions
        )
    
    def get_scene_activation_prompt(self, user_message: str, available_scenes: str) -> str:
        """Get formatted scene activation prompt."""
        return self.format_prompt(
            "scene_activation",
            user_message=user_message,
            available_scenes=available_scenes
        )
    
    def get_response_enhancement_prompt(self, response: str) -> str:
        """Get formatted response enhancement prompt."""
        return self.format_prompt(
            "response_enhancement",
            response=response
        )
    
    def get_clarification_request_prompt(self, failed_instruction: str, reason: str) -> str:
        """Get formatted clarification request prompt."""
        return self.format_prompt(
            "clarification_request",
            failed_instruction=failed_instruction,
            reason=reason
        )
    
    def get_confirmation_request_prompt(self, action_summary: str, risk_level: str = "high") -> str:
        """Get formatted confirmation request prompt."""
        return self.format_prompt(
            "confirmation_request",
            action_summary=action_summary,
            risk_level=risk_level
        )
    
    def get_agent_system_prompt(self) -> str:
        """Get the agent system prompt."""
        return self.format_prompt("agent_system")
    
    def get_chat_prompt_template(self) -> ChatPromptTemplate:
        """Get ChatPromptTemplate for agent usage."""
        system_prompt = self.get_agent_system_prompt()
        
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("ai", "{agent_scratchpad}")
        ])
    
    def reload_templates(self):
        """Reload all templates from files."""
        self.logger.info("Reloading prompt templates...")
        self._templates.clear()
        self._load_all_templates()
        self.logger.info("Prompt templates reloaded")


# Global prompt manager instance
prompt_manager = PromptManager()

# Convenience functions
def get_intent_detection_prompt(user_message: str, available_devices: str) -> str:
    """Get formatted intent detection prompt."""
    return prompt_manager.get_intent_detection_prompt(user_message, available_devices)


def get_device_control_prompt(user_messages: str, descriptions: str, original_prompt: str = "") -> str:
    """Get formatted device control prompt."""
    return prompt_manager.get_device_control_prompt(user_messages, descriptions, original_prompt)


def get_device_schedule_prompt(user_messages: str, descriptions: str) -> str:
    """Get formatted device schedule prompt."""
    return prompt_manager.get_device_schedule_prompt(user_messages, descriptions)


def get_scene_activation_prompt(user_message: str, available_scenes: str) -> str:
    """Get formatted scene activation prompt."""
    return prompt_manager.get_scene_activation_prompt(user_message, available_scenes)


def get_response_enhancement_prompt(response: str) -> str:
    """Get formatted response enhancement prompt."""
    return prompt_manager.get_response_enhancement_prompt(response)


def get_clarification_request_prompt(failed_instruction: str, reason: str) -> str:
    """Get formatted clarification request prompt."""
    return prompt_manager.get_clarification_request_prompt(failed_instruction, reason)


def get_confirmation_request_prompt(action_summary: str, risk_level: str = "high") -> str:
    """Get formatted confirmation request prompt."""
    return prompt_manager.get_confirmation_request_prompt(action_summary, risk_level)


def get_agent_system_prompt() -> str:
    """Get the agent system prompt."""
    return prompt_manager.get_agent_system_prompt()


def get_chat_prompt_template() -> ChatPromptTemplate:
    """Get ChatPromptTemplate for agent usage."""
    return prompt_manager.get_chat_prompt_template()
