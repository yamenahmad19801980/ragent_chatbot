# Smart Home Assistant (Ragent Chatbot)

An intelligent smart home assistant built with LangGraph and Gradio that can control IoT devices, schedule actions, and engage in natural conversation.

## Features

- 🤖 **Intelligent Intent Detection**: Automatically classifies user commands (control, query, schedule, scene, conversation)
- 🏠 **IoT Device Control**: Control switches, AC, lights, curtains, and other smart devices
- ⏰ **Device Scheduling**: Schedule device actions for specific times and days
- 🎬 **Scene Management**: Trigger smart home scenes for different moods/activities
- 🔍 **Web Search**: Answer general questions using web search capabilities
- 💬 **Natural Conversation**: Engage in friendly chat and general conversation
- 🛡️ **Safety Features**: High-risk action confirmation and validation

## Architecture

The project follows a clean, modular architecture:

```
ragent_chatbot/
├── app.py                      # Gradio UI / entrypoint
├── agent.py                    # LangGraph agent implementation
├── config.py                   # Configuration management
├── tool_registry.py            # Tool registration and management
├── requirements.txt
├── README.md
├── .env                        # Environment variables (create from .env.example)
│
├── prompts/
│  ├── agent_prompt.txt         # Chat/agent system prompt
│  └── intent_prompt.txt        # Intent classification prompt
│
├── tools/
│  ├── base_tool.py             # Base tool interface
│  ├── device_tools.py          # IoT device control tools
│  └── web_search_tool.py       # Web search capabilities
│
├── llm/
│  └── qwen_llm.py              # Qwen LLM configuration
│
├── memory/
│  └── chat_memory.py           # Chat memory management
│
├── domain/
│  ├── objects.py               # Pydantic models
│  └── api_client.py            # Syncrow API client
│
├── data/
│   └── device_mappings.csv     # Device function mappings
│
└── utils/
    └── normalizer.py           # Message normalization utilities
```

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yamenahmad19801980/ragent_chatbot.git
   cd ragent_chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Create a `.env` file in the root directory:
   ```env
   # API Keys
   QWEN_API_KEY=your_qwen_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   
   # Syncrow API Credentials
   EMAIL=your_email_here
   PASSWORD=your_password_here
   
   # Optional: Database Configuration
   SQL_DATABASE=your_database_name
   SQL_USER=your_db_user
   SQL_HOST=your_db_host
   SQL_PASSWORD=your_db_password
   SQL_PORT=5432
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access the interface**:
   Open your browser and go to `http://localhost:7860`

## Usage Examples

### Device Control
- "Turn on the living room lights"
- "Set the AC temperature to 72 degrees"
- "Turn off switch 1 in the 3 gang switch"

### Device Queries
- "What's the status of the kitchen switch?"
- "Is the AC running?"

### Scheduling
- "Schedule the AC to turn on at 8 AM tomorrow"
- "Turn on the lights at 7 PM every weekday"

### Scenes
- "Activate movie night scene"
- "Make it cozy"

### General Conversation
- "What's the weather like today?"
- "Tell me a joke"
- "Search for Thai restaurants nearby"

## API Integration

The chatbot integrates with the Syncrow IoT platform API to:
- Control IoT devices (switches, AC, lights, curtains)
- Query device status and functions
- Schedule device actions
- Trigger smart home scenes

## Development

### Adding New Tools

1. Create a new tool class in `tools/`
2. Register it in `tool_registry.py`
3. Update the agent routing if needed

### Customizing Prompts

Edit the prompt files in `prompts/` to customize the agent's behavior and responses.

### Adding New Device Types

Update `data/device_mappings.csv` with new device types and their available functions.

## Deployment

The application is configured for deployment on Hugging Face Spaces with GitHub Actions for automatic deployment.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue on GitHub.
