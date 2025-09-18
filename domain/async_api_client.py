"""
Async API client for Syncrow IoT platform.
Provides async/await support for better performance.
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from config import Config
from utils.logger import get_logger, log_api_call


class AsyncSyncrowAPIClient:
    """Async client for interacting with the Syncrow API."""
    
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.token = None
        self.session = None
        self.logger = get_logger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=Config.API_TIMEOUT)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def login(self, email: str, password: str) -> Optional[str]:
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
            self.logger.info(f"Attempting async login for user: {email}")
            async with self.session.post(url, headers=headers, json=body) as response:
                response_time = (time.time() - start_time) * 1000
                
                response.raise_for_status()
                data = await response.json()
                self.token = data["data"]["accessToken"]
                
                log_api_call(self.logger, "POST", url, response.status, response_time)
                self.logger.info("Async login successful")
                return self.token
                
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "POST", url, None, response_time, str(e))
            self.logger.error(f"Async login failed: {e}")
            return None
    
    async def batch_control(self, operation_type: str, devices_uuids: List[str], code: str, value: Any) -> Dict:
        """Send batch control commands to devices asynchronously."""
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
            self.logger.info(f"Async batch control: {operation_type} on {len(devices_uuids)} devices")
            async with self.session.post(url, headers=headers, json=body) as response:
                response_time = (time.time() - start_time) * 1000
                
                response.raise_for_status()
                result = await response.json()
                
                log_api_call(self.logger, "POST", url, response.status, response_time)
                self.logger.info(f"Async batch control successful for {len(devices_uuids)} devices")
                return result
                
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "POST", url, None, response_time, str(e))
            self.logger.error(f"Async batch control failed: {e}")
            return {"error": str(e)}
    
    async def add_schedule(self, device_uuid: str, category_name: str, time: str, code: str, value: Any, days: List[str]) -> Dict:
        """Add a schedule for a device asynchronously."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        body = {
            "category": category_name,
            "time": time,
            "function": {"code": code, "value": value},
            "days": days,
        }
        url = f"{self.base_url}/schedule/{device_uuid}"
        
        start_time = time.time()
        try:
            self.logger.info(f"Adding async schedule for device {device_uuid}: {time} on {days}")
            async with self.session.post(url, headers=headers, json=body) as response:
                response_time = (time.time() - start_time) * 1000
                
                response.raise_for_status()
                result = await response.json()
                
                log_api_call(self.logger, "POST", url, response.status, response_time)
                self.logger.info(f"Async schedule added successfully for device {device_uuid}")
                return result
                
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "POST", url, None, response_time, str(e))
            self.logger.error(f"Failed to add async schedule for device {device_uuid}: {e}")
            return {"error": str(e)}
    
    async def get_device_functions(self, device_uuid: str) -> Dict:
        """Get available functions for a device asynchronously."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/devices/{device_uuid}/functions"
        
        start_time = time.time()
        try:
            self.logger.debug(f"Getting async functions for device {device_uuid}")
            async with self.session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                
                response.raise_for_status()
                result = await response.json()
                
                log_api_call(self.logger, "GET", url, response.status, response_time)
                self.logger.debug(f"Retrieved {len(result.get('data', {}).get('functions', []))} async functions for device {device_uuid}")
                return result
                
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, None, response_time, str(e))
            self.logger.error(f"Failed to get async functions for device {device_uuid}: {e}")
            return {"error": str(e)}
    
    async def get_status(self, device_uuid: str) -> Dict:
        """Get status of a device asynchronously."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/devices/{device_uuid}/functions/status"
        
        start_time = time.time()
        try:
            self.logger.debug(f"Getting async status for device {device_uuid}")
            async with self.session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                
                response.raise_for_status()
                result = await response.json()
                
                log_api_call(self.logger, "GET", url, response.status, response_time)
                self.logger.debug(f"Retrieved async status for device {device_uuid}")
                return result
                
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, None, response_time, str(e))
            self.logger.error(f"Failed to get async status for device {device_uuid}: {e}")
            return {"error": str(e)}
    
    async def get_devices_per_space(self, project_uuid: str, community_uuid: str, space_uuid: str) -> Dict:
        """Get all devices in a specific space asynchronously."""
        headers = {"accept": "*/*", "Authorization": f"Bearer {self.token}"}
        url = f"{self.base_url}/projects/{project_uuid}/communities/{community_uuid}/spaces/{space_uuid}/devices"
        
        start_time = time.time()
        try:
            self.logger.info(f"Getting async devices for space {space_uuid}")
            async with self.session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                
                response.raise_for_status()
                result = await response.json()
                
                log_api_call(self.logger, "GET", url, response.status, response_time)
                device_count = len(result.get('data', []))
                self.logger.info(f"Retrieved {device_count} async devices for space {space_uuid}")
                return result
                
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, None, response_time, str(e))
            self.logger.error(f"Failed to get async devices for space {space_uuid}: {e}")
            return {"error": str(e), "statusCode": 500, "data": []}
    
    async def trigger_scene(self, scene_uuid: str) -> Dict:
        """Trigger a scene asynchronously."""
        headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.base_url}/scene/tap-to-run/{scene_uuid}/trigger"
        
        start_time = time.time()
        try:
            self.logger.info(f"Triggering async scene {scene_uuid}")
            async with self.session.post(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                
                response.raise_for_status()
                result = await response.json()
                
                log_api_call(self.logger, "POST", url, response.status, response_time)
                self.logger.info(f"Async scene {scene_uuid} triggered successfully")
                return result
                
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "POST", url, None, response_time, str(e))
            self.logger.error(f"Failed to trigger async scene {scene_uuid}: {e}")
            return {"error": str(e)}
    
    async def get_scenes(self, project_uuid: str, community_uuid: str, space_uuid: str) -> Dict:
        """Get all scenes for a space asynchronously."""
        headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.base_url}/projects/{project_uuid}/communities/{community_uuid}/spaces/{space_uuid}/scenes?showInHomePage=true"
        
        start_time = time.time()
        try:
            self.logger.info(f"Getting async scenes for space {space_uuid}")
            async with self.session.get(url, headers=headers) as response:
                response_time = (time.time() - start_time) * 1000
                
                response.raise_for_status()
                result = await response.json()
                
                log_api_call(self.logger, "GET", url, response.status, response_time)
                scene_count = len(result.get('data', []))
                self.logger.info(f"Retrieved {scene_count} async scenes for space {space_uuid}")
                return result
                
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            log_api_call(self.logger, "GET", url, None, response_time, str(e))
            self.logger.error(f"Failed to get async scenes for space {space_uuid}: {e}")
            return {"error": str(e), "data": []}
    
    async def batch_control_multiple(self, operations: List[Dict]) -> List[Dict]:
        """Execute multiple batch control operations concurrently."""
        tasks = []
        for operation in operations:
            task = self.batch_control(
                operation["operation_type"],
                operation["devices_uuids"],
                operation["code"],
                operation["value"]
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "operation": operations[i]
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_multiple_device_status(self, device_uuids: List[str]) -> List[Dict]:
        """Get status for multiple devices concurrently."""
        tasks = [self.get_status(device_uuid) for device_uuid in device_uuids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "device_uuid": device_uuids[i],
                    "error": str(result)
                })
            else:
                processed_results.append({
                    "device_uuid": device_uuids[i],
                    "status": result
                })
        
        return processed_results
