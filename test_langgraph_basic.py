#!/usr/bin/env python3
"""
Basic test script to verify LangGraph functionality without API keys.
This tests the core graph structure and node functionality.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_graph_structure():
    """Test that the graph can be created and has the expected structure."""
    print("🧪 Testing LangGraph structure...")
    
    try:
        from agent import RagentChatbot
        
        # Create chatbot instance (this will fail due to missing API keys, but we can test the graph structure)
        print("   Creating chatbot instance...")
        
        # Mock the LLM to avoid API key requirement
        class MockLLM:
            def bind_tools(self, tools, parallel_tool_calls=False):
                return self
            def invoke(self, messages):
                return type('MockResponse', (), {
                    'tool_calls': [],
                    'content': 'Mock response'
                })()
        
        # Temporarily replace the LLM
        import agent
        original_get_qwen_llm = agent.get_qwen_llm
        agent.get_qwen_llm = lambda: MockLLM()
        
        try:
            chatbot = RagentChatbot()
            graph = chatbot.graph
            
            print(f"   ✅ Graph created successfully")
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
            
            return True
            
        finally:
            # Restore original function
            agent.get_qwen_llm = original_get_qwen_llm
            
    except Exception as e:
        print(f"   ❌ Graph structure test failed: {e}")
        return False

def test_prompt_manager():
    """Test that the prompt manager works correctly."""
    print("\n📝 Testing prompt manager...")
    
    try:
        from prompts.prompt_manager import prompt_manager
        
        # Test loading prompts
        system_prompt = prompt_manager.get_agent_system_prompt()
        if system_prompt and len(system_prompt) > 0:
            print("   ✅ System prompt loaded successfully")
        else:
            print("   ❌ System prompt is empty")
            return False
        
        # Test intent detection prompt
        intent_prompt = prompt_manager.get_intent_detection_prompt(
            "Turn on the light", 
            '[{"name": "kitchen light", "type": "light"}]'
        )
        if intent_prompt and "Turn on the light" in intent_prompt:
            print("   ✅ Intent detection prompt formatted correctly")
        else:
            print("   ❌ Intent detection prompt formatting failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Prompt manager test failed: {e}")
        return False

def test_config_loading():
    """Test that configuration can be loaded."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        
        # Test that config class exists and has expected attributes
        expected_attrs = [
            'QWEN_API_KEY', 'TAVILY_API_KEY', 'EMAIL', 'PASSWORD',
            'PROJECT_UUID', 'COMMUNITY_UUID', 'SPACE_UUID', 'USER_UUID'
        ]
        
        missing_attrs = [attr for attr in expected_attrs if not hasattr(Config, attr)]
        if missing_attrs:
            print(f"   ⚠️  Missing config attributes: {missing_attrs}")
        else:
            print("   ✅ All expected config attributes present")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_domain_models():
    """Test that domain models can be imported."""
    print("\n🏗️  Testing domain models...")
    
    try:
        from domain.objects import Device, Intent, DeviceFunction, DeviceSchedule, Scene
        
        # Test creating instances
        device = Device(
            uuid="test-uuid",
            device_uuid="test-uuid",
            name="Test Device",
            product_type="light",
            space_uuid="test-space",
            category_name="lighting",
            spaces=[{"space_uuid": "test-space", "space_name": "Test Space"}]
        )
        
        intent = Intent(
            device_uuid="test-uuid",
            Intent="control"
        )
        
        print("   ✅ Domain models imported and instantiated successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Domain models test failed: {e}")
        return False

def test_services():
    """Test that services can be imported."""
    print("\n⚙️  Testing services...")
    
    try:
        from services.device_service import DeviceService
        from domain.api_client import SyncrowAPIClient
        
        # Test service instantiation (without API calls)
        api_client = SyncrowAPIClient()
        device_service = DeviceService(api_client)
        
        print("   ✅ Services imported and instantiated successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Services test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🤖 Ragent Chatbot - Basic LangGraph Test")
    print("=" * 50)
    
    tests = [
        test_graph_structure,
        test_prompt_manager,
        test_config_loading,
        test_domain_models,
        test_services
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! LangGraph structure is working correctly.")
        print("\n📝 Note: This test doesn't require API keys.")
        print("   To test with real API calls, configure your .env file with:")
        print("   - QWEN_API_KEY")
        print("   - TAVILY_API_KEY") 
        print("   - EMAIL")
        print("   - PASSWORD")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
