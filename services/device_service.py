"""
Centralized device service for IoT device operations.
Eliminates code duplication by providing unified device control logic.
"""

import pandas as pd
import time
from typing import List, Dict, Any, Optional
from langchain_core.messages import SystemMessage

from config import Config
from domain.api_client import SyncrowAPIClient
from domain.objects import Device, DeviceFunction, DeviceSchedule, Scene
from llm import get_qwen_llm
from prompts.prompt_manager import prompt_manager
from utils.cache import cached, cache_key_for_device_operation, cache_manager
from utils.logger import get_logger, log_device_operation, log_performance


class DeviceService:
    """Centralized service for all device operations."""
    
    def __init__(self, api_client: SyncrowAPIClient):
        self.api_client = api_client
        self.llm = get_qwen_llm()
        self.device_descriptions = pd.read_csv(Config.CSV_PATH)
        self.logger = get_logger(__name__)
    
    def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid token before making API calls."""
        if not self.api_client.token:
            self.logger.warning("No token available, attempting to login...")
            from config import Config
            new_token = self.api_client.login(Config.EMAIL, Config.PASSWORD)
            return new_token is not None
        return True
    
    @cached("devices_in_space", ttl=300)  # Cache for 5 minutes
    def get_devices_in_space(self, project_uuid: str, community_uuid: str, space_uuid: str) -> List[Device]:
        """Get all devices in a specific space."""
        start_time = time.time()
        
        # Ensure we have a valid token
        if not self._ensure_valid_token():
            self.logger.error("Failed to obtain valid token for device operation")
            return []
        
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
            
            duration = time.time() - start_time
            log_performance(self.logger, "get_devices_in_space", duration, {"device_count": len(devices)})
            self.logger.info(f"Retrieved {len(devices)} devices for space {space_uuid}")
            return devices
        else:
            self.logger.warning(f"Failed to fetch devices: {devices_json}")
            return []
    
    def get_device_descriptions(self, product_type: str) -> List[str]:
        """Get device descriptions for a specific product type."""
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
        return descriptions
    
    def control_device(self, device_uuid: str, user_message: str, product_type: str) -> Dict[str, Any]:
        """Control a device based on user message."""
        start_time = time.time()
        
        # Ensure we have a valid token
        if not self._ensure_valid_token():
            self.logger.error("Failed to obtain valid token for device control")
            return {"error": "Authentication failed. Please re-login."}
        
        # Get device functions (with caching)
        functions_json = self.api_client.get_device_functions(device_uuid)
        if functions_json.get("statusCode") != 201:
            log_device_operation(self.logger, "control_device", device_uuid, False, 
                               {"error": "Failed to get device functions"})
            return {"error": "Failed to get device functions"}
        
        possible_values = functions_json["data"]["functions"]
        descriptions = self.get_device_descriptions(product_type)
        
        # Use LLM to determine the correct function and value
        llm_tool_functions = self.llm.bind_tools(tools=[DeviceFunction], parallel_tool_calls=True)
        
        system_prompt = prompt_manager.get_device_control_prompt(
            str([{"device_uuid": device_uuid, "user_message": user_message, "product_type": product_type}]),
            "\n".join(descriptions),
            user_message
        )
        
        response = llm_tool_functions.invoke([SystemMessage(content=system_prompt)])
        
        results = []
        for tool_call in response.tool_calls:
            if tool_call["args"]["status"] == "Success":
                code = tool_call["args"]["code"]
                value = tool_call["args"]["value"]
                
                control_response = self.api_client.batch_control(
                    "COMMAND", [device_uuid], code, value
                )
                
                success = "error" not in control_response
                log_device_operation(self.logger, "control_device", device_uuid, success, 
                                   {"code": code, "value": value, "response": control_response})
                
                results.append({
                    "device_uuid": device_uuid,
                    "success": success,
                    "response": control_response
                })
            else:
                error_msg = tool_call["args"].get("failure_reason", "Unknown failure")
                log_device_operation(self.logger, "control_device", device_uuid, False, 
                                   {"error": error_msg})
                results.append({
                    "device_uuid": device_uuid,
                    "success": False,
                    "error": error_msg
                })
        
        duration = time.time() - start_time
        log_performance(self.logger, "control_device", duration, {"device_uuid": device_uuid})
        
        return {"results": results}
    
    def control_multiple_devices(self, user_messages: List[Dict], devices: List[Device]) -> List[str]:
        """Control multiple devices based on user messages."""
        control_responses = []
        
        # Process each device individually for better reliability
        for user_message in user_messages:
            device_uuid = user_message["device_uuid"]
            user_message_text = user_message["user_message"]
            product_type = user_message["product_type"]
            
            # Use the single device control method for each device
            result = self.control_device(device_uuid, user_message_text, product_type)
            
            if "error" in result:
                control_responses.append(f"Error controlling device {device_uuid}: {result['error']}")
            elif result.get("results"):
                for device_result in result["results"]:
                    if device_result["success"]:
                        control_responses.append(f"✅ Successfully controlled device {device_uuid}")
                    else:
                        control_responses.append(f"❌ Failed to control device {device_uuid}: {device_result['error']}")
            else:
                control_responses.append(f"❌ No action taken for device {device_uuid}")
        
        if not control_responses:
            control_responses = ["No devices were controlled."]
        
        return control_responses
    
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
    
    def schedule_multiple_devices(self, user_messages: List[Dict]) -> List[str]:
        """Schedule multiple devices based on user messages."""
        code_descriptions = {"control": "Commands: open, stop, close - controls the direction of the curtains"}
        descriptions = []
        llm_tool_functions = self.llm.bind_tools(tools=[DeviceSchedule], parallel_tool_calls=True)
        
        for user_message in user_messages:
            device_uuid = user_message["device_uuid"]
            functions_json = self.api_client.get_device_functions(device_uuid)
            if functions_json.get("statusCode") == 201:
                possible_values = functions_json["data"]["functions"]
                user_message["possible_values"] = possible_values
                for possible_value in possible_values:
                    if possible_value["code"] in code_descriptions.keys():
                        descriptions.append({possible_value["code"]: code_descriptions[possible_value["code"]]})
            else:
                print("[WARN] Failed at fetching functions")
                user_message["possible_values"] = None
        
        system_prompt = prompt_manager.get_device_schedule_prompt(str(user_messages), str(descriptions))
        
        response = llm_tool_functions.invoke([SystemMessage(content=system_prompt)])
        AI_messages = []
        
        for tool_call in response.tool_calls:
            if tool_call["args"]["status"] == "Success":
                code = tool_call["args"]["code"]
                value = tool_call["args"]["value"]
                device_uuid = tool_call["args"]["device_uuid"]
                time = tool_call["args"]["time"]
                days = tool_call["args"]["days"]
                
                control_response = self.api_client.add_schedule(device_uuid, "category_name", time, code, value, days)
                print(control_response)
                AI_messages.append(control_response)
            else:
                print(tool_call["args"]["failure_reason"])
        
        return AI_messages
    
    def trigger_scene_by_name(self, scene_name: str, available_scenes: List[Dict]) -> Dict[str, Any]:
        """Trigger a scene by name."""
        # Use LLM to match scene name
        llm_with_scene = self.llm.bind_tools(tools=[Scene])
        
        system_prompt = prompt_manager.get_scene_activation_prompt(scene_name, str(available_scenes))
        
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
    
    def get_scenes(self, project_uuid: str, community_uuid: str, space_uuid: str) -> List[Dict]:
        """Get all scenes for a space."""
        scenes = self.api_client.get_scenes(project_uuid, community_uuid, space_uuid)
        collected_scenes = []
        for scene in scenes.get("data", []):
            collected_scenes.append({
                "scene_name": scene["name"],
                "scene_uuid": scene["uuid"]
            })
        return collected_scenes
