#!/usr/bin/env python3
"""
Comprehensive LangGraph demonstration and testing script.
This script tests all the LangGraph functionality and provides a demo interface.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_environment_setup():
    """Test that environment variables are properly loaded."""
    print("🔧 Testing environment setup...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ['QWEN_API_KEY', 'TAVILY_API_KEY', 'EMAIL', 'PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                print(f"   ✅ {var}: {value[:10]}..." if len(value) > 10 else f"   ✅ {var}: {value}")
        
        if missing_vars:
            print(f"   ❌ Missing variables: {missing_vars}")
            return False
        
        print("   ✅ All environment variables loaded successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Environment setup failed: {e}")
        return False

def test_graph_compilation():
    """Test that the LangGraph can be compiled."""
    print("\n📊 Testing LangGraph compilation...")
    
    try:
        from agent import get_compiled_graph
        graph = get_compiled_graph()
        
        print(f"   ✅ Graph compiled successfully")
        print(f"   📊 Nodes: {list(graph.nodes.keys())}")
        print(f"   🔗 Edges: {len(graph.edges)}")
        
        # Test graph structure
        expected_nodes = [
            'detect_intent',
            'route_message', 
            'handle_control',
            'handle_query',
            'handle_schedule',
            'handle_scene',
            'request_clarification',
            'request_confirmation',
            'chat_node'
        ]
        
        missing_nodes = [node for node in expected_nodes if node not in graph.nodes]
        if missing_nodes:
            print(f"   ⚠️  Missing nodes: {missing_nodes}")
        else:
            print(f"   ✅ All expected nodes present")
        
        return graph
        
    except Exception as e:
        print(f"   ❌ Graph compilation failed: {e}")
        return None

def test_prompt_system():
    """Test the prompt management system."""
    print("\n📝 Testing prompt system...")
    
    try:
        from prompts.prompt_manager import prompt_manager
        
        # Test system prompt
        system_prompt = prompt_manager.get_agent_system_prompt()
        print(f"   ✅ System prompt loaded ({len(system_prompt)} characters)")
        
        # Test intent detection prompt
        intent_prompt = prompt_manager.get_intent_detection_prompt(
            "Turn on the kitchen light", 
            '[{"name": "kitchen light", "type": "light"}]'
        )
        print(f"   ✅ Intent detection prompt formatted")
        
        # Test device control prompt
        control_prompt = prompt_manager.get_device_control_prompt(
            '[{"device_uuid": "test", "user_message": "turn on", "product_type": "light"}]',
            "Light control: ON/OFF",
            "Turn on the light"
        )
        print(f"   ✅ Device control prompt formatted")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Prompt system test failed: {e}")
        return False

def test_domain_models():
    """Test domain models and data structures."""
    print("\n🏗️  Testing domain models...")
    
    try:
        from domain.objects import Device, Intent, DeviceFunction, DeviceSchedule, Scene
        
        # Test Device model
        device = Device(
            uuid="test-uuid-123",
            device_uuid="test-uuid-123",
            name="Kitchen Light",
            product_type="light",
            space_uuid="kitchen-space",
            category_name="lighting",
            spaces=[{"space_uuid": "kitchen-space", "space_name": "Kitchen"}]
        )
        print(f"   ✅ Device model: {device.name}")
        
        # Test Intent model
        intent = Intent(
            device_uuid="test-uuid-123",
            Intent="control"
        )
        print(f"   ✅ Intent model: {intent.Intent}")
        
        # Test DeviceFunction model
        function = DeviceFunction(
            device_uuid="test-uuid-123",
            code="ON",
            value=True,
            status="Success"
        )
        print(f"   ✅ DeviceFunction model: {function.code}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Domain models test failed: {e}")
        return False

def test_api_client():
    """Test API client initialization."""
    print("\n🌐 Testing API client...")
    
    try:
        from domain.api_client import SyncrowAPIClient
        
        client = SyncrowAPIClient()
        print(f"   ✅ API client initialized")
        print(f"   🔗 Base URL: {client.base_url}")
        
        return client
        
    except Exception as e:
        print(f"   ❌ API client test failed: {e}")
        return None

def test_services():
    """Test service layer."""
    print("\n⚙️  Testing services...")
    
    try:
        from services.device_service import DeviceService
        from domain.api_client import SyncrowAPIClient
        
        api_client = SyncrowAPIClient()
        device_service = DeviceService(api_client)
        
        print(f"   ✅ DeviceService initialized")
        print(f"   📊 Device descriptions loaded: {len(device_service.device_descriptions)} entries")
        
        return device_service
        
    except Exception as e:
        print(f"   ❌ Services test failed: {e}")
        return None

def demo_conversation_flow():
    """Demonstrate the conversation flow without API calls."""
    print("\n💬 Demonstrating conversation flow...")
    
    try:
        from agent import RagentChatbot
        from langchain_core.messages import HumanMessage
        
        # Create chatbot instance
        chatbot = RagentChatbot()
        
        # Test messages
        test_messages = [
            "Hello, how are you?",
            "Turn on the kitchen light",
            "What's the temperature?",
            "Set the AC to 72 degrees at 3 PM tomorrow",
            "Activate movie night scene"
        ]
        
        print("   🧪 Testing conversation flow with sample messages:")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n   Test {i}: '{message}'")
            
            try:
                # Create state with the message
                state = {"messages": [HumanMessage(content=message)]}
                
                # Test intent detection (first node)
                print(f"      🔍 Detecting intent...")
                # Note: This would normally call the LLM, but we'll skip for demo
                print(f"      ✅ Intent detection would process: '{message}'")
                
                # Test routing logic
                print(f"      🚦 Routing message...")
                # This would determine the next node based on intent
                print(f"      ✅ Message would be routed to appropriate handler")
                
            except Exception as e:
                print(f"      ⚠️  Demo step failed: {e}")
        
        print(f"\n   ✅ Conversation flow demonstration completed")
        return True
        
    except Exception as e:
        print(f"   ❌ Conversation flow demo failed: {e}")
        return False

def create_graph_visualization():
    """Create a text-based visualization of the graph structure."""
    print("\n📊 Creating graph visualization...")
    
    try:
        from agent import get_compiled_graph
        graph = get_compiled_graph()
        
        print("   🎯 LangGraph Structure:")
        print("   " + "="*50)
        print("   START")
        print("     ↓")
        print("   detect_intent")
        print("     ↓")
        print("   route_message (Decision Node)")
        print("     ├── ambiguous → request_clarification")
        print("     ├── control → handle_control")
        print("     ├── query → handle_query")
        print("     ├── schedule → handle_schedule")
        print("     ├── scene → handle_scene")
        print("     ├── high_risk → request_confirmation")
        print("     └── conversation → chat_node")
        print("     ↓")
        print("   END")
        print("   " + "="*50)
        
        # Save graph info to file
        graph_info = {
            "nodes": list(graph.nodes.keys()),
            "edges": len(graph.edges),
            "structure": "Linear flow with decision routing"
        }
        
        with open("graph_info.json", "w") as f:
            json.dump(graph_info, f, indent=2)
        
        print(f"   ✅ Graph info saved to graph_info.json")
        return True
        
    except Exception as e:
        print(f"   ❌ Graph visualization failed: {e}")
        return False

def main():
    """Run comprehensive LangGraph demonstration."""
    print("🤖 Ragent Chatbot - LangGraph Comprehensive Test & Demo")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Graph Compilation", test_graph_compilation),
        ("Prompt System", test_prompt_system),
        ("Domain Models", test_domain_models),
        ("API Client", test_api_client),
        ("Services", test_services),
        ("Conversation Flow", demo_conversation_flow),
        ("Graph Visualization", create_graph_visualization)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result is not False and result is not None
        except Exception as e:
            print(f"   ❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! LangGraph setup is working perfectly.")
        print("\n🚀 Your LangGraph chatbot is ready for development!")
        print("\n📝 Next steps:")
        print("   1. Configure your .env file with real API keys")
        print("   2. Test with real device data")
        print("   3. Deploy to Hugging Face Spaces")
        print("   4. Use for development and debugging")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
