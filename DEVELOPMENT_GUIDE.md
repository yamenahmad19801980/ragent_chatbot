# 🚀 Ragent Chatbot Development Guide

This guide provides comprehensive instructions for developers working on the Ragent Chatbot project, including LangGraph Studio setup, debugging, and testing.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Development Environment](#-development-environment)
- [LangGraph Studio Setup](#-langgraph-studio-setup)
- [Testing & Debugging](#-testing--debugging)
- [Code Structure](#-code-structure)
- [Common Tasks](#-common-tasks)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- Code editor (VS Code recommended)

### 1. Clone and Setup
```bash
git clone https://github.com/yamenahmad19801980/ragent_chatbot.git
cd ragent_chatbot
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Required variables:
# QWEN_API_KEY=your_qwen_api_key
# TAVILY_API_KEY=your_tavily_api_key
# EMAIL=your_syncrow_email
# PASSWORD=your_syncrow_password
```

### 3. Start Development
```bash
# Option 1: Start LangGraph Studio (Recommended for development)
python scripts/start_studio.py

# Option 2: Start Gradio app
python app.py

# Option 3: Test locally
python test_local.py
```

## 🛠️ Development Environment

### Recommended VS Code Extensions
- Python
- LangGraph
- GitLens
- Thunder Client (for API testing)
- Markdown All in One

### Project Structure
```
ragent_chatbot/
├── 📁 studio/              # LangGraph Studio configuration
├── 📁 scripts/             # Development scripts
├── 📁 prompts/             # MD prompt templates
├── 📁 services/            # Business logic
├── 📁 domain/              # Data models and API clients
├── 📁 llm/                 # LLM configuration
├── 📁 tools/               # Tool implementations
├── 📁 utils/               # Utility functions
├── 📄 agent.py             # Main LangGraph agent
├── 📄 app.py               # Gradio interface
└── 📄 config.py            # Configuration management
```

## 🎯 LangGraph Studio Setup

LangGraph Studio is the primary development tool for this project. It provides:
- **Graph Visualization**: See the conversation flow
- **Debugging**: Step through each node
- **Testing**: Send test messages
- **State Inspection**: View conversation state

### Installation
```bash
# Install LangGraph Studio
pip install langgraph-studio

# Or use our script
python scripts/start_studio.py --install-deps
```

### Starting LangGraph Studio

#### Windows
```bash
# Batch file
scripts\start_studio.bat

# PowerShell
scripts\start_studio.ps1

# Python script
python scripts/start_studio.py
```

#### Linux/Mac
```bash
# Python script
python scripts/start_studio.py

# Direct command
langgraph-studio --config studio/langgraph.json
```

### Accessing the Studio
1. Open browser to: http://localhost:8123
2. You'll see the graph visualization
3. Use the chat interface to test messages
4. Inspect state and debug issues

## 🧪 Testing & Debugging

### Graph Testing Workflow

#### 1. Basic Functionality Test
```python
# Test message: "Turn on the kitchen light"
# Expected flow:
# detect_intent → route_message → handle_control → END
```

#### 2. Error Handling Test
```python
# Test message: "Turn on the TV"
# Expected flow:
# detect_intent → route_message → request_clarification → END
```

#### 3. Complex Scenario Test
```python
# Test message: "Turn on the kitchen light and set temperature to 72"
# Expected flow:
# detect_intent → route_message → handle_control (multiple devices) → END
```

### Debugging Techniques

#### 1. State Inspection
- Click on any node to see its input/output
- Check conversation state between nodes
- Verify tool call arguments

#### 2. Step-by-Step Execution
- Use the "Step" button to execute one node at a time
- Monitor state changes between steps
- Identify where issues occur

#### 3. Error Analysis
- Check error messages in the console
- Inspect failed tool calls
- Verify API responses

### Common Test Cases

#### Intent Detection Tests
```python
# Control intent
"Turn on the kitchen light" → control

# Query intent  
"What's the temperature?" → query

# Schedule intent
"Turn on AC at 3 PM tomorrow" → schedule

# Scene intent
"Activate movie night" → scene

# Ambiguous intent
"Turn on the TV" → ambiguous (if no TV device)

# Conversation intent
"Tell me a joke" → conversation
```

#### Device Control Tests
```python
# Light control
"Turn on kitchen light" → Light ON

# Temperature control
"Set temperature to 72" → Thermostat 72°F

# Multiple devices
"Turn on all lights" → Multiple lights ON
```

## 🏗️ Code Structure

### Key Components

#### 1. Agent (`agent.py`)
- **Main LangGraph implementation**
- **State management**: `GraphState` with messages
- **Node functions**: `_detect_intent`, `_route_message`, etc.
- **Graph construction**: `_build_graph()`

#### 2. Services (`services/`)
- **DeviceService**: Device control logic
- **AsyncDeviceService**: Async version for performance

#### 3. Domain (`domain/`)
- **Objects**: Pydantic models (Device, Intent, etc.)
- **API Client**: Syncrow API integration

#### 4. Prompts (`prompts/`)
- **MD Templates**: All prompts in Markdown format
- **Prompt Manager**: Loads and formats templates

#### 5. Tools (`tools/`)
- **Web Search**: Internet search capability
- **Base Tool**: Common tool functionality

### Adding New Features

#### 1. New Intent Type
```python
# 1. Add to Intent model in domain/objects.py
class Intent(BaseModel):
    # ... existing intents
    new_intent: str = "new_intent"

# 2. Add routing in agent.py
def _route_message(self, state: GraphState):
    # ... existing routing
    elif intent == "new_intent":
        next_nodes.add("handle_new_intent")

# 3. Add handler node
def _handle_new_intent(self, state: GraphState) -> GraphState:
    # Implementation here
    pass

# 4. Add to graph
graph.add_node("handle_new_intent", self._handle_new_intent)
```

#### 2. New Tool
```python
# 1. Create tool in tools/
class NewTool(BaseTool):
    def execute(self, **kwargs):
        # Implementation here
        pass

# 2. Register in tool_registry.py
def register_new_tool(self):
    self.tools.append(NewTool())
```

## 🔧 Common Tasks

### 1. Adding New Device Types
```python
# 1. Update device mappings in data/device_mappings.csv
# 2. Add device descriptions in DeviceService.get_device_descriptions()
# 3. Test with LangGraph Studio
```

### 2. Modifying Prompts
```python
# 1. Edit MD files in prompts/
# 2. Test with LangGraph Studio
# 3. Verify prompt formatting in prompt_manager.py
```

### 3. Debugging API Issues
```python
# 1. Check API client logs
# 2. Verify credentials in .env
# 3. Test API calls directly
# 4. Check network connectivity
```

### 4. Performance Optimization
```python
# 1. Use caching for device lists
# 2. Implement async operations
# 3. Monitor execution time
# 4. Optimize prompt length
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Ensure you're in the project root
cd /path/to/ragent_chatbot
python scripts/start_studio.py
```

#### 2. Environment Variables
```bash
# Check .env file
cat .env

# Verify required variables are set
python -c "from config import Config; print(Config.validate())"
```

#### 3. Graph Compilation Errors
```bash
# Test compilation
python -c "from agent import get_compiled_graph; print('OK')"

# Check for syntax errors
python -m py_compile agent.py
```

#### 4. API Connection Issues
```bash
# Test API connection
python -c "from domain.api_client import SyncrowAPIClient; client = SyncrowAPIClient(); print(client.login('email', 'password'))"
```

#### 5. LangGraph Studio Won't Start
```bash
# Check port availability
netstat -an | findstr :8123

# Use different port
python scripts/start_studio.py --port 8124
```

### Debug Mode
```bash
# Enable verbose logging
LANGGRAPH_DEBUG=1 python scripts/start_studio.py --debug
```

### Log Files
- **Application logs**: `logs/ragent_chatbot.log`
- **LangGraph Studio logs**: Console output
- **API logs**: Check API client responses

## 📚 Additional Resources

### Documentation
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Studio Guide](https://langchain-ai.github.io/langgraph/how-tos/langgraph-studio/)
- [Project README](README.md)

### Team Resources
- **Repository**: https://github.com/yamenahmad19801980/ragent_chatbot
- **Hugging Face Space**: https://huggingface.co/spaces/yamen19801980/ragent_chatbot
- **Issues**: Use GitHub Issues for bug reports

### Development Tips
1. **Always test in LangGraph Studio** before deploying
2. **Use version control** for all changes
3. **Document new features** in this guide
4. **Share debugging insights** with the team
5. **Keep prompts in MD format** for maintainability

---

**Happy Coding! 🎉**

For questions or issues, please:
1. Check this guide first
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Ask in team chat for quick help
