# Security Implementation & Hardening

## Overview

This document outlines comprehensive security measures for the enhanced multi-agent system, including authentication, authorization, input validation, rate limiting, audit logging, and protection against common vulnerabilities.

## Existing Security Review

### Current Security Infrastructure

**Existing Security in `backend/app/`:**

- Basic CORS configuration
- Simple error handling
- No authentication/authorization system
- Limited input validation
- No rate limiting
- No audit logging

**Security Gaps Identified:**
- No user authentication system
- Missing input sanitization
- No rate limiting on APIs
- Lack of audit trails
- No secure WebSocket connections
- Missing security headers

## Enhanced Security Architecture

### Authentication & Authorization System

**File: `backend/app/security/auth.py` (New)**

```python
"""
Comprehensive authentication and authorization system.
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import jwt
import bcrypt
import secrets
from enum import Enum
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = settings.SECRET_KEY or secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Permission(str, Enum):
    """System permissions."""
    # Agent permissions
    AGENT_READ = "agent:read"
    AGENT_CREATE = "agent:create"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"

    # Task permissions
    TASK_READ = "task:read"
    TASK_CREATE = "task:create"
    TASK_UPDATE = "task:update"
    TASK_CANCEL = "task:cancel"

    # Debate permissions
    DEBATE_READ = "debate:read"
    DEBATE_CREATE = "debate:create"
    DEBATE_UPDATE = "debate:update"

    # Ollama permissions
    OLLAMA_READ = "ollama:read"
    OLLAMA_CHAT = "ollama:chat"
    OLLAMA_ADMIN = "ollama:admin"

    # System permissions
    SYSTEM_READ = "system:read"
    SYSTEM_ADMIN = "system:admin"

# Role-based permission mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        # All permissions
        perm.value for perm in Permission
    ],
    UserRole.OPERATOR: [
        Permission.AGENT_READ.value,
        Permission.AGENT_EXECUTE.value,
        Permission.TASK_READ.value,
        Permission.TASK_CREATE.value,
        Permission.TASK_UPDATE.value,
        Permission.TASK_CANCEL.value,
        Permission.DEBATE_READ.value,
        Permission.DEBATE_CREATE.value,
        Permission.OLLAMA_READ.value,
        Permission.OLLAMA_CHAT.value,
        Permission.SYSTEM_READ.value,
    ],
    UserRole.ANALYST: [
        Permission.AGENT_READ.value,
        Permission.TASK_READ.value,
        Permission.DEBATE_READ.value,
        Permission.OLLAMA_READ.value,
        Permission.SYSTEM_READ.value,
    ],
    UserRole.VIEWER: [
        Permission.AGENT_READ.value,
        Permission.TASK_READ.value,
        Permission.DEBATE_READ.value,
        Permission.SYSTEM_READ.value,
    ]
}

# Pydantic models
class User(BaseModel):
    """User model."""
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime]

class UserCreate(BaseModel):
    """User creation model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER

class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str

class Token(BaseModel):
    """Token model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Token data model."""
    user_id: str
    username: str
    role: UserRole
    permissions: List[str]

# Security utilities
class AuthService:
    """Authentication and authorization service."""

    def __init__(self):
        self.security = HTTPBearer(auto_error=False)

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenData]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                return None

            user_id = payload.get("sub")
            username = payload.get("username")
            role = payload.get("role")

            if not all([user_id, username, role]):
                return None

            permissions = ROLE_PERMISSIONS.get(UserRole(role), [])

            return TokenData(
                user_id=user_id,
                username=username,
                role=UserRole(role),
                permissions=permissions
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"Token validation error: {e}")
            return None

    def get_current_user(self, credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[User]:
        """Get current user from token."""
        if not credentials:
            return None

        token_data = self.verify_token(credentials.credentials)
        if not token_data:
            return None

        # In production, fetch user from database
        # For now, return mock user
        return User(
            id=token_data.user_id,
            username=token_data.username,
            email=f"{token_data.username}@example.com",
            role=token_data.role,
            last_login=datetime.now()
        )

    def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        if user.role == UserRole.ADMIN:
            return True

        user_permissions = ROLE_PERMISSIONS.get(user.role, [])
        return permission in user_permissions

    def require_permission(self, permission: str):
        """Dependency for requiring specific permission."""
        def dependency(
            credentials: Optional[HTTPAuthorizationCredentials] = Depends(self.security)
        ) -> User:
            user = self.get_current_user(credentials)
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )

            if not self.check_permission(user, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission}"
                )

            return user

        return dependency

# Global auth service instance
auth_service = AuthService()
```

### Rate Limiting & Abuse Prevention

**File: `backend/app/security/rate_limiting.py` (New)**

```python
"""
Advanced rate limiting and abuse prevention system.
"""

from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Dict, Any, Optional
import time
import redis
from enum import Enum

from ..core.config import settings


class RateLimitTier(Enum):
    """Rate limit tiers based on user role."""
    ADMIN = "admin"
    OPERATOR = "operator"
    ANALYST = "analyst"
    VIEWER = "viewer"
    ANONYMOUS = "anonymous"


class AdvancedLimiter:
    """Advanced rate limiter with tiered limits and burst handling."""

    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_RATE_LIMIT_DB,
            decode_responses=True
        )

        # Rate limit configurations (requests per minute)
        self.tier_limits = {
            RateLimitTier.ADMIN: {"standard": 1000, "burst": 2000},
            RateLimitTier.OPERATOR: {"standard": 500, "burst": 1000},
            RateLimitTier.ANALYST: {"standard": 200, "burst": 400},
            RateLimitTier.VIEWER: {"standard": 100, "burst": 200},
            RateLimitTier.ANONYMOUS: {"standard": 20, "burst": 50}
        }

        # Special limits for expensive operations
        self.expensive_limits = {
            "agent_execute": {"standard": 10, "burst": 20},
            "debate_create": {"standard": 5, "burst": 10},
            "ollama_chat": {"standard": 50, "burst": 100}
        }

    def get_user_tier(self, request: Request) -> RateLimitTier:
        """Determine user tier from request."""
        # Check for authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return RateLimitTier.ANONYMOUS

        # Extract user role from token (simplified)
        # In production, decode JWT and get user role
        try:
            # Mock user tier detection
            user_tier = request.headers.get("X-User-Tier", "viewer")
            return RateLimitTier(user_tier)
        except ValueError:
            return RateLimitTier.VIEWER

    def check_rate_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is within rate limit."""
        current_time = int(time.time())
        window_start = current_time - window

        # Clean old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)

        # Count current requests
        request_count = self.redis_client.zcount(key, window_start, current_time)

        if request_count >= limit:
            return False

        # Add current request
        self.redis_client.zadd(key, {str(current_time): current_time})
        self.redis_client.expire(key, window * 2)  # Keep data for 2 windows

        return True

    def get_remaining_requests(self, key: str, limit: int, window: int = 60) -> int:
        """Get remaining requests in current window."""
        current_time = int(time.time())
        window_start = current_time - window

        request_count = self.redis_client.zcount(key, window_start, current_time)
        return max(0, limit - request_count)

    def get_reset_time(self, key: str, window: int = 60) -> int:
        """Get time until rate limit resets."""
        current_time = int(time.time())
        window_start = current_time - window

        # Get oldest request in current window
        oldest = self.redis_client.zrange(key, 0, 0, withscores=True)
        if oldest:
            return int(oldest[0][1]) + window - current_time
        return window

    def is_rate_limited(self, request: Request, endpoint: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """Check if request should be rate limited."""
        user_tier = self.get_user_tier(request)
        client_ip = get_remote_address(request)

        # Create rate limit key
        base_key = f"ratelimit:{client_ip}:{user_tier.value}"

        # Check endpoint-specific limits
        if endpoint in self.expensive_limits:
            limit_config = self.expensive_limits[endpoint]
        else:
            limit_config = self.tier_limits[user_tier]

        # Check standard limit
        standard_key = f"{base_key}:standard"
        if not self.check_rate_limit(standard_key, limit_config["standard"]):
            remaining = self.get_remaining_requests(standard_key, limit_config["standard"])
            reset_time = self.get_reset_time(standard_key)

            return True, {
                "limit": limit_config["standard"],
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": reset_time
            }

        # Check burst limit (more lenient for short periods)
        burst_key = f"{base_key}:burst"
        if not self.check_rate_limit(burst_key, limit_config["burst"], window=10):
            remaining = self.get_remaining_requests(burst_key, limit_config["burst"], window=10)
            reset_time = self.get_reset_time(burst_key, window=10)

            return True, {
                "limit": limit_config["burst"],
                "remaining": remaining,
                "reset": reset_time,
                "retry_after": reset_time
            }

        return False, None


# Enhanced rate limit exceeded handler
def enhanced_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Enhanced rate limit exceeded handler with detailed response."""
    limiter = AdvancedLimiter()

    # Get rate limit details
    is_limited, details = limiter.is_rate_limited(request, request.url.path)

    response_data = {
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "retry_after": details.get("retry_after", 60) if details else 60,
        "limit": details.get("limit") if details else None,
        "remaining": details.get("remaining", 0) if details else 0,
        "reset": details.get("reset") if details else None
    }

    # Log rate limit violation
    logger.warning(
        "Rate limit exceeded",
        extra={
            "client_ip": get_remote_address(request),
            "endpoint": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("User-Agent"),
            "correlation_id": request.headers.get("X-Correlation-ID")
        }
    )

    return JSONResponse(
        status_code=429,
        content=response_data,
        headers={
            "Retry-After": str(response_data["retry_after"]),
            "X-RateLimit-Limit": str(response_data.get("limit", "")),
            "X-RateLimit-Remaining": str(response_data.get("remaining", 0)),
            "X-RateLimit-Reset": str(response_data.get("reset", 0))
        }
    )


# Global limiter instance
advanced_limiter = AdvancedLimiter()
```

### Input Validation & Sanitization

**File: `backend/app/security/validation.py` (New)**

```python
"""
Comprehensive input validation and sanitization system.
"""

import re
import bleach
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, validator, root_validator
from fastapi import HTTPException
import html
import json


class SecurityValidator:
    """Security-focused input validation and sanitization."""

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'data:',                      # Data URLs (can contain scripts)
        r'vbscript:',                  # VBScript
        r'on\w+\s*=',                  # Event handlers
        r'<\s*iframe[^>]*>.*?</\s*iframe\s*>',  # Iframes
        r'<\s*object[^>]*>.*?</\s*object\s*>',  # Object/embed tags
        r'<\s*embed[^>]*>.*?</\s*embed\s*>',    # Embed tags
        r'union\s+select',             # SQL injection patterns
        r';\s*drop\s+table',           # SQL injection
        r'--',                         # SQL comments
        r'/\*.*?\*/',                  # SQL comments
        r'<\?php',                     # PHP code
        r'<%.*%>',                     # ASP/JSP code
    ]

    # Allowed HTML tags for rich text (very restrictive)
    ALLOWED_HTML_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre'
    ]

    ALLOWED_HTML_ATTRS = {
        '*': ['class'],
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }

    @classmethod
    def sanitize_text(cls, text: str, allow_html: bool = False) -> str:
        """Sanitize text input to prevent XSS and injection attacks."""
        if not isinstance(text, str):
            return str(text)

        # Basic HTML entity encoding
        text = html.escape(text, quote=True)

        if allow_html:
            # Allow limited HTML tags
            text = bleach.clean(
                text,
                tags=cls.ALLOWED_HTML_TAGS,
                attributes=cls.ALLOWED_HTML_ATTRS,
                strip=True
            )
        else:
            # Strip all HTML tags
            text = bleach.clean(text, tags=[], strip=True)

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                raise ValueError(f"Input contains dangerous pattern: {pattern}")

        # Limit length
        if len(text) > 10000:  # 10KB limit
            raise ValueError("Input text too long")

        return text.strip()

    @classmethod
    def sanitize_json(cls, data: Any) -> Any:
        """Recursively sanitize JSON data."""
        if isinstance(data, dict):
            return {
                cls.sanitize_text(k): cls.sanitize_json(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [cls.sanitize_json(item) for item in data]
        elif isinstance(data, str):
            return cls.sanitize_text(data)
        else:
            return data

    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """Validate and sanitize filename."""
        if not filename or len(filename) > 255:
            raise ValueError("Invalid filename length")

        # Remove path traversal attempts
        filename = re.sub(r'[^\w\.-]', '', filename)
        filename = filename.replace('..', '')
        filename = filename.replace('/', '')
        filename = filename.replace('\\', '')

        # Check for dangerous extensions
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
        if any(filename.lower().endswith(ext) for ext in dangerous_extensions):
            raise ValueError("Dangerous file extension not allowed")

        return filename

    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate URL for safety."""
        if not url:
            return url

        # Parse URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)

            # Only allow http/https
            if parsed.scheme not in ['http', 'https']:
                raise ValueError("Only HTTP/HTTPS URLs allowed")

            # Prevent localhost/private IP access
            if parsed.hostname in ['localhost', '127.0.0.1', '::1']:
                raise ValueError("Localhost URLs not allowed")

            # Check for private IP ranges
            import ipaddress
            try:
                ip = ipaddress.ip_address(parsed.hostname)
                if ip.is_private or ip.is_loopback or ip.is_reserved:
                    raise ValueError("Private IP addresses not allowed")
            except ValueError:
                pass  # Not an IP, continue

            return url

        except Exception as e:
            raise ValueError(f"Invalid URL: {e}")

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email address."""
        if not email or len(email) > 254:  # RFC 5321 limit
            raise ValueError("Invalid email length")

        # Basic email regex (simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

        return email.lower().strip()


# Enhanced Pydantic models with security validation
class SecureBaseModel(BaseModel):
    """Base model with security validation."""

    @root_validator(pre=True)
    def validate_and_sanitize(cls, values):
        """Validate and sanitize all input fields."""
        validator = SecurityValidator()

        sanitized = {}
        for field_name, field_value in values.items():
            try:
                # Sanitize based on field type
                if isinstance(field_value, str):
                    sanitized[field_name] = validator.sanitize_text(field_value)
                elif isinstance(field_value, (dict, list)):
                    sanitized[field_name] = validator.sanitize_json(field_value)
                else:
                    sanitized[field_name] = field_value
            except ValueError as e:
                raise ValueError(f"Field '{field_name}': {e}")

        return sanitized

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SecureAgentRequest(SecureBaseModel):
    """Secure agent request model."""
    operation: str
    parameters: Dict[str, Any] = {}

    @validator('operation')
    def validate_operation(cls, v):
        """Validate operation name."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Operation name contains invalid characters')
        if len(v) > 100:
            raise ValueError('Operation name too long')
        return v

    @validator('parameters')
    def validate_parameters(cls, v):
        """Validate parameters for dangerous content."""
        # Check for potentially dangerous parameter keys
        dangerous_keys = ['password', 'token', 'secret', 'key', 'private']
        for key in v.keys():
            if any(dangerous in key.lower() for dangerous in dangerous_keys):
                # Don't log the actual value, just flag it
                raise ValueError(f'Parameter key "{key}" may contain sensitive data')

        # Limit parameter count and size
        if len(v) > 50:
            raise ValueError('Too many parameters')
        return v


class SecureDebateRequest(SecureBaseModel):
    """Secure debate request model."""
    debate_topic: str
    problem_statement: str
    selected_agents: List[str]

    @validator('debate_topic', 'problem_statement')
    def validate_text_length(cls, v):
        """Validate text field lengths."""
        if len(v) > 5000:  # 5KB limit
            raise ValueError('Text content too long')
        if len(v.strip()) < 10:
            raise ValueError('Text content too short')
        return v

    @validator('selected_agents')
    def validate_agents(cls, v):
        """Validate agent selection."""
        if len(v) < 2:
            raise ValueError('At least 2 agents required for debate')
        if len(v) > 9:
            raise ValueError('Maximum 9 agents allowed for debate')

        # Validate agent ID format
        for agent_id in v:
            if not re.match(r'^\d+$', agent_id):
                raise ValueError(f'Invalid agent ID format: {agent_id}')

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError('Duplicate agents not allowed')

        return v


class SecureOllamaRequest(SecureBaseModel):
    """Secure Ollama request model."""
    model: str
    message: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048

    @validator('model')
    def validate_model(cls, v):
        """Validate model name."""
        if not re.match(r'^[a-zA-Z0-9._-]+$', v):
            raise ValueError('Invalid model name format')
        if len(v) > 100:
            raise ValueError('Model name too long')
        return v

    @validator('message')
    def validate_message(cls, v):
        """Validate message content."""
        if len(v) > 50000:  # 50KB limit for messages
            raise ValueError('Message too long')
        return v

    @validator('temperature')
    def validate_temperature(cls, v):
        """Validate temperature parameter."""
        if v is not None and not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v

    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        """Validate max tokens parameter."""
        if v is not None and not 1 <= v <= 8192:
            raise ValueError('Max tokens must be between 1 and 8192')
        return v
```

### Security Headers & CORS

**File: `backend/app/security/headers.py` (New)**

```python
"""
Security headers and CORS configuration.
"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add comprehensive security headers."""

    def __init__(self, app, csp_policy: Optional[str] = None):
        super().__init__(app)
        self.csp_policy = csp_policy or self._get_default_csp()

    def _get_default_csp(self) -> str:
        """Get default Content Security Policy."""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Allow React
            "style-src 'self' 'unsafe-inline'; "  # Allow styled-components
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "  # Allow WebSocket connections
            "media-src 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "upgrade-insecure-requests; "
            "block-all-mixed-content;"
        )

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        # Comprehensive security headers
        headers = {
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": self.csp_policy,

            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",

            # Enable XSS protection
            "X-XSS-Protection": "1; mode=block",

            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",

            # Feature policy (permissions policy)
            "Permissions-Policy": (
                "camera=(), "
                "microphone=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "payment=(), "
                "usb=()"
            ),

            # HSTS (HTTP Strict Transport Security)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",

            # Remove server information
            "Server": "Multi-Agent System",

            # Request timing for security monitoring
            "X-Request-ID": request.headers.get("X-Request-ID", f"req_{int(start_time * 1000)}"),
        }

        # Add response time header
        response_time = int((time.time() - start_time) * 1000)
        headers["X-Response-Time"] = f"{response_time}ms"

        # Add security headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        # Log security events
        if response.status_code >= 400:
            logger.warning(
                "Security event",
                extra={
                    "status_code": response.status_code,
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": self._get_client_ip(request),
                    "user_agent": request.headers.get("User-Agent"),
                    "response_time_ms": response_time
                }
            )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get real client IP address."""
        # Check for forwarded headers (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in case of multiple
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        return request.client.host if request.client else "unknown"


def create_secure_cors_middleware(
    allow_origins: List[str],
    allow_credentials: bool = True,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None,
    max_age: int = 600
) -> CORSMiddleware:
    """Create secure CORS middleware configuration."""

    if allow_methods is None:
        allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

    if allow_headers is None:
        allow_headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Correlation-ID",
            "X-Request-ID"
        ]

    return CORSMiddleware(
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        max_age=max_age
    )


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request size for security."""

    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header
        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_request_size:
                    logger.warning(
                        "Request size limit exceeded",
                        extra={
                            "size": size,
                            "limit": self.max_request_size,
                            "client_ip": request.client.host if request.client else "unknown"
                        }
                    )
                    return Response(
                        status_code=413,
                        content="Request entity too large"
                    )
            except ValueError:
                pass  # Invalid Content-Length, let it pass for now

        response = await call_next(request)
        return response
```

### Audit Logging & Compliance

**File: `backend/app/security/audit.py` (New)**

```python
"""
Comprehensive audit logging and compliance system.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from enum import Enum
import hashlib
import os

from ..core.config import settings


class AuditEventType(Enum):
    """Types of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_OPERATION = "system_operation"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_VIOLATION = "compliance_violation"


class AuditSeverity(Enum):
    """Audit event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLogger:
    """Comprehensive audit logging system."""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "/var/log/agent-system/audit.log"
        self.logger = logging.getLogger("audit")

        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        # Set up audit-specific logger
        self.audit_handler = logging.FileHandler(self.log_file)
        self.audit_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        # Only log to file, not to other handlers
        audit_logger = logging.getLogger("audit")
        audit_logger.addHandler(self.audit_handler)
        audit_logger.setLevel(logging.INFO)

        # Prevent duplicate messages
        audit_logger.propagate = False

    def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        user_id: Optional[str],
        session_id: Optional[str],
        resource_type: str,
        resource_id: Optional[str],
        action: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        client_info: Optional[Dict[str, Any]] = None
    ):
        """Log a comprehensive audit event."""

        # Create audit event
        audit_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "severity": severity.value,
            "correlation_id": correlation_id,
            "user": {
                "id": user_id,
                "session_id": session_id
            },
            "resource": {
                "type": resource_type,
                "id": resource_id
            },
            "action": action,
            "status": status,
            "details": self._sanitize_audit_data(details or {}),
            "client_info": client_info or {},
            "system_info": {
                "hostname": os.uname().nodename if hasattr(os, 'uname') else 'unknown',
                "process_id": os.getpid()
            }
        }

        # Add data integrity hash
        event_json = json.dumps(audit_event, sort_keys=True, default=str)
        audit_event["integrity_hash"] = hashlib.sha256(event_json.encode()).hexdigest()

        # Log the event
        log_message = f"AUDIT: {event_type.value} - {action} - {status}"
        self.logger.info(
            log_message,
            extra={
                "audit_event": audit_event,
                "audit_data": json.dumps(audit_event)
            }
        )

        # For critical events, also log to system log
        if severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
            logging.critical(
                f"CRITICAL AUDIT EVENT: {log_message}",
                extra={"audit_event": audit_event}
            )

    def log_authentication(
        self,
        user_id: str,
        success: bool,
        method: str = "password",
        client_info: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        """Log authentication events."""
        severity = AuditSeverity.HIGH if not success else AuditSeverity.MEDIUM

        self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            severity=severity,
            user_id=user_id,
            resource_type="authentication",
            action="login_attempt",
            status="success" if success else "failure",
            details={"method": method},
            client_info=client_info,
            correlation_id=correlation_id
        )

    def log_authorization(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        allowed: bool,
        client_info: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        """Log authorization events."""
        severity = AuditSeverity.CRITICAL if not allowed else AuditSeverity.LOW

        self.log_event(
            event_type=AuditEventType.AUTHORIZATION,
            severity=severity,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status="allowed" if allowed else "denied",
            client_info=client_info,
            correlation_id=correlation_id
        )

    def log_data_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        query_details: Optional[Dict[str, Any]] = None,
        client_info: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        """Log data access events."""
        self.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            severity=AuditSeverity.MEDIUM,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status="success",
            details={"query": query_details},
            client_info=client_info,
            correlation_id=correlation_id
        )

    def log_security_event(
        self,
        event_type: str,
        severity: AuditSeverity,
        description: str,
        user_id: Optional[str] = None,
        client_info: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security-related events."""
        self.log_event(
            event_type=AuditEventType.SECURITY_EVENT,
            severity=severity,
            user_id=user_id,
            resource_type="security",
            resource_id=event_type,
            action="security_event",
            status="detected",
            details={
                "description": description,
                **(details or {})
            },
            client_info=client_info,
            correlation_id=correlation_id
        )

    @contextmanager
    def audit_context(
        self,
        operation: str,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        **context
    ):
        """Context manager for auditing operations."""
        start_time = datetime.now()

        try:
            yield
            duration = (datetime.now() - start_time).total_seconds()
            self.log_event(
                event_type=AuditEventType.SYSTEM_OPERATION,
                severity=AuditSeverity.LOW,
                user_id=user_id,
                resource_type="system",
                action=operation,
                status="completed",
                details={
                    "duration_seconds": duration,
                    **context
                },
                correlation_id=correlation_id
            )
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.log_event(
                event_type=AuditEventType.SYSTEM_OPERATION,
                severity=AuditSeverity.HIGH,
                user_id=user_id,
                resource_type="system",
                action=operation,
                status="failed",
                details={
                    "duration_seconds": duration,
                    "error": str(e),
                    **context
                },
                correlation_id=correlation_id
            )
            raise

    def _sanitize_audit_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data from audit logs."""
        if not data:
            return data

        sanitized = data.copy()
        sensitive_fields = [
            'password', 'token', 'secret', 'key', 'private',
            'authorization', 'cookie', 'session', 'credit_card'
        ]

        def sanitize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
            for key, value in d.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    d[key] = "***REDACTED***"
                elif isinstance(value, dict):
                    d[key] = sanitize_dict(value)
                elif isinstance(value, list):
                    d[key] = [
                        sanitize_dict(item) if isinstance(item, dict) else item
                        for item in value
                    ]
            return d

        return sanitize_dict(sanitized)

    def query_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query audit logs with filters."""
        # In production, this would query a database
        # For now, return empty list
        return []


# Global audit logger instance
audit_logger = AuditLogger()
```

This comprehensive security implementation provides authentication, authorization, rate limiting, input validation, audit logging, and protection against common web application vulnerabilities.
