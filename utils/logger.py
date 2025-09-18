"""
Centralized logging system for the ragent_chatbot project.
Provides structured logging with different levels and formatters.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Color the level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


class RagentLogger:
    """Centralized logger for the ragent_chatbot application."""
    
    _loggers = {}
    _initialized = False
    
    @classmethod
    def setup_logging(cls, 
                     log_level: str = "INFO",
                     log_file: Optional[str] = None,
                     structured: bool = False,
                     colored: bool = True):
        """Setup the logging configuration."""
        if cls._initialized:
            return
        
        # Create logs directory if it doesn't exist
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        if colored and not structured:
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        elif structured:
            console_formatter = StructuredFormatter()
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            if structured:
                file_formatter = StructuredFormatter()
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger instance for a specific module."""
        if not cls._initialized:
            cls.setup_logging()
        
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def log_api_call(cls, logger: logging.Logger, method: str, url: str, 
                    status_code: Optional[int] = None, response_time: Optional[float] = None,
                    error: Optional[str] = None):
        """Log API call details."""
        extra_fields = {
            "api_method": method,
            "api_url": url,
            "api_status_code": status_code,
            "api_response_time": response_time,
            "api_error": error
        }
        
        if error:
            logger.error(f"API call failed: {method} {url}", extra={"extra_fields": extra_fields})
        else:
            logger.info(f"API call successful: {method} {url} - {status_code} ({response_time}ms)", 
                       extra={"extra_fields": extra_fields})
    
    @classmethod
    def log_device_operation(cls, logger: logging.Logger, operation: str, device_uuid: str,
                           success: bool, details: Optional[Dict] = None):
        """Log device operation details."""
        extra_fields = {
            "device_operation": operation,
            "device_uuid": device_uuid,
            "device_success": success,
            "device_details": details
        }
        
        if success:
            logger.info(f"Device operation successful: {operation} on {device_uuid}", 
                       extra={"extra_fields": extra_fields})
        else:
            logger.error(f"Device operation failed: {operation} on {device_uuid}", 
                        extra={"extra_fields": extra_fields})
    
    @classmethod
    def log_intent_detection(cls, logger: logging.Logger, user_message: str, 
                           detected_intents: List[Dict], processing_time: Optional[float] = None):
        """Log intent detection details."""
        extra_fields = {
            "intent_user_message": user_message,
            "intent_detected": detected_intents,
            "intent_processing_time": processing_time
        }
        
        logger.info(f"Intent detection completed for: {user_message[:50]}...", 
                   extra={"extra_fields": extra_fields})
    
    @classmethod
    def log_conversation_turn(cls, logger: logging.Logger, user_message: str, 
                            ai_response: str, turn_id: Optional[str] = None):
        """Log conversation turn details."""
        extra_fields = {
            "conversation_turn_id": turn_id,
            "conversation_user_message": user_message,
            "conversation_ai_response": ai_response
        }
        
        logger.info(f"Conversation turn completed", extra={"extra_fields": extra_fields})
    
    @classmethod
    def log_performance(cls, logger: logging.Logger, operation: str, duration: float, 
                       details: Optional[Dict] = None):
        """Log performance metrics."""
        extra_fields = {
            "performance_operation": operation,
            "performance_duration": duration,
            "performance_details": details
        }
        
        logger.info(f"Performance: {operation} took {duration:.3f}s", 
                   extra={"extra_fields": extra_fields})


# Convenience functions for easy access
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return RagentLogger.get_logger(name)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None, 
                 structured: bool = False, colored: bool = True):
    """Setup the logging configuration."""
    RagentLogger.setup_logging(log_level, log_file, structured, colored)


def log_api_call(logger: logging.Logger, method: str, url: str, 
                status_code: Optional[int] = None, response_time: Optional[float] = None,
                error: Optional[str] = None):
    """Log API call details."""
    RagentLogger.log_api_call(logger, method, url, status_code, response_time, error)


def log_device_operation(logger: logging.Logger, operation: str, device_uuid: str,
                        success: bool, details: Optional[Dict] = None):
    """Log device operation details."""
    RagentLogger.log_device_operation(logger, operation, device_uuid, success, details)


def log_intent_detection(logger: logging.Logger, user_message: str, 
                        detected_intents: List[Dict], processing_time: Optional[float] = None):
    """Log intent detection details."""
    RagentLogger.log_intent_detection(logger, user_message, detected_intents, processing_time)


def log_conversation_turn(logger: logging.Logger, user_message: str, 
                         ai_response: str, turn_id: Optional[str] = None):
    """Log conversation turn details."""
    RagentLogger.log_conversation_turn(logger, user_message, ai_response, turn_id)


def log_performance(logger: logging.Logger, operation: str, duration: float, 
                   details: Optional[Dict] = None):
    """Log performance metrics."""
    RagentLogger.log_performance(logger, operation, duration, details)
