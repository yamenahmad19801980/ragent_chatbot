"""
Graph visualization utilities for the ragent_chatbot LangGraph.
"""

import json
from typing import Dict, List, Any

def create_graph_mermaid() -> str:
    """
    Create a Mermaid diagram representation of the LangGraph.
    
    Returns:
        str: Mermaid diagram code
    """
    mermaid_code = """
graph TD
    START([START]) --> detect_intent[detect_intent]
    
    detect_intent --> route_decision{route_message}
    
    route_decision -->|ambiguous| request_clarification[request_clarification]
    route_decision -->|control| handle_control[handle_control]
    route_decision -->|query| handle_query[handle_query]
    route_decision -->|schedule| handle_schedule[handle_schedule]
    route_decision -->|scene| handle_scene[handle_scene]
    route_decision -->|conversation| chat_node[chat_node]
    route_decision -->|high_risk| request_confirmation[request_confirmation]
    route_decision -->|END| END_NODE([END])
    
    request_clarification --> enhance_response[enhance_response]
    handle_control --> enhance_response
    handle_query --> enhance_response
    handle_schedule --> enhance_response
    handle_scene --> enhance_response
    chat_node --> enhance_response
    
    request_confirmation --> confirmation_decision{confirmation_result}
    confirmation_decision -->|confirmed| handle_control
    confirmation_decision -->|cancelled| END_NODE
    confirmation_decision -->|unclear| request_confirmation
    
    enhance_response --> END_NODE
    
    %% Styling
    classDef startEnd fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef process fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef enhance fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    
    class START,END_NODE startEnd
    class detect_intent,handle_control,handle_query,handle_schedule,handle_scene,chat_node,request_clarification,request_confirmation process
    class route_decision,confirmation_decision decision
    class enhance_response enhance
    """
    
    return mermaid_code.strip()

def create_graph_description() -> str:
    """
    Create a text description of the graph structure.
    
    Returns:
        str: Graph description
    """
    description = """
RAGENT CHATBOT LANGGRAPH STRUCTURE
==================================

START
  ↓
detect_intent
  ↓
route_message (Decision Node)
  ├── ambiguous → request_clarification
  ├── control → handle_control
  ├── query → handle_query
  ├── schedule → handle_schedule
  ├── scene → handle_scene
  ├── conversation → chat_node
  ├── high_risk → request_confirmation
  └── END → END

CONFIRMATION FLOW:
request_confirmation → confirmation_result
  ├── confirmed → handle_control
  ├── cancelled → END
  └── unclear → request_confirmation

ENHANCEMENT FLOW:
All user-facing nodes → enhance_response → END

NODE DESCRIPTIONS:
==================

1. detect_intent
   - Analyzes user input
   - Classifies intent (control, query, schedule, etc.)
   - Identifies target devices
   - Returns intent classification

2. handle_control
   - Controls IoT devices
   - Sends commands to Syncrow API
   - Handles device responses
   - Returns control results

3. handle_query
   - Queries device status
   - Gets device information
   - Returns status data

4. handle_schedule
   - Schedules device actions
   - Sets up recurring tasks
   - Manages time-based controls

5. handle_scene
   - Activates smart home scenes
   - Triggers predefined configurations
   - Manages scene states

6. chat_node
   - Handles general conversation
   - Uses web search tools
   - Provides general assistance

7. request_clarification
   - Asks for clarification
   - Handles ambiguous requests
   - Provides helpful prompts

8. request_confirmation
   - Requests confirmation for high-risk actions
   - Implements safety measures
   - Handles user approval

9. enhance_response
   - Improves response tone
   - Makes responses more user-friendly
   - Final response processing

CONDITIONAL ROUTING:
===================

The graph uses conditional edges based on:
- Intent classification results
- User confirmation responses
- Error conditions
- Safety requirements

MEMORY AND STATE:
================

- Messages: Conversation history
- Device data: IoT device information
- User context: User preferences and settings
- API state: Syncrow API connection status
"""
    
    return description

def create_node_details() -> Dict[str, Any]:
    """
    Create detailed information about each node.
    
    Returns:
        Dict: Node details
    """
    return {
        "nodes": {
            "detect_intent": {
                "type": "processing",
                "description": "Analyzes user input and classifies intent",
                "inputs": ["user_message", "device_list"],
                "outputs": ["intent_classification", "device_uuid", "reason"],
                "tools_used": ["Intent model"],
                "api_calls": ["get_devices_per_space"]
            },
            "handle_control": {
                "type": "action",
                "description": "Controls IoT devices via Syncrow API",
                "inputs": ["device_uuid", "user_message", "product_type"],
                "outputs": ["control_result", "success_status"],
                "tools_used": ["DeviceFunction model", "batch_control API"],
                "api_calls": ["batch_control", "get_device_functions"]
            },
            "handle_query": {
                "type": "action",
                "description": "Queries device status and information",
                "inputs": ["device_uuid"],
                "outputs": ["device_status", "device_info"],
                "tools_used": [],
                "api_calls": ["get_status"]
            },
            "handle_schedule": {
                "type": "action",
                "description": "Schedules device actions for specific times",
                "inputs": ["device_uuid", "user_message", "time", "days"],
                "outputs": ["schedule_result", "schedule_id"],
                "tools_used": ["DeviceSchedule model"],
                "api_calls": ["add_schedule", "get_device_functions"]
            },
            "handle_scene": {
                "type": "action",
                "description": "Activates smart home scenes",
                "inputs": ["user_message", "available_scenes"],
                "outputs": ["scene_result", "scene_name"],
                "tools_used": ["Scene model"],
                "api_calls": ["get_scenes", "trigger_scene"]
            },
            "chat_node": {
                "type": "conversation",
                "description": "Handles general conversation and web search",
                "inputs": ["user_message", "chat_history"],
                "outputs": ["response", "search_results"],
                "tools_used": ["web_search", "general_llm"],
                "api_calls": ["Tavily search API"]
            },
            "request_clarification": {
                "type": "interaction",
                "description": "Requests clarification for ambiguous requests",
                "inputs": ["ambiguous_intent", "reason"],
                "outputs": ["clarification_message"],
                "tools_used": [],
                "api_calls": []
            },
            "request_confirmation": {
                "type": "interaction",
                "description": "Requests confirmation for high-risk actions",
                "inputs": ["high_risk_action"],
                "outputs": ["confirmation_request"],
                "tools_used": [],
                "api_calls": []
            },
            "enhance_response": {
                "type": "processing",
                "description": "Enhances response tone and user-friendliness",
                "inputs": ["raw_response"],
                "outputs": ["enhanced_response"],
                "tools_used": ["response_enhancement_llm"],
                "api_calls": []
            }
        },
        "edges": {
            "conditional": [
                "route_message → handle_control",
                "route_message → handle_query", 
                "route_message → handle_schedule",
                "route_message → handle_scene",
                "route_message → chat_node",
                "route_message → request_clarification",
                "route_message → request_confirmation",
                "confirmation_result → handle_control",
                "confirmation_result → END"
            ],
            "direct": [
                "START → detect_intent",
                "handle_control → enhance_response",
                "handle_query → enhance_response",
                "handle_schedule → enhance_response", 
                "handle_scene → enhance_response",
                "chat_node → enhance_response",
                "request_clarification → enhance_response",
                "enhance_response → END"
            ]
        }
    }

def save_graph_files():
    """Save graph visualization files."""
    # Save Mermaid diagram
    with open("graph_visualization.mmd", "w", encoding="utf-8") as f:
        f.write(create_graph_mermaid())
    
    # Save graph description
    with open("graph_description.txt", "w", encoding="utf-8") as f:
        f.write(create_graph_description())
    
    # Save node details
    with open("node_details.json", "w", encoding="utf-8") as f:
        json.dump(create_node_details(), f, indent=2)
    
    print("Graph visualization files created:")
    print("- graph_visualization.mmd (Mermaid diagram)")
    print("- graph_description.txt (Text description)")
    print("- node_details.json (Detailed node information)")

if __name__ == "__main__":
    save_graph_files()
