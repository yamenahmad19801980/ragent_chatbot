"""
Main agent implementation using LangGraph.
Handles intent detection, routing, and execution of various commands.
"""

import json
import time
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
from services import DeviceService
from prompts.prompt_manager import prompt_manager
from utils.normalizer import MessageNormalizer
from utils.logger import get_logger, log_intent_detection, log_conversation_turn, log_performance

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
        self.device_service = DeviceService(self.api_client)
        self.normalizer = MessageNormalizer()
        self.logger = get_logger(__name__)
        
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
        for node in ["handle_control", "handle_query", "handle_schedule", "handle_scene",  "request_clarification"]:
            builder.add_edge(node, "enhance_response")
                
        builder.add_edge("chat_node", END)
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
        """Detect intent from user message using centralized services."""
        raw_messages = state["messages"]
        
        # Get devices using centralized service
        collected_devices = self.device_service.get_devices_in_space(
            Config.PROJECT_UUID, Config.COMMUNITY_UUID, Config.SPACE_UUID
        )
        
        if not collected_devices:
            return {"messages": [AIMessage("Failed at Fetching Devices")] + state["messages"]}
        
        # Store devices
        namespace = ("devices", Config.USER_UUID)
        self.memory.get_base_store().put(namespace, Config.USER_UUID, collected_devices)
        
        # Normalize messages using centralized utility
        messages = MessageNormalizer.normalize_messages(raw_messages)
        
        # Find user message using centralized utility
        user_msg = MessageNormalizer.find_user_message(messages)
        if not user_msg:
            raise ValueError("No user message found")
        
        # Create prompt using centralized template
        devices_json = [device.__dict__ for device in collected_devices]
        prompt = prompt_manager.get_intent_detection_prompt(user_msg, str(devices_json))
        
        llm_with_intent = self.llm.bind_tools([Intent], parallel_tool_calls=True)
        response = llm_with_intent.invoke([
            SystemMessage(content="You are an intent classifier"),
            HumanMessage(content=prompt)
        ])
        
        # Set ambiguous for None device_uuid
        for tool_call in response.tool_calls:
            if tool_call["args"].get("device_uuid") is None:
                tool_call["args"]["Intent"] = "ambiguous"
        
        return {**state, "messages": state["messages"] + [response]}
    
    def _route_message(self, state: GraphState) -> List[Literal["request_confirmation", "request_clarification", "handle_query", "handle_control", "handle_schedule", "handle_scene", "chat_node", END]]:
        """Route message based on detected intent."""
        message = state["messages"][-1]
        if len(message.tool_calls) == 0:
            return END
        
        next_nodes = set()
        for tool_call in message.tool_calls:
            intent = tool_call["args"].get("Intent", "conversation")  # Default to conversation
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
                # Default to conversation for unknown intents
                next_nodes.add("chat_node")
        
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
        """Handle device control commands using centralized service."""
        start_time = time.time()
        message = state["messages"][-1]
        devices = self.memory.get_base_store().search(("devices", Config.USER_UUID))
        
        user_messages = []
        
        for tool_call in message.tool_calls:
            device_uuid = tool_call["args"].get("device_uuid")
            user_message = tool_call["args"].get("user_message", "")
            
            if tool_call["args"].get("Intent") == "control" and device_uuid:
                product_type = [device.product_type for device in devices[0].value if device.uuid == device_uuid]
                if product_type:
                    user_messages.append({
                        "device_uuid": device_uuid,
                        "product_type": product_type[0],
                        "user_message": user_message
                    })
        
        # Use centralized device service for control operations
        control_responses = self.device_service.control_multiple_devices(user_messages, devices[0].value)
        
        duration = time.time() - start_time
        log_performance(self.logger, "handle_control", duration, {"device_count": len(user_messages)})
        
        return {
            **state,
            "messages": state["messages"] + [
                AIMessage(content="Device control result(s): " + "\n".join(control_responses))
            ]
        }    
    def _handle_scene(self, state: GraphState) -> GraphState:
        """Handle scene activation using centralized service."""
        message = state["messages"][-1]
        
        user_message = ""
        for tool_call in message.tool_calls:
            if tool_call["args"]["Intent"] == "scene":
                user_message = tool_call["args"]["user_message"]
                break
        
        # Get scenes using centralized service
        collected_scenes = self.device_service.get_scenes(Config.PROJECT_UUID, Config.COMMUNITY_UUID, Config.SPACE_UUID)
        
        # Use centralized service for scene activation
        result = self.device_service.trigger_scene_by_name(user_message, collected_scenes)
        
        if result["success"]:
            return {
                "messages": state["messages"] + [AIMessage(content=f"{result['scene_name']} Scene: " + str(result["response"]))]
            }
        else:
            return {
                "messages": state["messages"] + [AIMessage(content="Scene not found or could not be activated")]
            }
    
    def _handle_schedule(self, state: GraphState) -> GraphState:
        """Handle device scheduling using centralized service."""
        message = state["messages"][-1]
        user_messages = []
        
        for tool_call in message.tool_calls:
            device_uuid = tool_call["args"]["device_uuid"]
            user_message = tool_call["args"]["user_message"]
            if tool_call["args"]["Intent"] == "schedule":
                user_messages.append({"device_uuid": device_uuid, "user_message": user_message})
        
        # Use centralized service for device scheduling
        AI_messages = self.device_service.schedule_multiple_devices(user_messages)
        
        return {**state, "messages": state["messages"] + [AIMessage(content=str(AI_messages))]}
    
    def _chat_node(self, state: GraphState) -> GraphState:
        """Handle general chat with tool-calling agent support using centralized utilities."""
        messages = state["messages"]
        
        # Normalize messages using centralized utility
        lc_messages = MessageNormalizer.normalize_messages(messages)
        
        # Filter out incomplete tool call sequences using centralized utility
        filtered_messages = MessageNormalizer.filter_tool_call_messages(lc_messages)
        
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
        """Request clarification for ambiguous commands using centralized templates."""
        message = state["messages"][-1]
        response_message = ""
        
        for tool_call in message.tool_calls:
            if tool_call["args"]["Intent"] == "ambiguous":
                reason = tool_call["args"]["reason"]
                user_message = tool_call["args"]["user_message"]
                response_message += "Failed to handle the following instruction: " + str(user_message) + "\n"
                response_message += "Reason: " + str(reason)
        
        # Use centralized template for clarification
        clarification_prompt = prompt_manager.get_clarification_request_prompt(response_message, "")
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=clarification_prompt)]
        }
    
    def _request_confirmation(self, state: GraphState) -> GraphState:
        """Request confirmation for high-risk actions using centralized templates."""
        confirmation_message = prompt_manager.get_confirmation_request_prompt("high-risk action", "high")
        state["messages"] = state["messages"] + [AIMessage(content=confirmation_message)]
        
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
        """Enhance response with friendlier tone using centralized templates."""
        last = state["messages"][-1]
        if not isinstance(last, AIMessage):
            return state
        
        # Use centralized template for response enhancement
        enhance_prompt = prompt_manager.get_response_enhancement_prompt(last.content)
        
        try:
            enhanced = self.llm.invoke([
                SystemMessage(content="You are a response enhancer that improves tone only."),
                HumanMessage(content=enhance_prompt)
            ])
            # Create a new state with the enhanced message replacing the last one
            new_messages = list(state["messages"][:-1]) + [AIMessage(content=enhanced.content)]
            return {"messages": new_messages}
        except Exception:
            return state
    
    def chat(self, message: str, history: list) -> str:
        """Main chat interface using centralized message normalization."""
        # Convert Gradio history into LangChain messages using centralized utility
        messages = MessageNormalizer.normalize_gradio_history(history)
        
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

# Export function for LangGraph Studio
def get_compiled_graph():
    """Export function for LangGraph Studio to access the compiled graph."""
    chatbot = RagentChatbot()
    return chatbot.graph

# For direct execution
if __name__ == "__main__":
    # This allows the graph to be imported by LangGraph Studio
    graph = get_compiled_graph()
    print("Graph compiled successfully for LangGraph Studio")
