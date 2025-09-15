"""
Device control tools for IoT devices via Syncrow API.
This module now serves as a compatibility layer for the centralized device service.
"""

from typing import List
from langchain.agents import Tool
from domain.api_client import SyncrowAPIClient
from services.device_service import DeviceService

def create_device_tools(api_client: SyncrowAPIClient) -> List[Tool]:
    """Create LangChain tools for device control using centralized service."""
    device_service = DeviceService(api_client)
    
    def control_device_tool(device_uuid: str, user_message: str, product_type: str) -> str:
        """Tool for controlling devices."""
        result = device_service.control_device(device_uuid, user_message, product_type)
        return str(result)
    
    def query_device_tool(device_uuid: str) -> str:
        """Tool for querying device status."""
        result = device_service.query_device_status(device_uuid)
        return str(result)
    
    def schedule_device_tool(device_uuid: str, user_message: str) -> str:
        """Tool for scheduling device actions."""
        result = device_service.schedule_device(device_uuid, user_message)
        return str(result)
    
    return [
        Tool(
            name="control_device",
            func=lambda device_uuid, user_message, product_type: control_device_tool(device_uuid, user_message, product_type),
            description="Control IoT devices (turn on/off, set temperature, etc.)"
        ),
        Tool(
            name="query_device",
            func=lambda device_uuid: query_device_tool(device_uuid),
            description="Query the status of IoT devices"
        ),
        Tool(
            name="schedule_device",
            func=lambda device_uuid, user_message: schedule_device_tool(device_uuid, user_message),
            description="Schedule device actions for specific times and days"
        )
    ]