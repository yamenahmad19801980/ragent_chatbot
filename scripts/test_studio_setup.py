#!/usr/bin/env python3
"""
Test script to verify LangGraph Studio setup is working correctly.
This script tests all components needed for LangGraph Studio.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from agent import get_compiled_graph
        from config import Config
        from domain.api_client import SyncrowAPIClient
        from services.device_service import DeviceService
        from prompts.prompt_manager import prompt_manager
        print("✅ Core imports successful")
        
        # Test LangGraph Studio import
        import langgraph_studio
        print("✅ LangGraph Studio import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        
        # Test required variables
        required_vars = ['QWEN_API_KEY', 'TAVILY_API_KEY', 'EMAIL', 'PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(Config, var, None):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_graph_compilation():
    """Test that the graph can be compiled."""
    print("\n📊 Testing graph compilation...")
    
    try:
        from agent import get_compiled_graph
        graph = get_compiled_graph()
        
        # Test graph properties
        if hasattr(graph, 'nodes') and hasattr(graph, 'edges'):
            print("✅ Graph compiled successfully")
            print(f"   Nodes: {len(graph.nodes)}")
            print(f"   Edges: {len(graph.edges)}")
            return True
        else:
            print("❌ Graph structure invalid")
            return False
    except Exception as e:
        print(f"❌ Graph compilation error: {e}")
        return False

def test_prompt_manager():
    """Test prompt manager functionality."""
    print("\n📝 Testing prompt manager...")
    
    try:
        from prompts.prompt_manager import prompt_manager
        
        # Test a simple prompt
        test_prompt = prompt_manager.get_agent_system_prompt()
        if test_prompt and len(test_prompt) > 0:
            print("✅ Prompt manager working")
            return True
        else:
            print("❌ Prompt manager returned empty prompt")
            return False
    except Exception as e:
        print(f"❌ Prompt manager error: {e}")
        return False

def test_studio_config():
    """Test LangGraph Studio configuration file."""
    print("\n🎯 Testing LangGraph Studio configuration...")
    
    try:
        import json
        studio_config_path = Path(__file__).parent.parent / "studio" / "langgraph.json"
        
        if not studio_config_path.exists():
            print("❌ langgraph.json not found")
            return False
        
        with open(studio_config_path, 'r') as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = ['dependencies', 'graphs', 'env', 'working_directory']
        for field in required_fields:
            if field not in config:
                print(f"❌ Missing field in config: {field}")
                return False
        
        print("✅ LangGraph Studio configuration valid")
        return True
    except Exception as e:
        print(f"❌ Studio config error: {e}")
        return False

def test_api_client():
    """Test API client initialization."""
    print("\n🌐 Testing API client...")
    
    try:
        from domain.api_client import SyncrowAPIClient
        client = SyncrowAPIClient()
        
        # Test that client can be created
        if client and hasattr(client, 'base_url'):
            print("✅ API client initialized")
            return True
        else:
            print("❌ API client initialization failed")
            return False
    except Exception as e:
        print(f"❌ API client error: {e}")
        return False

def main():
    """Run all tests."""
    print("🤖 Ragent Chatbot - LangGraph Studio Setup Test")
    print("=" * 50)
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    tests = [
        test_imports,
        test_config,
        test_graph_compilation,
        test_prompt_manager,
        test_studio_config,
        test_api_client
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
        print("🎉 All tests passed! LangGraph Studio setup is ready.")
        print("\n🚀 To start LangGraph Studio, run:")
        print("   python scripts/start_studio.py")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Configure .env file with required variables")
        print("   3. Check Python version (3.8+ required)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
