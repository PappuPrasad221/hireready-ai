import logging
import sys
from datetime import datetime
from typing import Optional
import os

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Format the message
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        record.name = f"{log_color}{record.name}{reset_color}"
        
        return super().format(record)

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up logger with custom formatting"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = ColoredFormatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log directory exists
    log_dir = "logs"
    if os.path.exists(log_dir):
        file_handler = logging.FileHandler(f"{log_dir}/{name}.log")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# Create main application logger
app_logger = setup_logger("hireready_ai")

def log_request(method: str, path: str, user_id: Optional[str] = None):
    """Log API request"""
    user_info = f" | User: {user_id}" if user_id else ""
    app_logger.info(f"{method} {path}{user_info}")

def log_response(method: str, path: str, status_code: int, duration: float):
    """Log API response"""
    app_logger.info(f"{method} {path} | Status: {status_code} | Duration: {duration:.2f}s")

def log_error(error: Exception, context: str = ""):
    """Log error with context"""
    context_info = f" | Context: {context}" if context else ""
    app_logger.error(f"Error{context_info}: {str(error)}", exc_info=True)

def log_api_call(endpoint: str, method: str, user_id: Optional[str] = None, 
                 request_data: Optional[dict] = None, response_data: Optional[dict] = None):
    """Log detailed API call information"""
    user_info = f" | User: {user_id}" if user_id else ""
    
    log_message = f"API Call: {method} {endpoint}{user_info}"
    
    if request_data:
        # Log only non-sensitive data
        safe_data = {k: v for k, v in request_data.items() 
                     if k not in ['password', 'token', 'secret', 'key']}
        if safe_data:
            log_message += f" | Request: {safe_data}"
    
    if response_data:
        # Log only non-sensitive response data
        safe_response = {k: v for k, v in response_data.items() 
                        if k not in ['token', 'secret', 'key', 'password']}
        if safe_response:
            log_message += f" | Response: {safe_response}"
    
    app_logger.info(log_message)

def log_ai_interaction(service: str, operation: str, user_id: str, 
                       input_data: Optional[str] = None, output_data: Optional[str] = None):
    """Log AI service interactions"""
    log_message = f"AI Service: {service} | Operation: {operation} | User: {user_id}"
    
    if input_data:
        # Truncate long inputs
        safe_input = input_data[:200] + "..." if len(input_data) > 200 else input_data
        log_message += f" | Input: {safe_input}"
    
    if output_data:
        # Truncate long outputs
        safe_output = output_data[:200] + "..." if len(output_data) > 200 else output_data
        log_message += f" | Output: {safe_output}"
    
    app_logger.info(log_message)

def log_file_operation(operation: str, file_type: str, file_size: int, user_id: str):
    """Log file operations"""
    app_logger.info(f"File Operation: {operation} | Type: {file_type} | Size: {file_size} bytes | User: {user_id}")

def log_system_event(event: str, details: Optional[str] = None):
    """Log system events"""
    details_info = f" | Details: {details}" if details else ""
    app_logger.info(f"System Event: {event}{details_info}")

def log_performance_warning(operation: str, duration: float, threshold: float):
    """Log performance warnings"""
    app_logger.warning(f"Performance Warning: {operation} took {duration:.2f}s (threshold: {threshold:.2f}s)")

def log_security_event(event: str, user_id: Optional[str] = None, 
                        ip_address: Optional[str] = None, details: Optional[str] = None):
    """Log security-related events"""
    user_info = f" | User: {user_id}" if user_id else ""
    ip_info = f" | IP: {ip_address}" if ip_address else ""
    details_info = f" | Details: {details}" if details else ""
    
    app_logger.warning(f"Security Event: {event}{user_info}{ip_info}{details_info}")

# Create log directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")
