# LangGraph Studio Setup for Ragent Chatbot

This directory contains the configuration and setup for LangGraph Studio, enabling developers to visualize, debug, and test the chatbot's graph workflow.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- LangGraph Studio installed: `pip install langgraph-studio`
- All project dependencies installed

### 1. Install LangGraph Studio
```bash
# From the project root directory
pip install langgraph-studio

# Or install from requirements
pip install -r requirements.txt
```

### 2. Start LangGraph Studio
```bash
# From the studio directory
cd studio
langgraph-studio

# Or from project root
langgraph-studio --config studio/langgraph.json
```

### 3. Access the Studio
Open your browser to: http://localhost:8123

## 📁 Configuration Files

### `langgraph.json`
Main configuration file that tells LangGraph Studio:
- Where to find the graph (`../agent.py:get_compiled_graph`)
- Environment variables (`.env` file)
- Working directory (project root)

### `.langgraph_api/`
Directory containing:
- Checkpoint files (`.pckl`) - Graph state persistence
- Store files - Memory and conversation history
- Retry counters - Error handling state

## 🔧 Development Features

### Graph Visualization
- **Node Flow**: See how messages flow through intent detection → routing → execution
- **State Inspection**: View conversation state at each step
- **Error Tracking**: Identify where and why errors occur

### Debugging Tools
- **Step-by-step Execution**: Run individual nodes in isolation
- **State Modification**: Manually adjust conversation state
- **Tool Testing**: Test individual tools without full conversation flow

### Testing Capabilities
- **Message Simulation**: Send test messages to any node
- **Edge Case Testing**: Test ambiguous, high-risk, and error scenarios
- **Performance Monitoring**: Track execution time and resource usage

## 🎯 Common Use Cases

### 1. Testing Intent Detection
```python
# Test message: "Turn on the kitchen light"
# Expected: Intent = "control", Device = "kitchen light"
```

### 2. Debugging Device Control
```python
# Test message: "Set temperature to 72"
# Check: Device lookup, function mapping, API call
```

### 3. Testing Error Handling
```python
# Test message: "Turn on the TV"
# Expected: Intent = "ambiguous" (if no TV device exists)
```

## 🛠️ Development Workflow

### 1. Start Development Session
```bash
# Terminal 1: Start LangGraph Studio
cd studio
langgraph-studio

# Terminal 2: Start your app (optional)
cd ..
python app.py
```

### 2. Test Graph Changes
1. Modify code in `agent.py` or related files
2. Refresh LangGraph Studio (Ctrl+R)
3. Test the changes with sample messages
4. Debug any issues using the visualization tools

### 3. Debug Specific Issues
1. Use the graph visualization to trace message flow
2. Set breakpoints at specific nodes
3. Inspect state variables and tool outputs
4. Modify state manually to test edge cases

## 📊 Graph Structure

```
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
  ├── high_risk → request_confirmation
  └── conversation → chat_node
  ↓
END
```

## 🔍 Key Nodes to Monitor

### `detect_intent`
- **Input**: User message, device list
- **Output**: Intent classification with tool calls
- **Debug**: Check if devices are properly loaded

### `route_message`
- **Input**: Intent classification results
- **Output**: Next node to execute
- **Debug**: Verify routing logic for each intent type

### `handle_control`
- **Input**: Device control commands
- **Output**: Device control results
- **Debug**: API calls, device mapping, function execution

### `handle_query`
- **Input**: Status queries
- **Output**: Device status information
- **Debug**: Device lookup, status retrieval

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure you're in the project root
cd /path/to/ragent_chatbot
langgraph-studio --config studio/langgraph.json
```

#### 2. Environment Variables
```bash
# Check .env file exists and has required variables
cat .env
```

#### 3. Graph Compilation Errors
```bash
# Test graph compilation
python -c "from agent import get_compiled_graph; print('Graph compiled successfully')"
```

#### 4. Port Already in Use
```bash
# Use different port
langgraph-studio --port 8124
```

### Debug Mode
```bash
# Enable verbose logging
LANGGRAPH_DEBUG=1 langgraph-studio
```

## 📝 Best Practices

### 1. Regular Testing
- Test after each code change
- Use both positive and negative test cases
- Verify error handling paths

### 2. State Inspection
- Always check conversation state between nodes
- Verify tool call arguments are correct
- Monitor memory usage and cleanup

### 3. Performance Monitoring
- Track execution time for each node
- Monitor API call latency
- Check for memory leaks in long conversations

### 4. Documentation
- Document any custom nodes or edges
- Update this README when adding new features
- Share debugging insights with the team

## 🔗 Useful Links

- [LangGraph Studio Documentation](https://langchain-ai.github.io/langgraph/how-tos/langgraph-studio/)
- [LangGraph Concepts](https://langchain-ai.github.io/langgraph/concepts/)
- [Project Repository](https://github.com/yamenahmad19801980/ragent_chatbot)

## 👥 Team Collaboration

### Sharing Configurations
- Commit `langgraph.json` to version control
- Don't commit `.langgraph_api/` files (add to `.gitignore`)
- Share debugging insights in team chat

### Code Reviews
- Test graph changes in LangGraph Studio before submitting PR
- Include screenshots of graph visualization for complex changes
- Document any new nodes or routing logic

---

**Happy Debugging! 🐛✨**
