# Comprehensive Logging System Guide

## Overview

The ragent_chatbot implements a comprehensive logging system that provides structured logging, performance monitoring, and detailed tracking throughout the application. This guide explains how to use and configure the logging system.

## Features

### 🎯 **Centralized Logging**
- Single logger instance per module
- Consistent formatting across all components
- Easy configuration through environment variables

### 📊 **Structured Logging**
- JSON-formatted logs for easy parsing
- Structured data with extra fields
- Machine-readable format for analysis

### 🎨 **Colored Console Output**
- Color-coded log levels for easy reading
- Configurable color schemes
- Clean console output during development

### 📁 **File Logging**
- Automatic log file rotation
- Configurable log file paths
- UTF-8 encoding support

### ⚡ **Performance Monitoring**
- Built-in performance tracking
- API call timing
- Operation duration logging

## Configuration

### Environment Variables

```bash
# Logging Configuration
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/ragent_chatbot.log  # Log file path (optional)
LOG_STRUCTURED=false              # Enable JSON structured logging
LOG_COLORED=true                  # Enable colored console output
```

### Programmatic Configuration

```python
from utils.logger import setup_logging

# Setup logging with custom configuration
setup_logging(
    log_level="DEBUG",
    log_file="logs/app.log",
    structured=True,
    colored=True
)
```

## Usage Examples

### 1. Basic Logging

```python
from utils.logger import get_logger

# Get logger for your module
logger = get_logger(__name__)

# Basic logging
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
logger.debug("Debug information")
```

### 2. API Call Logging

```python
from utils.logger import log_api_call
import time

def make_api_call(url, method="GET"):
    start_time = time.time()
    try:
        response = requests.get(url)
        response_time = (time.time() - start_time) * 1000
        log_api_call(logger, method, url, response.status_code, response_time)
        return response
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        log_api_call(logger, method, url, None, response_time, str(e))
        raise
```

### 3. Device Operation Logging

```python
from utils.logger import log_device_operation

def control_device(device_uuid, action):
    try:
        # Perform device operation
        result = perform_device_action(device_uuid, action)
        log_device_operation(logger, "control_device", device_uuid, True, {
            "action": action,
            "result": result
        })
        return result
    except Exception as e:
        log_device_operation(logger, "control_device", device_uuid, False, {
            "action": action,
            "error": str(e)
        })
        raise
```

### 4. Intent Detection Logging

```python
from utils.logger import log_intent_detection
import time

def detect_intent(user_message):
    start_time = time.time()
    try:
        intents = process_intent_detection(user_message)
        processing_time = time.time() - start_time
        log_intent_detection(logger, user_message, intents, processing_time)
        return intents
    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        raise
```

### 5. Performance Logging

```python
from utils.logger import log_performance
import time

def expensive_operation():
    start_time = time.time()
    try:
        # Perform expensive operation
        result = perform_operation()
        duration = time.time() - start_time
        log_performance(logger, "expensive_operation", duration, {
            "result_count": len(result),
            "operation_type": "data_processing"
        })
        return result
    except Exception as e:
        duration = time.time() - start_time
        log_performance(logger, "expensive_operation", duration, {
            "error": str(e),
            "operation_type": "data_processing"
        })
        raise
```

### 6. Conversation Logging

```python
from utils.logger import log_conversation_turn
import uuid

def handle_conversation(user_message, ai_response):
    turn_id = str(uuid.uuid4())
    log_conversation_turn(logger, user_message, ai_response, turn_id)
    return ai_response
```

## Log Output Examples

### Console Output (Colored)

```
2024-01-15 10:30:45,123 - ragent_chatbot.agent - INFO - Intent detection completed for: Turn on the lights...
2024-01-15 10:30:45,234 - ragent_chatbot.api_client - INFO - API call successful: POST https://api.example.com/login - 200 (150ms)
2024-01-15 10:30:45,345 - ragent_chatbot.device_service - INFO - Device operation successful: control_device on device-123
2024-01-15 10:30:45,456 - ragent_chatbot.agent - INFO - Performance: handle_control took 0.234s
```

### Structured JSON Output

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "ragent_chatbot.agent",
  "message": "Intent detection completed for: Turn on the lights...",
  "module": "agent",
  "function": "_detect_intent",
  "line": 125,
  "extra_fields": {
    "intent_user_message": "Turn on the lights",
    "intent_detected": [{"intent": "control", "device_uuid": "light-123"}],
    "intent_processing_time": 0.234
  }
}
```

## Integration Throughout the Application

### 1. **API Client** (`domain/api_client.py`)
- Logs all API calls with timing and status
- Tracks authentication and device operations
- Records errors and retries

### 2. **Device Service** (`services/device_service.py`)
- Logs device operations and caching
- Tracks performance metrics
- Records device control results

### 3. **Agent** (`agent.py`)
- Logs intent detection and routing
- Tracks conversation turns
- Monitors performance of each node

### 4. **Memory Management** (`memory/chat_memory.py`)
- Logs memory operations
- Tracks checkpoint creation
- Records conversation history

### 5. **Tool Registry** (`tool_registry.py`)
- Logs tool initialization
- Tracks tool usage
- Records tool execution results

## Best Practices

### 1. **Use Appropriate Log Levels**
```python
logger.debug("Detailed debugging information")
logger.info("General information about program execution")
logger.warning("Something unexpected happened, but the program can continue")
logger.error("A serious error occurred")
logger.critical("A very serious error occurred, the program may not be able to continue")
```

### 2. **Include Context in Log Messages**
```python
# Good
logger.info(f"Processing device {device_uuid} with action {action}")

# Better
logger.info(f"Processing device {device_uuid} with action {action}", extra={
    "extra_fields": {
        "device_uuid": device_uuid,
        "action": action,
        "user_id": user_id
    }
})
```

### 3. **Log Performance Metrics**
```python
import time

start_time = time.time()
# ... perform operation ...
duration = time.time() - start_time
log_performance(logger, "operation_name", duration, {"details": "value"})
```

### 4. **Handle Exceptions Properly**
```python
try:
    # ... risky operation ...
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

## Monitoring and Analysis

### 1. **Log File Analysis**
```bash
# View recent logs
tail -f logs/ragent_chatbot.log

# Search for errors
grep "ERROR" logs/ragent_chatbot.log

# Count API calls
grep "API call" logs/ragent_chatbot.log | wc -l
```

### 2. **Structured Log Analysis**
```python
import json

# Parse structured logs
with open("logs/ragent_chatbot.log", "r") as f:
    for line in f:
        log_entry = json.loads(line)
        if log_entry["level"] == "ERROR":
            print(f"Error: {log_entry['message']}")
```

### 3. **Performance Monitoring**
```python
# Extract performance metrics
performance_logs = []
with open("logs/ragent_chatbot.log", "r") as f:
    for line in f:
        log_entry = json.loads(line)
        if "performance_duration" in log_entry.get("extra_fields", {}):
            performance_logs.append(log_entry)

# Analyze performance
durations = [log["extra_fields"]["performance_duration"] for log in performance_logs]
avg_duration = sum(durations) / len(durations)
print(f"Average operation duration: {avg_duration:.3f}s")
```

## Troubleshooting

### Common Issues

1. **Logs not appearing**
   - Check LOG_LEVEL configuration
   - Verify log file permissions
   - Ensure logger is properly initialized

2. **Performance impact**
   - Use appropriate log levels
   - Consider async logging for high-volume applications
   - Monitor log file size and rotation

3. **Structured logging issues**
   - Ensure all extra fields are JSON serializable
   - Check for circular references in objects
   - Validate JSON output format

## Conclusion

The comprehensive logging system provides:
- **Visibility**: Complete visibility into application behavior
- **Debugging**: Easy debugging with detailed context
- **Monitoring**: Performance and error monitoring
- **Analysis**: Structured data for analysis and optimization

This logging system is essential for maintaining and debugging the ragent_chatbot application in production environments.
