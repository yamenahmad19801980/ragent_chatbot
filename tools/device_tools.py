"""
Device control tools for IoT devices via Syncrow API.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.agents import Tool

from config import Config
from domain.api_client import SyncrowAPIClient
from domain.objects import Device, DeviceFunction, DeviceSchedule, Scene
from llm import get_qwen_llm

class DeviceTools:
    """Tools for controlling IoT devices."""
    
    def __init__(self, api_client: SyncrowAPIClient):
        self.api_client = api_client
        self.llm = get_qwen_llm()
        self.device_descriptions = pd.read_csv(Config.CSV_PATH)
    
    def get_devices_in_space(self, project_uuid: str, community_uuid: str, space_uuid: str) -> List[Device]:
        """Get all devices in a specific space."""
        devices_json = self.api_client.get_devices_per_space(project_uuid, community_uuid, space_uuid)
        
        if devices_json.get("statusCode") == 200:
            devices = []
            for device_json in devices_json["data"]:
                devices.append(Device(
                    uuid=device_json["uuid"],
                    product_type=device_json["productType"],
                    name=device_json["name"],
                    category_name=device_json["categoryName"],
                    spaces=device_json["spaces"],
                    subspace={
                        "uuid": device_json["subspace"]["uuid"],
                        "subspaceName": device_json["subspace"]["subspaceName"]
                    } if device_json["subspace"] else None,
                    tag=device_json["deviceTag"]["name"] if device_json["deviceTag"] else None
                ))
            return devices
        else:
            print(f"[WARN] Failed to fetch devices: {devices_json}")
            return []
    
    def control_device(self, device_uuid: str, user_message: str, product_type: str) -> Dict[str, Any]:
        """Control a device based on user message."""
        # Get device functions
        functions_json = self.api_client.get_device_functions(device_uuid)
        if functions_json.get("statusCode") != 201:
            return {"error": "Failed to get device functions"}
        
        possible_values = functions_json["data"]["functions"]
        
        # Get device descriptions for this product type
        rows = self.device_descriptions[self.device_descriptions["product_type"] == product_type]
        descriptions = []
        for row in rows.values:
            code, code_description, value, value_description, product_type = row
            descriptions.append(f"""
                "Product Type": {product_type},
                "Code": {code},
                "Code Description": {code_description},
                "Value": {value},
                "Value Description": {value_description}
            """)
        
        # Use LLM to determine the correct function and value
        llm_tool_functions = self.llm.bind_tools(tools=[DeviceFunction], parallel_tool_calls=True)
        
        system_prompt = f"""You are an IoT assistant. 
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
        
        response = llm_tool_functions.invoke([SystemMessage(content=system_prompt)])
        
        results = []
        for tool_call in response.tool_calls:
            if tool_call["args"]["status"] == "Success":
                code = tool_call["args"]["code"]
                value = tool_call["args"]["value"]
                
                control_response = self.api_client.batch_control(
                    "COMMAND", [device_uuid], code, value
                )
                results.append({
                    "device_uuid": device_uuid,
                    "success": True,
                    "response": control_response
                })
            else:
                results.append({
                    "device_uuid": device_uuid,
                    "success": False,
                    "error": tool_call["args"].get("failure_reason", "Unknown failure")
                })
        
        return {"results": results}
    
    def query_device_status(self, device_uuid: str) -> Dict[str, Any]:
        """Query the status of a device."""
        status = self.api_client.get_status(device_uuid)
        return {"device_uuid": device_uuid, "status": status}
    
    def schedule_device(self, device_uuid: str, user_message: str) -> Dict[str, Any]:
        """Schedule a device action."""
        # Get device functions
        functions_json = self.api_client.get_device_functions(device_uuid)
        if functions_json.get("statusCode") != 201:
            return {"error": "Failed to get device functions"}
        
        possible_values = functions_json["data"]["functions"]
        
        # Use LLM to determine schedule parameters
        llm_tool_functions = self.llm.bind_tools(tools=[DeviceSchedule], parallel_tool_calls=True)
        
        system_prompt = f"""You are an IoT assistant for scheduling devices.
Your job is to extract scheduling parameters from the user message including time, days, and device function.

User message: {user_message}
Device UUID: {device_uuid}

Available functions for this device:
{possible_values}

Extract the following:
- time: in HH:MM format
- days: list of days (Sun, Mon, Tue, Wed, Thu, Fri, Sat)
- code: function code to execute
- value: value for the function
"""
        
        response = llm_tool_functions.invoke([SystemMessage(content=system_prompt)])
        
        results = []
        for tool_call in response.tool_calls:
            if tool_call["args"]["status"] == "Success":
                code = tool_call["args"]["code"]
                value = tool_call["args"]["value"]
                time = tool_call["args"]["time"]
                days = tool_call["args"]["days"]
                
                schedule_response = self.api_client.add_schedule(
                    device_uuid, "category_name", time, code, value, days
                )
                results.append({
                    "device_uuid": device_uuid,
                    "success": True,
                    "response": schedule_response
                })
            else:
                results.append({
                    "device_uuid": device_uuid,
                    "success": False,
                    "error": tool_call["args"].get("failure_reason", "Unknown failure")
                })
        
        return {"results": results}
    
    def trigger_scene_by_name(self, scene_name: str, available_scenes: List[Dict]) -> Dict[str, Any]:
        """Trigger a scene by name."""
        # Use LLM to match scene name
        llm_with_scene = self.llm.bind_tools(tools=[Scene])
        
        system_prompt = f"""
        You are an IoT assistant that determines which scene to trigger based on user prompt.
        If the scene is not available then just set the field uuid to None.
        
        User message: {scene_name}
        Available scenes: {available_scenes}
        """
        
        response = llm_with_scene.invoke([SystemMessage(content=system_prompt)])
        
        if response.tool_calls and response.tool_calls[0]["args"]["scene_uuid"]:
            scene_uuid = response.tool_calls[0]["args"]["scene_uuid"]
            scene_name = response.tool_calls[0]["args"]["scene_name"]
            
            result = self.api_client.trigger_scene(scene_uuid)
            return {
                "success": True,
                "scene_name": scene_name,
                "response": result
            }
        else:
            return {
                "success": False,
                "error": f"Scene '{scene_name}' not found"
            }

def create_device_tools(api_client: SyncrowAPIClient) -> List[Tool]:
    """Create LangChain tools for device control."""
    device_tools = DeviceTools(api_client)
    
    def control_device_tool(device_uuid: str, user_message: str, product_type: str) -> str:
        """Tool for controlling devices."""
        result = device_tools.control_device(device_uuid, user_message, product_type)
        return str(result)
    
    def query_device_tool(device_uuid: str) -> str:
        """Tool for querying device status."""
        result = device_tools.query_device_status(device_uuid)
        return str(result)
    
    def schedule_device_tool(device_uuid: str, user_message: str) -> str:
        """Tool for scheduling device actions."""
        result = device_tools.schedule_device(device_uuid, user_message)
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
