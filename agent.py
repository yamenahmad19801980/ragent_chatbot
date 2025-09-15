"""
Main agent implementation using LangGraph.
Handles intent detection, routing, and execution of various commands.
"""

import json
from typing import List, Dict, Any, Literal, Sequence, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage, messages_from_dict, messages_to_dict
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt
from typing_extensions import Annotated, TypedDict
import pandas as pd

from config import Config
from domain.api_client import SyncrowAPIClient
from domain.objects import Device, Intent, DeviceFunction, DeviceSchedule, Scene
from llm import get_qwen_llm
from llm.langsmith_config import setup_langsmith, create_run_name
from memory import ChatMemory
from tool_registry import ToolRegistry

class GraphState(TypedDict):
    """State model for the agent graph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]

class RagentChatbot:
    """Main chatbot agent using LangGraph."""
    
    def __init__(self):
        self.llm = get_qwen_llm()
        self.memory = ChatMemory()
        self.tool_registry = ToolRegistry()
        self.api_client = self.tool_registry.get_api_client()
        self.device_descriptions = pd.read_csv(Config.CSV_PATH)
        
        # Setup LangSmith for tracking and debugging
        self.langsmith_enabled = setup_langsmith()
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        builder = StateGraph(MessagesState)
        
        # Add nodes
        builder.add_node("detect_intent", self._detect_intent)
        builder.add_node("request_clarification", self._request_clarification)
        builder.add_node("request_confirmation", self._request_confirmation)
        builder.add_node("handle_query", self._handle_query)
        builder.add_node("handle_schedule", self._handle_schedule)
        builder.add_node("handle_control", self._handle_control)
        builder.add_node("handle_scene", self._handle_scene)
        builder.add_node("chat_node", self._chat_node)
        builder.add_node("enhance_response", self._enhance_response)
        
        # Add edges
        builder.add_edge(START, "detect_intent")
        builder.add_conditional_edges(
            "detect_intent",
            self._route_message,
            {
                "request_clarification": "request_clarification",
                "request_confirmation": "request_confirmation",
                "handle_control": "handle_control",
                "handle_query": "handle_query",
                "handle_schedule": "handle_schedule",
                "chat_node": "chat_node",
                "handle_scene": "handle_scene",
                END: "__end__"
            }
        )
        
        # Pass user-visible branches through enhancer
        for node in ["handle_control", "handle_query", "handle_schedule", "handle_scene", "chat_node", "request_clarification"]:
            builder.add_edge(node, "enhance_response")
        builder.add_edge("enhance_response", END)
        
        # Handle confirmation flow
        builder.add_conditional_edges(
            "request_confirmation",
            lambda state: {
                "confirmed": "handle_control",
                "cancelled": END,
                "unclear": "request_confirmation"
            }.get(state.get("next_action", "unclear"), "request_confirmation"),
            {
                "handle_control": "handle_control",
                "request_confirmation": "request_confirmation",
                END: END
            }
        )
        
        return builder.compile()
    
    def _detect_intent(self, state: GraphState) -> GraphState:
        """Detect intent from user message."""
        raw_messages = state["messages"]
        
        # Get devices
        devices_json = self.api_client.get_devices_per_space(
            Config.PROJECT_UUID, Config.COMMUNITY_UUID, Config.SPACE_UUID
        )
        
        if devices_json.get("statusCode") == 200:
            collected_devices = []
            for device_json in devices_json["data"]:
                collected_devices.append(Device(
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
        else:
            print(f"[WARN] Failed at fetching devices: {devices_json}")
            return {"messages": [AIMessage("Failed at Fetching Devices")] + state["messages"]}
        
        # Store devices
        namespace = ("devices", Config.USER_UUID)
        self.memory.get_base_store().put(namespace, Config.USER_UUID, collected_devices)
        
        # Normalize messages
        messages: List[BaseMessage] = []
        for m in raw_messages:
            if isinstance(m, BaseMessage):
                messages.append(m)
            elif isinstance(m, dict):
                if "role" in m and "content" in m:
                    role_to_type = {"user": "human", "assistant": "ai", "system": "system"}
                    message_type = role_to_type.get(m["role"], "human")
                    messages.extend(messages_from_dict([{
                        "type": message_type,
                        "data": {"content": m["content"]}
                    }]))
                elif "type" in m and "data" in m:
                    messages.extend(messages_from_dict([m]))
                else:
                    print(f"[WARN] Skipping unrecognized message format: {m}")
            else:
                print(f"[WARN] Invalid message object: {m}")
        
        # Find user message
        user_msg = next((msg.content for msg in reversed(messages) if msg.type == "human" and msg.content), None)
        if not user_msg:
            raise ValueError("No user message found")
        
        # Load intent prompt
        with open("prompts/intent_prompt.txt", "r") as f:
            intent_prompt = f.read()
        
        # Create full prompt
        prompt = f"""
{intent_prompt}

### USER INPUT:
"{user_msg}"

### AVAILABLE DEVICES:
{json.dumps([device.__dict__ for device in collected_devices], indent=2)}
"""
        
        llm_with_intent = self.llm.bind_tools([Intent], parallel_tool_calls=True)
        response = llm_with_intent.invoke([
            SystemMessage(content="You are an intent classifier"),
            HumanMessage(content=prompt)
        ])
        
        # Set ambiguous for None device_uuid
        for tool_call in response.tool_calls:
            if tool_call["args"]["device_uuid"] is None:
                tool_call["args"]["Intent"] = "ambiguous"
        
        return {**state, "messages": state["messages"] + [response]}
    
    def _route_message(self, state: GraphState) -> List[Literal["request_confirmation", "request_clarification", "handle_query", "handle_control", "handle_schedule", "handle_scene", "chat_node", END]]:
        """Route message based on detected intent."""
        message = state["messages"][-1]
        if len(message.tool_calls) == 0:
            return END
        
        next_nodes = set()
        for tool_call in message.tool_calls:
            intent = tool_call["args"]["Intent"]
            if intent == "ambiguous":
                next_nodes.add("request_clarification")
            elif intent == "control":
                next_nodes.add("handle_control")
            elif intent == "query":
                next_nodes.add("handle_query")
            elif intent == "schedule":
                next_nodes.add("handle_schedule")
            elif intent == "high_risk":
                next_nodes.add("request_confirmation")
            elif intent == "conversation":
                next_nodes.add("chat_node")
            elif intent == "scene":
                next_nodes.add("handle_scene")
            else:
                raise ValueError(f"Unknown intent: {intent}")
        
        return list(next_nodes)
    
    def _handle_query(self, state: GraphState) -> GraphState:
        """Handle device status queries."""
        message = state["messages"][-1]
        user_messages = []
        
        for tool_call in message.tool_calls:
            if tool_call["args"]["Intent"] == "query":
                device_uuid = tool_call["args"]["device_uuid"]
                user_messages.append({"device_uuid": device_uuid})
        
        query_responses = []
        for user_message in user_messages:
            status = self.api_client.get_status(user_message["device_uuid"])
            query_responses.append(status)
        
        return {**state, "messages": state["messages"] + [AIMessage(content=str(query_responses))]}
    
    def _handle_control(self, state: GraphState) -> GraphState:
        """Handle device control commands."""
        message = state["messages"][-1]
        devices = self.memory.get_base_store().search(("devices", Config.USER_UUID))
        
        user_messages = []
        descriptions = []
        control_responses = []
        
        for tool_call in message.tool_calls:
            device_uuid = tool_call["args"]["device_uuid"]
            user_message = tool_call["args"]["user_message"]
            
            if tool_call["args"]["Intent"] == "control":
                product_type = [device.product_type for device in devices[0].value if device.uuid == device_uuid]
                if product_type:
                    user_messages.append({
                        "device_uuid": device_uuid,
                        "product_type": product_type[0],
                        "user_message": user_message
                    })
                    
                    rows = self.device_descriptions[self.device_descriptions["product_type"] == product_type[0]]
                    for row in rows.values:
                        code, code_description, value, value_description, product_type = row
                        descriptions.append(f"""
                            "Product Type": {product_type},
                            "Code": {code},
                            "Code Description": {code_description},
                            "Value": {value},
                            "Value Description": {value_description}
                        """)
        
        llm_tool_functions = self.llm.bind_tools(tools=[DeviceFunction], parallel_tool_calls=True)
        
        system_prompt = f"""You are an IoT assistant. 
Your job is to take the human command and turn it into a structured object that should align with the possible value of the API.
If the user`s prompt does not align with the possible values then you should set them to None and the status to Failure.
Don't do the mistake of setting the value as a dictionary when the datatype is not dictionary, for example don't do this:
['value': 'True'] when the datatype is boolean, it should be only this ---> True

<user_messages>
{user_messages}
</user_messages>

This is an explanation for how to control product types:
<descriptions>
{descriptions}
</descriptions>

The following is the original prompt before being decomposed into user_messages:
<original_prompt>
{state["messages"][-1]}
</original_prompt>
"""
        
        response = llm_tool_functions.invoke([SystemMessage(content=system_prompt)])
        
        for tool_call in response.tool_calls:
            if tool_call["args"]["status"] == "Success":
                code = tool_call["args"]["code"]
                value = tool_call["args"]["value"]
                device_uuid = tool_call["args"]["device_uuid"]
                
                control_response = self.api_client.batch_control("COMMAND", [device_uuid], code, value)
                control_responses.append(f"Success for {device_uuid}: {control_response}")
            else:
                failure_reason = tool_call["args"].get("failure_reason", "Unknown failure")
                control_responses.append(f"Failed: {failure_reason}")
        
        if not control_responses:
            control_responses = ["No control actions were performed."]
        
        return {
            **state,
            "messages": state["messages"] + [
                AIMessage(content="Device control result(s): " + "\n".join(control_responses))
            ]
        }
    
    def _handle_scene(self, state: GraphState) -> GraphState:
        """Handle scene activation."""
        message = state["messages"][-1]
        
        user_message = ""
        for tool_call in message.tool_calls:
            if tool_call["args"]["Intent"] == "scene":
                user_message = tool_call["args"]["user_message"]
                break
        
        scenes = self.api_client.get_scenes(Config.PROJECT_UUID, Config.COMMUNITY_UUID, Config.SPACE_UUID)
        collected_scenes = []
        for scene in scenes.get("data", []):
            collected_scenes.append({
                "scene_name": scene["name"],
                "scene_uuid": scene["uuid"]
            })
        
        system_prompt = f"""
        You are an IoT assistant that determines that tries to search for scenes based on user prompt.
        If the scene is not available then just set the field uuid to None.
        
        User message: {user_message}
        Available scenes: {collected_scenes}
        """
        
        llm_with_scene = self.llm.bind_tools(tools=[Scene])
        llm_response = llm_with_scene.invoke([SystemMessage(content=system_prompt)])
        
        if llm_response.tool_calls and llm_response.tool_calls[0]["args"]["scene_uuid"]:
            scene_uuid = llm_response.tool_calls[0]["args"]["scene_uuid"]
            scene_name = llm_response.tool_calls[0]["args"]["scene_name"]
            
            response = self.api_client.trigger_scene(scene_uuid)
            return {
                "messages": state["messages"] + [AIMessage(content=f"{scene_name} Scene: " + str(response))]
            }
        else:
            return {
                "messages": state["messages"] + [AIMessage(content="Scene not found or could not be activated")]
            }
    
    def _handle_schedule(self, state: GraphState) -> GraphState:
        """Handle device scheduling."""
        message = state["messages"][-1]
        user_messages = []
        
        for tool_call in message.tool_calls:
            device_uuid = tool_call["args"]["device_uuid"]
            user_message = tool_call["args"]["user_message"]
            if tool_call["args"]["Intent"] == "schedule":
                user_messages.append({"device_uuid": device_uuid, "user_message": user_message})
        
        code_descriptions = {"control": "Commands: open, stop, close - controls the direction of the curtains"}
        descriptions = []
        llm_tool_functions = self.llm.bind_tools(tools=[DeviceSchedule], parallel_tool_calls=True)
        
        for user_message in user_messages:
            functions_json = self.api_client.get_device_functions(user_message["device_uuid"])
            if functions_json.get("statusCode") == 201:
                possible_values = functions_json["data"]["functions"]
                user_message["possible_values"] = possible_values
                for possible_value in possible_values:
                    if possible_value["code"] in code_descriptions.keys():
                        descriptions.append({possible_value["code"]: code_descriptions[possible_value["code"]]})
            else:
                print("[WARN] Failed at fetching functions")
                user_message["possible_values"] = None
        
        system_prompt = f"""You are an IoT assistant. 
Your job is to take the human command and turn it into a structured object that should align with the possible value of the API.
If the user`s prompt does not align with the possible values then you should set them to None and the status to Failure.
Don't do the mistake of setting the value as a dictionary when the datatype is not dictionary, for example don't do this:
['value': 'True'] when the datatype is boolean, it should be only this ---> True

The dictionary of devices with corresponding possible values are mentioned below:
<user_messages>
{user_messages}
</user_messages>

Each possible value correspond to a certain device ID. The device IDs are in the same order of the user`s prompt. 

The following is a description for the codes:
<descriptions>
{descriptions}
</descriptions>
"""
        
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
        
        return {**state, "messages": state["messages"] + [AIMessage(content=str(AI_messages))]}
    
    def _chat_node(self, state: GraphState) -> GraphState:
        """Handle general chat with tool-calling agent support."""
        messages = state["messages"]
        
        # Ensure all messages are LangChain messages
        lc_messages: List[BaseMessage] = []
        for m in messages:
            if isinstance(m, BaseMessage):
                lc_messages.append(m)
            elif isinstance(m, dict) and "role" in m:
                role_map = {"user": "human", "assistant": "ai", "system": "system", "tool": "tool", "tool_call": "tool_call"}
                lc_messages.extend(messages_from_dict([{
                    "type": role_map[m["role"]],
                    "data": {"content": m["content"]}
                }]))
        
        # Filter out incomplete tool call sequences from chat history
        filtered_messages = []
        i = 0
        while i < len(lc_messages):
            msg = lc_messages[i]
            
            # If this is an AI message with tool calls, check if it has responses
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_call_ids = {tc['id'] for tc in msg.tool_calls}
                
                # Look ahead for tool response messages
                j = i + 1
                found_responses = set()
                while j < len(lc_messages) and hasattr(lc_messages[j], 'tool_call_id'):
                    found_responses.add(lc_messages[j].tool_call_id)
                    j += 1
                
                # Only include if all tool calls have responses
                if tool_call_ids == found_responses:
                    filtered_messages.extend(lc_messages[i:j])
                    i = j
                else:
                    i += 1
            else:
                filtered_messages.append(msg)
                i += 1
        
        # Create agent executor
        agent = create_tool_calling_agent(
            llm=self.llm, 
            tools=self.tool_registry.get_all_tools(), 
            prompt=self.tool_registry.get_agent_prompt()
        )
        agent_executor = AgentExecutor(agent=agent, tools=self.tool_registry.get_all_tools(), verbose=True)
        
        # Run the agent with filtered history
        agent_output = agent_executor.invoke({
            "input": lc_messages[-1].content,
            "chat_history": filtered_messages
        })
        
        return {**state, "messages": state["messages"] + [AIMessage(content=agent_output["output"])]}
    
    def _request_clarification(self, state: GraphState) -> GraphState:
        """Request clarification for ambiguous commands."""
        message = state["messages"][-1]
        response_message = ""
        
        for tool_call in message.tool_calls:
            if tool_call["args"]["Intent"] == "ambiguous":
                reason = tool_call["args"]["reason"]
                user_message = tool_call["args"]["user_message"]
                response_message += "Failed to handle the following instruction: " + str(user_message) + "\n"
                response_message += "Reason: " + str(reason)
        
        clarification_prompt = (
            f"I'm having trouble understanding your request.\n"
            f"{response_message}\n"
            f"Could you please clarify what you meant?"
        )
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=clarification_prompt)]
        }
    
    def _request_confirmation(self, state: GraphState) -> GraphState:
        """Request confirmation for high-risk actions."""
        state["messages"] = state["messages"] + [
            AIMessage(content="⚠️ This is a high-risk action. Please reply 'confirm' or 'cancel'.")
        ]
        
        confirmation_response = interrupt({
            "question": "Do you want to confirm this high-risk action?",
            "messages": messages_to_dict(state["messages"]),
            "action_summary": state.get("action", "unknown action")
        })
        
        state["messages"] = state["messages"] + [HumanMessage(content=confirmation_response)]
        
        if confirmation_response.lower() in ["confirm", "yes", "approve"]:
            return {**state, "next_action": "confirmed"}
        elif confirmation_response.lower() in ["cancel", "no"]:
            return {**state, "next_action": "cancelled"}
        else:
            state["messages"] = state["messages"] + [
                AIMessage(content="Please reply with 'confirm' or 'cancel'.")
            ]
            return {**state, "next_action": "unclear"}
    
    def _enhance_response(self, state: GraphState) -> GraphState:
        """Enhance response with friendlier tone."""
        last = state["messages"][-1]
        if not isinstance(last, AIMessage):
            return state
        
        enhance_prompt = f"""
You are a friendly smart-home assistant.
Rewrite the following response in a concise, user-friendly way.
Do NOT invent actions or change their outcome. Keep all technical facts intact.

Response:
{last.content}
"""
        try:
            enhanced = self.llm.invoke([
                SystemMessage(content="You are a response enhancer that improves tone only."),
                HumanMessage(content=enhance_prompt)
            ])
            return {**state, "messages": state["messages"] + [AIMessage(content=enhanced.content)]}
        except Exception:
            return state
    
    def chat(self, message: str, history: list) -> str:
        """Main chat interface."""
        # Convert Gradio history into LangChain messages
        messages = []
        
        # Handle both tuple format (old) and dict format (new with type="messages")
        for item in history:
            if isinstance(item, dict):
                # New format: {"role": "user/assistant", "content": "message"}
                if item.get("role") == "user":
                    messages.append(HumanMessage(content=item.get("content", "")))
                elif item.get("role") == "assistant":
                    messages.append(AIMessage(content=item.get("content", "")))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                # Old format: (user_message, bot_message)
                user, bot = item
                if user:
                    messages.append(HumanMessage(content=user))
                if bot:
                    messages.append(AIMessage(content=bot))
            elif isinstance(item, str):
                # Single string message
                messages.append(HumanMessage(content=item))
        
        # Add the new user message
        messages.append(HumanMessage(content=message))
        
        # Create config with thread_id for conversation persistence
        config = {
            "configurable": {
                "thread_id": "default_thread",  # Use a default thread ID
                "base_store": self.memory.get_base_store(),
                "token": None,  # Will be set after login
                "user_uuid": Config.USER_UUID,
                "project_uuid": Config.PROJECT_UUID,
                "community_uuid": Config.COMMUNITY_UUID,
                "space_uuid": Config.SPACE_UUID,
            },
            "recursion_limit": Config.RECURSION_LIMIT
        }
        
        # Add LangSmith metadata if enabled
        if self.langsmith_enabled:
            config["metadata"] = {
                "run_name": create_run_name(message),
                "user_id": Config.USER_UUID,
                "project": Config.LANGSMITH_PROJECT,
                "conversation_type": "smart_home_assistant"
            }
        
        # Run through graph
        result = self.graph.invoke({"messages": messages}, config=config)
        
        # Get the assistant's reply
        reply = result["messages"][-1].content
        return reply
