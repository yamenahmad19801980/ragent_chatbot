"""
Domain objects for the ragent_chatbot project.
Contains all Pydantic models used throughout the application.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime

class UserProfile(BaseModel):
    name: str = Field("User`s name")
    uuid: str = Field("User`s id")
    email: str = Field("Uer`s email")
    geolocation: dict[float, float] = Field(
        description="Latitude and longitude of the user, {'latitude':value,'longitude':value}",
        default_factory=dict
    )
    
class UserPreference(BaseModel):
    temp_per_room: Optional[dict[str, float]] = Field(
        description="Preferred temperature per room, {'room_name':degree}",
        default_factory=dict
    )
    temp_per_time: Optional[dict[str, float]] = Field(
        description="Preferred temperature per hour, {'hour_time': degree}",
        default_factory=dict
    )
    temp_per_season: Optional[dict[str, float]] = Field(
        description="Preferred temperature per season, {'season': degree}",
        default_factory=dict
    )
    
    bright_per_room: Optional[dict[str, float]] = Field(
        description="Preferred brightness per room  {'room_name': brightness}",
        default_factory=dict
    )
    light_temp_per_room: Optional[dict[str, float]] = Field(
        description="Preferred light temperature per room {'room_name','light_temperature'}",
        default_factory=dict
    )
    
    music_list: Optional[list[str]] = Field(
        description="List of of preferred musics", 
        default_factory=list
    )
    volume_per_room: Optional[dict[str, float]] = Field(
        description="Preferred volume per room, {'room_name':volume}", 
        default_factory=dict
    )
    
    wakeup_hour: Optional[datetime] = Field(description="Usual Wakeup hour", default=None)
    sleep_hour: Optional[datetime] = Field(description="Usual sleep hour", default=None)
    
    favorite_scenes: Optional[list[str]] = Field(
        description="Scene names the user frequently uses",
        default_factory=list
    )

class Scene(BaseModel):
    scene_name: str = Field(
        description="The name of the scene deduced from the instruction regardless of whether the scene is available or not. Should not be None"
    )
    scene_uuid: str = Field(
        description="The ID of the scene if the scene was found, otherwise None",
        default=None
    )
    
class DeviceFunction(BaseModel):
    status: str = Field(description="State indicating whether the function has been extracted successfully(Success/Failure)")
    device_uuid: str = Field(description="The ID of the device commanded by the user.")
    code: Optional[str] = Field(default=None, description="Name of the functionality(e.g. countdown)")
    value: Optional[Any] = Field(default=None, description="The value of the performed functionality,(e.g. setting countdown to 300)")
    failure_reason: Optional[str] = Field(default=None, description="Specify the reason behind the failure if any")

class ListDeviceFunction(BaseModel):
    device_functions: DeviceFunction = Field(description="A list of functions extracted from device IDs")

class DeviceSchedule(BaseModel):
    status: str = Field(description="State indicating whether the function has been extracted successfully(Success/Failure)")
    device_uuid: Optional[str] = Field(description="The ID of the device that you want to control")
    code: Optional[str] = Field(default=None, description="Name of the functionality(e.g. countdown)")
    value: Optional[Any] = Field(default=None, description="The value of the performed functionality,(e.g. setting countdown to 300)")
    days: Optional[list[str]] = Field(
        default=None,
        description="A list of days which takes any of the following arguments: Sun, Mon, Tue, Wed, Thu, Fri, Sat"
    )
    time: Optional[str] = Field(default=None, description="Time represented in the following format: HH:MM. Example: 09:37")
    failure_reason: Optional[str] = Field(default=None, description="Specify the reason behind the failure if any")
    
class Intent(BaseModel):
    Intent: Literal["control", "query", "schedule", "ambiguous", "high_risk", "conversation", "scene"] = Field(
        description="Classifies user`s command"
    )
    device_uuid: str = Field(description="The ID of the device commanded by the user.")
    user_message: str = Field(
        description="The instruction related to that specific device ID. For example, if this intent is related only to the TV and the user instruction is Turn on TV and lights then this instruction should be turn on TV. Another example: 'Turn on switch 1 in activate countdown in the 3G switch' should become 2 intents one of them is 'Turn on switch 1 in the 3G switch' and the other 'Activate countdown in the 3G switch'"
    )
    reason: str = Field(default=None, description="brief explanation of why this category was chosen")
    next_action: str = Field(default=None, description="suggested next step for this intent type")
    confidence: float = Field(default="Represents the percentage to what degree the model is confident about his chosen intent")
    product_type: str = Field(description="The type of the device commanded by the user.")

class DeviceUsageRecord(BaseModel):
    timestamp: datetime = Field(description="The time the device was controlled")
    subspace: str = Field(description="The subspace the device belongs to.")
    device_name: str = Field(description="The name of the device")
    device_uuid: str = Field(description="The Id of the device")
    code: str = Field(description="The functionality that have been affected(e.g. Switch, Countdown, etc)")
    value: Any = Field(description="The value given for the specified functionality(e.g. setting temperature to 30F)")

class Device(BaseModel):
    uuid: str = Field(description="Unique identifier for the device (backend DB ID)")
    product_type: Optional[str] = Field(description="Human-readable product type")
    name: str = Field(description="Custom or default name of the device")
    category_name: Optional[str] = Field(description="Human-readable category name")
    spaces: list[dict] = Field(description="The spaces where the device belongs")
    subspace: Optional[dict] = Field(default=None, description="The subspace where the device belongs")
    tag: Optional[str] = Field(default=None, description="Small description of the device")
