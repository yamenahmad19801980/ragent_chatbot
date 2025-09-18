# 🔄 Ragent Chatbot Workflow Diagram

## Complete User Command to Result Cycle

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           🏠 RAGENT CHATBOT WORKFLOW                           │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   👤 USER       │    │  🖥️ GRADIO       │    │  🤖 AGENT       │
│   INPUT         │    │  INTERFACE       │    │  PROCESSING     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │ "Turn off switch 2"    │                        │
         ├───────────────────────►│                        │
         │                        │ chat_fn(message,        │
         │                        │  history)               │
         │                        ├────────────────────────►│
         │                        │                        │
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 📝 MESSAGE      │
         │                        │                        │ │ NORMALIZATION   │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ normalize_gradio_history()
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 🎯 INTENT       │
         │                        │                        │ │ DETECTION       │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ LLM analyzes message
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 🔀 INTENT       │
         │                        │                        │ │ ROUTING         │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ Intent: "control"
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 🏠 DEVICE       │
         │                        │                        │ │ CONTROL         │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ DeviceService.control_multiple_devices()
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 🔧 API          │
         │                        │                        │ │ EXECUTION       │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ batch_control("COMMAND", [device_uuid], "turn_off", false)
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ ✅ RESULT       │
         │                        │                        │ │ GENERATION      │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ "✅ Successfully controlled device switch_2"
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 📤 RESPONSE     │
         │                        │                        │ │ TO USER         │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ AIMessage(content="Device control result(s): ...")
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 🔄 STATE        │
         │                        │                        │ │ UPDATE          │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ Add to conversation state
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 📋 RETURN       │
         │                        │                        │ │ TO GRADIO       │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ return reply
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 🖥️ GRADIO       │
         │                        │                        │ │ DISPLAY         │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ Update chat history
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 👤 USER         │
         │                        │                        │ │ SEES RESULT     │
         │                        │                        │ └─────────────────┘
         │                        │                        │         │
         │                        │                        │         │ "✅ Successfully controlled device switch_2"
         │                        │                        │         ▼
         │                        │                        │ ┌─────────────────┐
         │                        │                        │ │ 🎉 COMPLETE     │
         │                        │                        │ │ CYCLE           │
         │                        │                        │ └─────────────────┘
```

## 🔄 Alternative Workflows

### **Query Workflow:**
```
User: "What's the status of the AC?"
↓
Intent: "query"
↓
_handle_query() → DeviceService.query_device_status()
↓
API: get_status(device_uuid)
↓
Result: "AC is currently OFF, temperature set to 72°F"
```

### **Scheduling Workflow:**
```
User: "Turn on lights at 7 PM tomorrow"
↓
Intent: "schedule"
↓
_handle_schedule() → DeviceService.schedule_multiple_devices()
↓
Creates schedule: device_uuid + time + action
↓
Result: "✅ Scheduled lights to turn on at 7:00 PM tomorrow"
```

### **Scene Workflow:**
```
User: "Activate movie night scene"
↓
Intent: "scene"
↓
_handle_scene() → DeviceService.trigger_scene_by_name()
↓
API: trigger_scene(scene_uuid)
↓
Result: "🎬 Movie night scene activated!"
```

### **Conversation Workflow:**
```
User: "What's the weather like?"
↓
Intent: "conversation"
↓
_chat_node() → Web search tool
↓
Search API call
↓
Result: "Today's weather is sunny with 75°F..."
```

## 🏗️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Gradio UI     │  │   Web Interface │  │   Mobile App    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   LangGraph     │  │   Intent        │  │   Message       │ │
│  │   Agent         │  │   Detection     │  │   Normalizer    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        SERVICE LAYER                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Device        │  │   Prompt        │  │   Memory        │ │
│  │   Service       │  │   Templates     │  │   Management    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                        INTEGRATION LAYER                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Syncrow API   │  │   Qwen LLM      │  │   Web Search    │ │
│  │   (IoT Devices) │  │   (Language)    │  │   (Information) │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

- **🔄 Real-time Processing**: Instant response to user commands
- **🧠 Intelligent Routing**: Automatic intent detection and routing
- **🏠 Device Control**: Direct IoT device manipulation
- **⏰ Scheduling**: Future action planning
- **🎬 Scenes**: Complex multi-device automation
- **💬 Natural Language**: Human-like conversation
- **🔍 Web Search**: External information retrieval
- **📱 Web Interface**: Easy-to-use Gradio UI
- **🔄 State Management**: Conversation persistence
- **🛡️ Error Handling**: Graceful failure recovery
