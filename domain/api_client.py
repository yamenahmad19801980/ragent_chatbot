"""
API client for Syncrow IoT platform.
Thin wrapper around the Syncrow API endpoints with comprehensive logging.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from config import Config
from utils.logger import get_logger, log_api_call

class SyncrowAPIClient:
    """Client for interacting with the Syncrow API."""
    
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.token = None
        self.logger = get_logger(__name__)
    
    def login(self, email: str, password: str) -> Optional[str]:
        """Login to the Syncrow API and return access token."""
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json"
        }
        body = {
            "email": email,
            "password": password
        }
        url = f"{self.base_url}/authentication/user/login"
        
        start_time = time.time()
        try:
            self.logger.info(f"Attempting login for user: {email}")
            response = requests.post(url, headers=headers, json=body, timeout=Config.API_TIMEOUT)
            response_time = (time.time() - start_time) * 1000
            
            response.raise_for_status()
            self.token = response.json()["data"]["accessToken"]
            
            log_api_call(self.logger, "POST", url, response.status_code, response_time)
            self.logger.info("Login successful")
            return self.token
            
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "POST", url, None, response_time, str(e))
            self.logger.error(f"Login failed: {e}")
            return None
    
    def batch_control(self, operation_type: str, devices_uuids: List[str], code: str, value: Any) -> Dict:
        """Send batch control commands to devices."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        body = {
            "operationType": operation_type,
            "devicesUuid": devices_uuids,
            "code": code,
            "value": value,
        }
        url = f"{self.base_url}/devices/batch"
        
        start_time = time.time()
        try:
            self.logger.info(f"Batch control: {operation_type} on {len(devices_uuids)} devices")
            response = requests.post(url, headers=headers, json=body, timeout=Config.API_TIMEOUT)
            response_time = (time.time() - start_time) * 1000
            
            response.raise_for_status()
            result = response.json()
            
            log_api_call(self.logger, "POST", url, response.status_code, response_time)
            self.logger.info(f"Batch control successful for {len(devices_uuids)} devices")
            return result
            
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "POST", url, None, response_time, str(e))
            self.logger.error(f"Batch control failed: {e}")
            return {"error": str(e)}
    
    def add_schedule(self, device_uuid: str, category_name: str, time: str, code: str, value: Any, days: List[str]) -> Dict:
        """Add a schedule for a device."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        body = {
            "category": category_name,
            "time": time,
            "function": {"code": code, "value": value},
            "days": days,
        }
        url = f"{self.base_url}/schedule/{device_uuid}"
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[add_schedule] Error: {e}")
            return {"error": str(e)}
    
    def get_device_functions(self, device_uuid: str) -> Dict:
        """Get available functions for a device."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/devices/{device_uuid}/functions"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[get_device_functions] Error: {e}")
            return {"error": str(e)}
    
    def get_status(self, device_uuid: str) -> Dict:
        """Get status of a device."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/devices/{device_uuid}/functions/status"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[get_status] Error: {e}")
            return {"error": str(e)}
    
    def get_devices_per_space(self, project_uuid: str, community_uuid: str, space_uuid: str) -> Dict:
        """Get all devices in a specific space."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/projects/{project_uuid}/communities/{community_uuid}/spaces/{space_uuid}/devices"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[get_devices_per_space] Error: {e}")
            return {"error": str(e), "statusCode": 500, "data": []}
    
    def trigger_scene(self, scene_uuid: str) -> Dict:
        """Trigger a scene."""
        headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.base_url}/scene/tap-to-run/{scene_uuid}/trigger"
        
        start_time = time.time()
        try:
            self.logger.info(f"Triggering scene {scene_uuid}")
            response = requests.post(url, headers=headers, timeout=Config.API_TIMEOUT)
            response_time = (time.time() - start_time) * 1000
            
            response.raise_for_status()
            result = response.json()
            
            log_api_call(self.logger, "POST", url, response.status_code, response_time)
            self.logger.info(f"Scene {scene_uuid} triggered successfully")
            return result
            
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "POST", url, None, response_time, str(e))
            self.logger.error(f"Failed to trigger scene {scene_uuid}: {e}")
            return {"error": str(e)}
    
    def get_scenes(self, project_uuid: str, community_uuid: str, space_uuid: str) -> Dict:
        """Get all scenes for a space."""
        headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.base_url}/projects/{project_uuid}/communities/{community_uuid}/spaces/{space_uuid}/scenes?showInHomePage=true"
        
        start_time = time.time()
        try:
            self.logger.info(f"Getting scenes for space {space_uuid}")
            response = requests.get(url, headers=headers, timeout=Config.API_TIMEOUT)
            response_time = (time.time() - start_time) * 1000
            
            response.raise_for_status()
            result = response.json()
            
            log_api_call(self.logger, "GET", url, response.status_code, response_time)
            scene_count = len(result.get('data', []))
            self.logger.info(f"Retrieved {scene_count} scenes for space {space_uuid}")
            return result
            
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, None, response_time, str(e))
            self.logger.error(f"Failed to get scenes for space {space_uuid}: {e}")
            return {"error": str(e), "data": []}
