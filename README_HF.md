---
title: Smart Home Assistant
emoji: 🏠
colorFrom: blue
colorTo: purple
sdk: gradio
python_version: "3.11"
sdk_version: "5.45.0"
app_file: app.py
pinned: false
hf_oauth: true
hf_oauth_scopes:
- inference-api
license: mit
short_description: Intelligent smart home assistant with IoT device control
---

# Smart Home Assistant

An intelligent smart home assistant built with LangGraph that can control IoT devices, schedule actions, and engage in natural conversation.

## Features

- 🤖 **Intelligent Intent Detection**: Automatically classifies user commands
- 🏠 **IoT Device Control**: Control switches, AC, lights, curtains, and other smart devices  
- ⏰ **Device Scheduling**: Schedule device actions for specific times and days
- 🎬 **Scene Management**: Trigger smart home scenes for different moods/activities
- 🔍 **Web Search**: Answer general questions using web search capabilities
- 💬 **Natural Conversation**: Engage in friendly chat and general conversation

## Usage Examples

### Device Control
- "Turn on the living room lights"
- "Set the AC temperature to 72 degrees"
- "Turn off switch 1 in the 3 gang switch"

### Device Queries
- "What's the status of the kitchen switch?"
- "Is the AC running?"

### Scheduling
- "Schedule the AC to turn on at 8 AM tomorrow"
- "Turn on the lights at 7 PM every weekday"

### Scenes
- "Activate movie night scene"
- "Make it cozy"

### General Conversation
- "What's the weather like today?"
- "Tell me a joke"
- "Search for Thai restaurants nearby"

## Architecture

Built with:
- **LangGraph**: For complex conversation flows and intent routing
- **Gradio**: For the web interface
- **Qwen LLM**: For natural language understanding
- **Syncrow API**: For IoT device integration

The assistant uses advanced intent detection to understand user commands and route them to appropriate handlers for device control, scheduling, scene activation, or general conversation.
