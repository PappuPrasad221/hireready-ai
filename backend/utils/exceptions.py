from fastapi import HTTPException, status
from typing import Any, Dict, Optional
from datetime import datetime
import traceback

class HireReadyException(Exception):
    """Base exception for HireReady AI application"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)

class ValidationError(HireReadyException):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR")
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = str(value)

class AuthenticationError(HireReadyException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")

class AuthorizationError(HireReadyException):
    """Raised when user lacks permissions"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, "AUTHZ_ERROR")

class ResourceNotFoundError(HireReadyException):
    """Raised when requested resource is not found"""
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None):
        super().__init__(message, "NOT_FOUND")
        if resource_type:
            self.details["resource_type"] = resource_type
        if resource_id:
            self.details["resource_id"] = resource_id

class FileProcessingError(HireReadyException):
    """Raised when file processing fails"""
    def __init__(self, message: str, file_type: str = None, file_size: int = None):
        super().__init__(message, "FILE_ERROR")
        if file_type:
            self.details["file_type"] = file_type
        if file_size:
            self.details["file_size"] = file_size

class AIServiceError(HireReadyException):
    """Raised when AI service calls fail"""
    def __init__(self, message: str, service: str = None, model: str = None):
        super().__init__(message, "AI_ERROR")
        if service:
            self.details["service"] = service
        if model:
            self.details["model"] = model

class DatabaseError(HireReadyException):
    """Raised when database operations fail"""
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, "DB_ERROR")
        if operation:
            self.details["operation"] = operation

class RateLimitError(HireReadyException):
    """Raised when rate limits are exceeded"""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(message, "RATE_LIMIT")
        if retry_after:
            self.details["retry_after"] = retry_after

def handle_exception(exc: Exception) -> HTTPException:
    """Convert custom exceptions to HTTP exceptions"""
    
    if isinstance(exc, HireReadyException):
        status_code = _get_status_code(exc.error_code)
        return HTTPException(
            status_code=status_code,
            detail={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": exc.timestamp.isoformat()
            }
        )
    
    elif isinstance(exc, HTTPException):
        return exc
    
    else:
        # Log unexpected exceptions
        import traceback
        traceback.print_exc()
        
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"type": type(exc).__name__},
                "timestamp": datetime.now().isoformat()
            }
        )

def _get_status_code(error_code: str) -> int:
    """Get HTTP status code for error type"""
    status_codes = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "AUTH_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHZ_ERROR": status.HTTP_403_FORBIDDEN,
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "FILE_ERROR": status.HTTP_400_BAD_REQUEST,
        "AI_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "DB_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "RATE_LIMIT": status.HTTP_429_TOO_MANY_REQUESTS,
        "INTERNAL_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    
    return status_codes.get(error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

def create_error_response(error_code: str, message: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "error": error_code,
        "message": message,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }

def validate_file_upload(file_size: int, file_type: str, max_size: int = 10 * 1024 * 1024):
    """Validate file upload parameters"""
    if file_size > max_size:
        raise ValidationError(
            f"File size exceeds maximum allowed size of {max_size // (1024*1024)}MB",
            "file_size",
            file_size
        )
    
    allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
    if file_type not in allowed_types:
        raise ValidationError(
            f"File type {file_type} is not allowed. Allowed types: {', '.join(allowed_types)}",
            "file_type",
            file_type
        )

def validate_required_fields(data: Dict[str, Any], required_fields: list):
    """Validate required fields in request data"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            "required_fields",
            missing_fields
        )

def validate_email_format(email: str):
    """Validate email format"""
    import re
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValidationError(
            "Invalid email format",
            "email",
            email
        )

def validate_password_strength(password: str):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError(
            "Password must be at least 8 characters long",
            "password"
        )
    
    if not any(c.isupper() for c in password):
        raise ValidationError(
            "Password must contain at least one uppercase letter",
            "password"
        )
    
    if not any(c.islower() for c in password):
        raise ValidationError(
            "Password must contain at least one lowercase letter",
            "password"
        )
    
    if not any(c.isdigit() for c in password):
        raise ValidationError(
            "Password must contain at least one digit",
            "password"
        )

def validate_role(role: str):
    """Validate user role"""
    allowed_roles = ['user', 'admin', 'interviewer']
    
    if role not in allowed_roles:
        raise ValidationError(
            f"Role must be one of: {', '.join(allowed_roles)}",
            "role",
            role
        )

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially harmful characters
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def validate_json_data(data: str):
    """Validate JSON data format"""
    import json
    
    try:
        json.loads(data)
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON format: {str(e)}",
            "json_data",
            data[:100] + "..." if len(data) > 100 else data
        )
