# LangSmith Integration Setup

This document explains how to set up LangSmith for tracking and debugging your Smart Home Assistant.

## What is LangSmith?

LangSmith is a platform for debugging, testing, evaluating, and monitoring LLM applications. It provides:

- **Conversation Tracking**: See all interactions in a visual interface
- **Performance Monitoring**: Track response times and token usage
- **Error Debugging**: Detailed error logs and stack traces
- **Evaluation Tools**: Test and compare different prompts and models
- **Analytics**: Usage patterns and conversation insights

## Setup Instructions

### 1. Get LangSmith API Key

1. Go to [https://smith.langchain.com](https://smith.langchain.com)
2. Sign up or log in to your account
3. Go to Settings → API Keys
4. Create a new API key
5. Copy the API key

### 2. Configure Environment Variables

Add these environment variables to your `.env` file or Hugging Face Space secrets:

```env
# LangSmith Configuration
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=ragent-chatbot
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

### 3. Optional Configuration

You can customize the project name and endpoint:

- `LANGSMITH_PROJECT`: Name of your project in LangSmith (default: "ragent-chatbot")
- `LANGSMITH_ENDPOINT`: LangSmith API endpoint (default: https://api.smith.langchain.com)

## Features Enabled

Once configured, LangSmith will automatically track:

### 1. Conversation Flows
- User messages and assistant responses
- Intent detection results
- Device control actions
- Error handling and recovery

### 2. Performance Metrics
- Response times for each step
- Token usage and costs
- Success/failure rates
- Graph execution paths

### 3. Debug Information
- Detailed logs for each node in the LangGraph
- Tool call parameters and results
- API request/response data
- Error stack traces

## Viewing Your Data

1. Go to [https://smith.langchain.com](https://smith.langchain.com)
2. Navigate to your project
3. View conversations in the "Traces" section
4. Analyze performance in the "Analytics" section
5. Debug issues in the "Debug" section

## Debugging Features

### Conversation Tracking
- See the complete conversation flow
- Identify where issues occur
- Track user satisfaction and response quality

### Performance Analysis
- Monitor response times
- Identify bottlenecks
- Optimize prompt engineering

### Error Debugging
- Detailed error logs
- Stack trace analysis
- Context preservation

## Troubleshooting

### LangSmith Not Working
- Check that `LANGSMITH_API_KEY` is set correctly
- Verify the API key is valid and has proper permissions
- Check network connectivity to LangSmith servers

### Missing Data
- Ensure the environment variables are loaded correctly
- Check that the LangSmith client is initialized properly
- Verify the project name matches your LangSmith project

### Performance Issues
- LangSmith adds minimal overhead (~10-50ms per request)
- If performance is critical, you can disable it by removing the API key
- Consider using sampling for high-volume applications

## Advanced Configuration

### Custom Run Names
The system automatically creates descriptive run names based on user messages. You can customize this in `llm/langsmith_config.py`.

### Metadata Tracking
Additional metadata is automatically included:
- User ID
- Project UUIDs
- Conversation type
- Timestamps

### Sampling
For high-volume applications, you can implement sampling to reduce costs:

```python
# In langsmith_config.py
os.environ["LANGCHAIN_SAMPLING_RATE"] = "0.1"  # 10% sampling
```

## Support

For LangSmith-specific issues:
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangSmith Support](https://smith.langchain.com/support)

For this project:
- Check the GitHub repository issues
- Review the debug logs in the application
