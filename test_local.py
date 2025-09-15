#!/usr/bin/env python3
"""
Local testing script for the Smart Home Assistant.
Run this to test your setup before starting the full application.
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from agent import RagentChatbot
        print("✅ Agent module imported successfully")
    except ImportError as e:
        print(f"❌ Agent import failed: {e}")
        return False
    
    try:
        from domain.api_client import SyncrowAPIClient
        print("✅ API client imported successfully")
    except ImportError as e:
        print(f"❌ API client import failed: {e}")
        return False
    
    try:
        from llm import get_qwen_llm
        print("✅ LLM module imported successfully")
    except ImportError as e:
        print(f"❌ LLM import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration setup."""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        
        # Test required variables
        required_vars = [
            ('QWEN_API_KEY', Config.QWEN_API_KEY),
            ('TAVILY_API_KEY', Config.TAVILY_API_KEY),
            ('EMAIL', Config.EMAIL),
            ('PASSWORD', Config.PASSWORD),
        ]
        
        missing_vars = []
        for name, value in required_vars:
            if not value:
                missing_vars.append(name)
            else:
                print(f"✅ {name} is set")
        
        if missing_vars:
            print(f"❌ Missing required variables: {missing_vars}")
            print("   Please set these in your .env file")
            return False
        
        # Test optional variables
        optional_vars = [
            ('LANGSMITH_API_KEY', Config.LANGSMITH_API_KEY),
        ]
        
        for name, value in optional_vars:
            if value:
                print(f"✅ {name} is set (optional)")
            else:
                print(f"⚠️  {name} is not set (optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_llm_connection():
    """Test LLM connection."""
    print("\n🤖 Testing LLM connection...")
    
    try:
        from llm import get_qwen_llm
        
        llm = get_qwen_llm()
        print("✅ LLM instance created successfully")
        
        # Test a simple prompt
        response = llm.invoke("Hello, this is a test. Please respond with 'Test successful'.")
        print(f"✅ LLM response: {response.content[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def test_api_client():
    """Test API client connection."""
    print("\n🌐 Testing API client...")
    
    try:
        from domain.api_client import SyncrowAPIClient
        
        client = SyncrowAPIClient()
        print("✅ API client created successfully")
        
        # Test login (this will fail if credentials are wrong)
        from config import Config
        if Config.EMAIL and Config.PASSWORD:
            print("   Testing login...")
            token = client.login(Config.EMAIL, Config.PASSWORD)
            if token:
                print("✅ Login successful")
                return True
            else:
                print("❌ Login failed - check your credentials")
                return False
        else:
            print("⚠️  Skipping login test - no credentials provided")
            return True
            
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        return False

def test_chatbot_creation():
    """Test chatbot creation."""
    print("\n🏠 Testing chatbot creation...")
    
    try:
        from agent import RagentChatbot
        
        chatbot = RagentChatbot()
        print("✅ Chatbot created successfully")
        print(f"   LangSmith enabled: {chatbot.langsmith_enabled}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chatbot creation failed: {e}")
        return False

def test_simple_conversation():
    """Test a simple conversation."""
    print("\n💬 Testing simple conversation...")
    
    try:
        from agent import RagentChatbot
        
        chatbot = RagentChatbot()
        
        # Test a simple message
        response = chatbot.chat("Hello, this is a test message.", [])
        print(f"✅ Conversation test successful")
        print(f"   Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🏠 Smart Home Assistant - Local Testing")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Please create one with your API keys.")
        print("   See LOCAL_TESTING.md for details.")
        return
    
    tests = [
        test_imports,
        test_configuration,
        test_llm_connection,
        test_api_client,
        test_chatbot_creation,
        test_simple_conversation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! You're ready to run the application.")
        print("\n🚀 To start the application, run:")
        print('   "C:\\Program Files\\Odoo 18.0e.20241014\\python\\python.exe" app.py')
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("   See LOCAL_TESTING.md for troubleshooting help.")

if __name__ == "__main__":
    main()
