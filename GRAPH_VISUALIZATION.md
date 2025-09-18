# 🏠 Smart Home Assistant - LangGraph Visualization

## 📊 **Graph Structure Overview**

```
                    START
                      │
                      ▼
              ┌───────────────┐
              │ detect_intent │
              └───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ route_message │ ◄─── Decision Node
              └───────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   control   │ │    query    │ │  schedule   │
│             │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│    scene    │ │   chat_node │ │ambiguous/   │
│             │ │             │ │clarification│
└─────────────┘ └─────────────┘ └─────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
              ┌───────────────┐
              │enhance_response│
              └───────────────┘
                      │
                      ▼
                     END
```

## 🔄 **Detailed Flow Diagram**

```
START
  │
  ▼
┌─────────────────────────────────────────┐
│            detect_intent                │
│  • Analyzes user input                  │
│  • Classifies intent                    │
│  • Identifies target devices            │
│  • Returns classification result        │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│           route_message                 │ ◄─── DECISION POINT
│  • Routes based on intent               │
│  • Handles multiple intents             │
│  • Manages parallel processing          │
└─────────────────────────────────────────┘
  │
  ├─── control ────► ┌─────────────────────┐
  │                  │   handle_control    │
  │                  │  • Device control   │
  │                  │  • API calls        │
  │                  │  • Error handling   │
  │                  └─────────────────────┘
  │
  ├─── query ──────► ┌─────────────────────┐
  │                  │    handle_query     │
  │                  │  • Status queries   │
  │                  │  • Device info      │
  │                  │  • Data retrieval   │
  │                  └─────────────────────┘
  │
  ├─── schedule ───► ┌─────────────────────┐
  │                  │   handle_schedule   │
  │                  │  • Time-based tasks │
  │                  │  • Recurring events │
  │                  │  • Calendar mgmt    │
  │                  └─────────────────────┘
  │
  ├─── scene ──────► ┌─────────────────────┐
  │                  │    handle_scene     │
  │                  │  • Scene activation │
  │                  │  • Configuration    │
  │                  │  • State management │
  │                  └─────────────────────┘
  │
  ├─── conversation ► ┌─────────────────────┐
  │                  │     chat_node       │
  │                  │  • General chat     │
  │                  │  • Web search       │
  │                  │  • Tool usage       │
  │                  └─────────────────────┘
  │
  ├─── ambiguous ──► ┌─────────────────────┐
  │                  │request_clarification│
  │                  │  • Ask for details  │
  │                  │  • Provide help     │
  │                  │  • Guide user       │
  │                  └─────────────────────┘
  │
  └─── high_risk ──► ┌─────────────────────┐
                     │request_confirmation │
                     │  • Safety checks    │
                     │  • User approval    │
                     │  • Risk assessment  │
                     └─────────────────────┘
                            │
                            ▼
                     ┌─────────────────────┐
                     │ confirmation_result │ ◄─── DECISION POINT
                     └─────────────────────┘
                            │
                            ├─── confirmed ──► handle_control
                            ├─── cancelled ──► END
                            └─── unclear ────► request_confirmation

All user-facing nodes ──► ┌─────────────────────┐
                          │  enhance_response   │
                          │  • Improve tone     │
                          │  • User-friendly    │
                          │  • Final polish     │
                          └─────────────────────┘
                                   │
                                   ▼
                                  END
```

## 🎯 **Node Types and Colors**

| Node Type | Color | Description |
|-----------|-------|-------------|
| **START/END** | 🔵 Blue | Entry and exit points |
| **Processing** | 🟣 Purple | Data processing nodes |
| **Decision** | 🟠 Orange | Conditional routing |
| **Action** | 🟢 Green | Device control actions |
| **Enhancement** | 🟢 Green | Response improvement |

## 🔍 **How to View in LangSmith**

### **1. Trace View**
- Open any conversation trace
- Look for the "Graph" or "Execution" tab
- See nodes connected by arrows

### **2. Node Details**
- Click on any node to see:
  - Input/output data
  - Execution time
  - Token usage
  - Error information

### **3. Flow Visualization**
- Timeline view shows execution order
- Graph view shows relationships
- Dependency view shows connections

## 📈 **Performance Monitoring**

### **Key Metrics to Watch**
1. **detect_intent**: Classification accuracy
2. **handle_control**: Device control success rate
3. **enhance_response**: Response quality
4. **Overall flow**: End-to-end performance

### **Common Issues**
1. **Intent misclassification**: Wrong routing
2. **API failures**: Device control errors
3. **Timeout issues**: Long-running operations
4. **Memory issues**: State management problems

## 🛠️ **Debugging Tips**

1. **Start with detect_intent**: Check if intent is correctly identified
2. **Follow the flow**: Trace execution through each node
3. **Check API calls**: Verify Syncrow API responses
4. **Monitor performance**: Look for slow nodes
5. **Review errors**: Check error logs and stack traces

## 📊 **Graph Statistics**

- **Total Nodes**: 9
- **Decision Points**: 2
- **Action Nodes**: 5
- **Processing Nodes**: 2
- **Maximum Depth**: 4 levels
- **Parallel Paths**: 6 (from route_message)

This graph structure provides a robust, scalable architecture for handling various types of smart home interactions while maintaining safety and user experience standards.
