"""
API client for Syncrow IoT platform.
Thin wrapper around the Syncrow API endpoints.
"""

import requests
from typing import Dict, List, Optional, Any
from config import Config

class SyncrowAPIClient:
    """Client for interacting with the Syncrow API."""
    
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.token = None
    
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
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            self.token = response.json()["data"]["accessToken"]
            return self.token
        except requests.exceptions.RequestException as e:
            print(f"[login] Error login: {e}")
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
        
        try:
            response = requests.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[batch_control] Error: {e}")
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
        
        try:
            response = requests.post(url, headers=headers)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[trigger_scene] Error triggering scene: {e}")
            return {"error": str(e)}
    
    def get_scenes(self, project_uuid: str, community_uuid: str, space_uuid: str) -> Dict:
        """Get all scenes for a space."""
        headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.base_url}/projects/{project_uuid}/communities/{community_uuid}/spaces/{space_uuid}/scenes?showInHomePage=true"
        
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[get_scenes] Error getting scenes: {e}")
            return {"error": str(e)}
