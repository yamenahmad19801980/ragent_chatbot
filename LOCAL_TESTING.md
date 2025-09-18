# 🏠 Local Testing Guide - Smart Home Assistant

This guide shows you how to run and test your Smart Home Assistant locally on your development machine.

## 📋 **Prerequisites**

### **1. Python Environment**
- Python 3.11+ (you have 3.12.3 in your Odoo installation)
- pip package manager

### **2. Required API Keys**
- Qwen API key
- Tavily API key  
- Syncrow API credentials (email/password)
- LangSmith API key (optional, for debugging)

## 🚀 **Quick Start**

### **1. Navigate to Project Directory**
```bash
cd ragent_chatbot
```

### **2. Install Dependencies**
```bash
# Using your Odoo Python
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -m pip install -r requirements.txt
```

### **3. Create Environment File**
Create a `.env` file in the project root:
```env
# API Keys
QWEN_API_KEY=your_qwen_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Syncrow API Credentials
EMAIL=your_syncrow_email_here
PASSWORD=your_syncrow_password_here

# LangSmith (Optional)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=ragent-chatbot-local

# Database (Optional)
SQL_DATABASE=your_database_name
SQL_USER=your_db_user
SQL_HOST=your_db_host
SQL_PASSWORD=your_db_password
SQL_PORT=5432
```

### **4. Run the Application**
```bash
# Using your Odoo Python
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" app.py
```

### **5. Access the Interface**
- Open your browser
- Go to `http://localhost:7860`
- Start chatting with your Smart Home Assistant!

## 🧪 **Testing Scenarios**

### **1. Basic Conversation Test**
```
User: "Hello, how are you?"
Expected: Friendly response with smart home capabilities
```

### **2. Device Control Test**
```
User: "Turn on the living room lights"
Expected: Intent detection → device control → confirmation
```

### **3. Device Query Test**
```
User: "What's the status of the kitchen switch?"
Expected: Intent detection → device query → status response
```

### **4. Scheduling Test**
```
User: "Schedule the AC to turn on at 8 AM tomorrow"
Expected: Intent detection → schedule creation → confirmation
```

### **5. Scene Activation Test**
```
User: "Activate movie night scene"
Expected: Intent detection → scene lookup → scene activation
```

### **6. Web Search Test**
```
User: "What's the weather like today?"
Expected: Intent detection → web search → weather response
```

## 🔧 **Development Tools**

### **1. Debug Mode**
Add debug logging to see detailed execution:
```python
# In agent.py, add at the top
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **2. Test Individual Components**
```bash
# Test LangSmith setup
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "
from llm.langsmith_config import setup_langsmith
print('LangSmith enabled:', setup_langsmith())
"

# Test API client
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "
from domain.api_client import SyncrowAPIClient
client = SyncrowAPIClient()
token = client.login('your_email', 'your_password')
print('Login successful:', token is not None)
"

# Test graph visualization
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" utils/graph_visualizer.py
```

### **3. Unit Testing**
Create test files for individual components:
```bash
# Create test directory
mkdir tests

# Test intent detection
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "
from agent import RagentChatbot
chatbot = RagentChatbot()
result = chatbot.chat('Turn on the lights', [])
print('Test result:', result)
"
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **1. Import Errors**
```bash
# Make sure you're in the project directory
cd ragent_chatbot

# Check Python path
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "import sys; print(sys.path)"
```

#### **2. Missing Dependencies**
```bash
# Install missing packages
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -m pip install --upgrade pip
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -m pip install -r requirements.txt
```

#### **3. API Connection Issues**
- Check your API keys in `.env`
- Verify network connectivity
- Test API endpoints individually

#### **4. Gradio Issues**
```bash
# Update Gradio
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -m pip install --upgrade gradio

# Check Gradio version
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "import gradio; print(gradio.__version__)"
```

### **Debug Commands**

#### **1. Check Configuration**
```bash
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "
from config import Config
print('Config validation:', Config.validate())
print('Qwen API key set:', bool(Config.QWEN_API_KEY))
print('Tavily API key set:', bool(Config.TAVILY_API_KEY))
"
```

#### **2. Test LangGraph**
```bash
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "
from agent import RagentChatbot
chatbot = RagentChatbot()
print('Graph created successfully')
print('LangSmith enabled:', chatbot.langsmith_enabled)
"
```

#### **3. Test API Client**
```bash
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "
from domain.api_client import SyncrowAPIClient
client = SyncrowAPIClient()
print('API client created successfully')
"
```

## 📊 **Performance Testing**

### **1. Load Testing**
```bash
# Test multiple conversations
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "
import time
from agent import RagentChatbot

chatbot = RagentChatbot()
start_time = time.time()

# Test 10 conversations
for i in range(10):
    result = chatbot.chat(f'Test message {i}', [])
    print(f'Message {i}: {len(result)} characters')

end_time = time.time()
print(f'Total time: {end_time - start_time:.2f} seconds')
print(f'Average time per message: {(end_time - start_time)/10:.2f} seconds')
"
```

### **2. Memory Usage**
```bash
# Monitor memory usage
"C:\Program Files\Odoo 18.0e.20241014\python\python.exe" -c "
import psutil
import os

process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

## 🔍 **Debugging with LangSmith**

### **1. Enable LangSmith**
- Add `LANGSMITH_API_KEY` to your `.env` file
- Restart the application
- Check LangSmith dashboard for traces

### **2. View Traces**
1. Go to [https://smith.langchain.com](https://smith.langchain.com)
2. Navigate to your project
3. View real-time traces as you test

### **3. Debug Specific Issues**
- Look for error nodes in traces
- Check input/output data for each node
- Monitor performance metrics

## 📝 **Testing Checklist**

### **Before Testing**
- [ ] Environment variables set correctly
- [ ] All dependencies installed
- [ ] API keys valid and working
- [ ] Network connectivity confirmed

### **During Testing**
- [ ] Basic conversation works
- [ ] Device control functions
- [ ] Error handling works
- [ ] Performance is acceptable
- [ ] LangSmith tracking works (if enabled)

### **After Testing**
- [ ] All test scenarios pass
- [ ] No critical errors
- [ ] Performance meets requirements
- [ ] Documentation updated

## 🚀 **Production Deployment**

### **1. Environment Setup**
- Use production API keys
- Set up proper logging
- Configure monitoring

### **2. Performance Optimization**
- Enable caching where appropriate
- Optimize API calls
- Monitor resource usage

### **3. Security**
- Secure API key storage
- Implement rate limiting
- Add input validation

## 📞 **Support**

If you encounter issues:
1. Check the troubleshooting section
2. Review error logs
3. Test individual components
4. Check LangSmith traces (if enabled)
5. Review the GitHub repository issues

Happy testing! 🎉
