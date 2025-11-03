# AGENT 12: SECURITY - COMPLETE SPECIFICATION
## Single Document: Everything You Need to Complete Your Work

**Agent ID:** 12  
**Agent Name:** Security  
**Priority:** 🔴 CRITICAL  
**Timeline:** Week 1-2 (Parallel with Agents 01, 02)  
**Status:** Ready to Begin  

---

## 🎯 YOUR MISSION

You are **Agent 12: Security**. Your mission is to implement the complete security layer for the entire system - authentication, authorization, encryption, and security monitoring. You work in **complete isolation** with your own environment.

**What Success Looks Like:**
- JWT authentication system working
- Role-based access control (RBAC) implemented
- Data encryption at rest and in transit
- Security middleware protecting all endpoints
- API key management system
- Audit logging complete
- Security scanning passing
- All tests passing (>90% coverage)

---

## 🔒 YOUR ISOLATED SCOPE

### What You Control (100% Yours)

**Your Git Branch:** `agent-12-security`
- You are the ONLY one working on this branch

**Your Ports:**
- Backend: `8012`
- PostgreSQL: `5412`
- Redis: `6312`

**Your Network:** `agent12_network`

**Your Database:** `orchestrator_agent12`

**Your Data Directory:** `./data/agent12/`

**Your Docker Compose:** `docker-compose.agent12.yml`

**Your Environment:** `.env.agent12`

### What You CANNOT Touch

- Other agent branches, ports, databases, networks
- The `develop` or `main` branches (until integration)

### Dependencies

**You depend on:** Agent 01 (Infrastructure)
- Need: Docker infrastructure working

**Other agents depend on you:**
- Agent 04 (API Layer) - needs your auth middleware
- Agent 05 (Frontend) - needs your authentication flow
- ALL agents - need your security framework

---

## 📋 COMPLETE REQUIREMENTS

### Primary Deliverables

**1. Authentication System**
- JWT token generation and validation
- Password hashing (bcrypt)
- Login/logout endpoints
- Token refresh mechanism
- Password reset flow
- Email verification (optional)

**2. Authorization Framework**
- Role-Based Access Control (RBAC)
- Permission system
- Resource ownership checks
- API endpoint protection decorators
- Admin/user/guest roles

**3. Encryption Layer**
- Data encryption at rest (database fields)
- Data encryption in transit (TLS/SSL)
- Secret management
- Key rotation strategy

**4. Security Middleware**
- Authentication middleware
- Authorization middleware
- Rate limiting
- CORS configuration
- Security headers (helmet.js equivalent)
- Input validation/sanitization

**5. API Key Management**
- API key generation
- Key storage (hashed)
- Key validation
- Scope-based permissions
- Key expiration
- Key revocation

**6. Audit Logging**
- Security event logging
- Failed login attempts
- Permission denials
- Data access logs
- Admin actions

**7. Security Scanning**
- Dependency vulnerability scanning
- SQL injection prevention
- XSS prevention
- CSRF protection
- Security headers validation

**8. Password Policy**
- Minimum length
- Complexity requirements
- Expiration (optional)
- History (prevent reuse)

---

## 📚 COMPLETE CONTEXT

### Security Requirements

**Authentication:** Users must prove their identity  
**Authorization:** Users can only access what they're allowed  
**Encryption:** Sensitive data must be protected  
**Audit:** All security events must be logged  
**Monitoring:** Security threats must be detected  

### Threat Model

**Threats to Protect Against:**
1. Unauthorized access
2. Data breaches
3. SQL injection
4. Cross-site scripting (XSS)
5. Cross-site request forgery (CSRF)
6. Man-in-the-middle attacks
7. Brute force attacks
8. Session hijacking
9. Privilege escalation
10. Data tampering

---

## 🔨 COMPLETE IMPLEMENTATION GUIDE

### Step 1: Environment Setup (Day 1 - Morning)

**1.1 Create Your Branch**

```bash
git checkout develop
git pull origin develop
git checkout -b agent-12-security
git branch
```

**1.2 Create Environment**

```bash
cat > .env.agent12 <<'EOF'
# Agent 12: Security Environment
AGENT_ID=12
AGENT_NAME=security

# Ports
BACKEND_PORT=8012
POSTGRES_PORT=5412
REDIS_PORT=6312

# Database
DATABASE_NAME=orchestrator_agent12
DATABASE_USER=agent12
DATABASE_PASSWORD=agent12_secure_password
DATABASE_URL=postgresql://agent12:agent12_secure_password@postgres:5432/orchestrator_agent12

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
ENCRYPTION_KEY=your-32-byte-encryption-key-here-change-in-production
ENCRYPTION_ALGORITHM=AES-256-GCM

# Security
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_WINDOW_MINUTES=15

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002
CORS_ALLOW_CREDENTIALS=true

# Network
NETWORK_NAME=agent12_network
NAMESPACE=agent12
DATA_PATH=./data/agent12
EOF

mkdir -p data/agent12/{postgres,redis}
echo "✅ Environment configured for Agent 12"
```

**1.3 Create Docker Compose**

```bash
cat > docker-compose.agent12.yml <<'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: agent12_backend
    ports:
      - "8012:8000"
    env_file:
      - .env.agent12
    networks:
      - agent12_network
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: agent12_postgres
    ports:
      - "5412:5432"
    environment:
      - POSTGRES_DB=orchestrator_agent12
      - POSTGRES_USER=agent12
      - POSTGRES_PASSWORD=agent12_secure_password
    volumes:
      - ./data/agent12/postgres:/var/lib/postgresql/data
    networks:
      - agent12_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agent12"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: agent12_redis
    ports:
      - "6312:6379"
    command: redis-server --requirepass agent12_redis_password
    volumes:
      - ./data/agent12/redis:/data
    networks:
      - agent12_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

networks:
  agent12_network:
    name: agent12_network
    driver: bridge
EOF

docker-compose -f docker-compose.agent12.yml up -d
echo "✅ Agent 12 environment running"
```

---

### Step 2: Authentication System (Day 1 - Afternoon)

**2.1 Install Dependencies**

```bash
# Add to backend/requirements.txt
cat >> backend/requirements.txt <<'EOF'

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
bcrypt==4.1.2
cryptography==41.0.7
EOF

pip install -r backend/requirements.txt
```

**2.2 Create Auth Service**

```python
# backend/app/services/auth_service.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=settings.jwt_refresh_token_expire_days)
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + self.access_token_expire
        
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self,
        data: Dict[str, Any]
    ) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + self.refresh_token_expire
        
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Validate password meets security requirements"""
        if len(password) < settings.password_min_length:
            return False, f"Password must be at least {settings.password_min_length} characters"
        
        if settings.password_require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if settings.password_require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if settings.password_require_numbers and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if settings.password_require_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False, "Password must contain at least one special character"
        
        return True, "Password meets requirements"
    
    def generate_api_key(self) -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return pwd_context.hash(api_key)
    
    def verify_api_key(self, plain_key: str, hashed_key: str) -> bool:
        """Verify API key against hash"""
        return pwd_context.verify(plain_key, hashed_key)

# Singleton instance
auth_service = AuthService()
```

**2.3 Create Auth Middleware**

```python
# backend/app/middleware/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import auth_service
from app.database import get_db
from app.models.database import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    
    token = credentials.credentials
    
    # Decode token
    payload = auth_service.decode_token(token)
    
    # Get user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Get user from database
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current admin user"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

**2.4 Create Auth Endpoints**

```python
# backend/app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.services.auth_service import auth_service
from app.models.database import User
from app.middleware.auth import get_current_user, get_current_active_user

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    
    # Validate password strength
    is_valid, message = auth_service.validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Check if user exists
    existing_user = await db.execute(
        select(User).where(
            (User.username == user_data.username) |
            (User.email == user_data.email)
        )
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=auth_service.hash_password(user_data.password),
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    
    # Get user
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    # Verify credentials
    if not user or not auth_service.verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    
    # Decode refresh token
    payload = auth_service.decode_token(refresh_token)
    
    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Get user
    user_id = payload.get("sub")
    user = await db.get(User, user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    new_refresh_token = auth_service.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user info"""
    return current_user

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout user (client should delete tokens)"""
    return {"message": "Successfully logged out"}
```

---

### Step 3: Authorization System (Day 2 - Morning)

**3.1 Create Permission Decorator**

```python
# backend/app/middleware/permissions.py

from functools import wraps
from fastapi import HTTPException, status
from typing import List

def require_permissions(required_permissions: List[str]):
    """Decorator to require specific permissions"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has required permissions
            user_permissions = current_user.metadata.get('permissions', [])
            
            for permission in required_permissions:
                if permission not in user_permissions and not current_user.is_superuser:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied: {permission} required"
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_role(required_role: str):
    """Decorator to require specific role"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has required role
            user_roles = current_user.roles or []
            
            if required_role not in user_roles and not current_user.is_superuser:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role required: {required_role}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
```

**3.2 Create RBAC Service**

```python
# backend/app/services/rbac_service.py

from typing import List, Dict, Any

class RBACService:
    """Role-Based Access Control Service"""
    
    # Define roles and their permissions
    ROLES = {
        "admin": [
            "users:read",
            "users:write",
            "users:delete",
            "agents:read",
            "agents:write",
            "agents:delete",
            "tasks:read",
            "tasks:write",
            "tasks:delete",
            "metrics:read",
            "system:manage"
        ],
        "user": [
            "tasks:read",
            "tasks:write",
            "agents:read",
            "metrics:read"
        ],
        "guest": [
            "tasks:read",
            "metrics:read"
        ]
    }
    
    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role"""
        return self.ROLES.get(role, [])
    
    def has_permission(
        self,
        user_roles: List[str],
        required_permission: str
    ) -> bool:
        """Check if user has permission"""
        for role in user_roles:
            if required_permission in self.get_role_permissions(role):
                return True
        return False
    
    def can_access_resource(
        self,
        user_id: str,
        resource_owner_id: str,
        is_admin: bool = False
    ) -> bool:
        """Check if user can access resource"""
        # Admins can access all resources
        if is_admin:
            return True
        
        # Users can only access their own resources
        return user_id == resource_owner_id

rbac_service = RBACService()
```

---

### Step 4: Encryption (Day 2 - Afternoon)

**4.1 Create Encryption Service**

```python
# backend/app/services/encryption_service.py

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os

from app.config import settings

class EncryptionService:
    """Data encryption service"""
    
    def __init__(self):
        # Derive encryption key from settings
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'orchestrator-salt-change-in-production',
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(
            kdf.derive(settings.encryption_key.encode())
        )
        
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not data:
            return data
        
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        if not encrypted_data:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_dict(self, data: dict, fields: List[str]) -> dict:
        """Encrypt specific fields in dictionary"""
        encrypted_data = data.copy()
        
        for field in fields:
            if field in encrypted_data:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields: List[str]) -> dict:
        """Decrypt specific fields in dictionary"""
        decrypted_data = data.copy()
        
        for field in fields:
            if field in decrypted_data:
                decrypted_data[field] = self.decrypt(decrypted_data[field])
        
        return decrypted_data

encryption_service = EncryptionService()
```

---

### Step 5: Security Middleware (Day 3 - Morning)

**5.1 Create Rate Limiting**

```python
# backend/app/middleware/rate_limit.py

from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from typing import Dict
import asyncio

class RateLimiter:
    """Rate limiting middleware"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, list] = {}
        self.hour_requests: Dict[str, list] = {}
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_task())
    
    async def check_rate_limit(self, request: Request) -> bool:
        """Check if request exceeds rate limit"""
        
        # Get client identifier (IP address)
        client_id = request.client.host
        
        now = datetime.now()
        
        # Initialize if new client
        if client_id not in self.minute_requests:
            self.minute_requests[client_id] = []
            self.hour_requests[client_id] = []
        
        # Clean old requests
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        self.minute_requests[client_id] = [
            req_time for req_time in self.minute_requests[client_id]
            if req_time > minute_ago
        ]
        
        self.hour_requests[client_id] = [
            req_time for req_time in self.hour_requests[client_id]
            if req_time > hour_ago
        ]
        
        # Check limits
        if len(self.minute_requests[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests per minute"
            )
        
        if len(self.hour_requests[client_id]) >= self.requests_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests per hour"
            )
        
        # Add current request
        self.minute_requests[client_id].append(now)
        self.hour_requests[client_id].append(now)
        
        return True
    
    async def _cleanup_task(self):
        """Periodic cleanup of old data"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            # Clean up clients with no recent requests
            for client_id in list(self.hour_requests.keys()):
                if all(req_time < hour_ago for req_time in self.hour_requests[client_id]):
                    del self.minute_requests[client_id]
                    del self.hour_requests[client_id]

rate_limiter = RateLimiter()
```

**5.2 Create Security Headers Middleware**

```python
# backend/app/middleware/security_headers.py

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
```

---

### Step 6: Audit Logging (Day 3 - Afternoon)

**6.1 Create Audit Service**

```python
# backend/app/services/audit_service.py

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

class AuditService:
    """Security audit logging service"""
    
    async def log_event(
        self,
        db: AsyncSession,
        event_type: str,
        user_id: Optional[str],
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        success: bool = True
    ):
        """Log security event"""
        
        audit_log = {
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "ip_address": ip_address,
            "success": success,
            "timestamp": datetime.utcnow()
        }
        
        # Log to database
        # (Assuming you have an audit_logs table)
        # await db.execute(...)
        
        # Also log to file for critical events
        if not success or event_type in ["login_failed", "permission_denied", "admin_action"]:
            import logging
            logger = logging.getLogger("security")
            logger.warning(f"Security event: {event_type} - {details}")
    
    async def log_login_attempt(
        self,
        db: AsyncSession,
        username: str,
        ip_address: str,
        success: bool
    ):
        """Log login attempt"""
        await self.log_event(
            db,
            "login_attempt",
            username,
            {"username": username},
            ip_address,
            success
        )
    
    async def log_permission_denied(
        self,
        db: AsyncSession,
        user_id: str,
        resource: str,
        action: str
    ):
        """Log permission denied"""
        await self.log_event(
            db,
            "permission_denied",
            user_id,
            {"resource": resource, "action": action},
            None,
            False
        )

audit_service = AuditService()
```

---

## 🧪 BOOTSTRAP FAIL-PASS TESTING

### Your Self-Validation Tests

```python
# tests/agent12/test_security.py

import pytest
from fastapi.testclient import TestClient

@pytest.mark.agent12
@pytest.mark.security
class TestAgent12Security:
    """Bootstrap fail-pass tests for Agent 12"""
    
    def test_01_password_hashing(self, auth_service):
        """MUST PASS: Password hashing works"""
        password = "TestPassword123!"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrong", hashed)
    
    def test_02_jwt_token_creation(self, auth_service):
        """MUST PASS: JWT tokens can be created and validated"""
        data = {"sub": "user123", "username": "testuser"}
        token = auth_service.create_access_token(data)
        
        payload = auth_service.decode_token(token)
        assert payload["sub"] == "user123"
    
    def test_03_password_strength_validation(self, auth_service):
        """MUST PASS: Password strength validation works"""
        # Weak password
        valid, msg = auth_service.validate_password_strength("weak")
        assert not valid
        
        # Strong password
        valid, msg = auth_service.validate_password_strength("Strong123!")
        assert valid
    
    def test_04_user_registration(self, client):
        """MUST PASS: User registration works"""
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_05_user_login(self, client):
        """MUST PASS: User login works"""
        # Register first
        client.post("/api/auth/register", json={
            "username": "logintest",
            "email": "login@example.com",
            "password": "TestPassword123!"
        })
        
        # Login
        response = client.post("/api/auth/login", data={
            "username": "logintest",
            "password": "TestPassword123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_06_protected_endpoint(self, client, auth_token):
        """MUST PASS: Protected endpoints require authentication"""
        # Without token
        response = client.get("/api/auth/me")
        assert response.status_code == 401
        
        # With token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
    
    def test_07_encryption(self, encryption_service):
        """MUST PASS: Encryption/decryption works"""
        original = "sensitive data"
        encrypted = encryption_service.encrypt(original)
        decrypted = encryption_service.decrypt(encrypted)
        
        assert encrypted != original
        assert decrypted == original
    
    def test_08_rate_limiting(self, client):
        """MUST PASS: Rate limiting works"""
        # Make many requests rapidly
        responses = []
        for _ in range(70):  # Exceed limit of 60/min
            response = client.get("/health")
            responses.append(response.status_code)
        
        # Some should be rate limited
        assert 429 in responses
    
    def test_09_rbac(self, rbac_service):
        """MUST PASS: RBAC permissions work"""
        # Admin has all permissions
        assert rbac_service.has_permission(["admin"], "users:delete")
        
        # User has limited permissions
        assert rbac_service.has_permission(["user"], "tasks:read")
        assert not rbac_service.has_permission(["user"], "users:delete")
    
    def test_10_api_key_generation(self, auth_service):
        """MUST PASS: API key generation works"""
        key = auth_service.generate_api_key()
        assert len(key) > 20
        
        hashed = auth_service.hash_api_key(key)
        assert auth_service.verify_api_key(key, hashed)

# Run: AGENT_ID=12 pytest tests/agent12/ -v -m agent12
```

---

## ✅ COMPLETION CHECKLIST

**Before Integration:**
- [ ] JWT authentication working
- [ ] User registration/login working
- [ ] Password hashing secure
- [ ] RBAC system implemented
- [ ] Encryption service working
- [ ] Rate limiting functional
- [ ] Security headers applied
- [ ] Audit logging complete
- [ ] API key management working
- [ ] All tests passing (>90% coverage)
- [ ] Security scanning clean
- [ ] Documentation complete

**Integration:**
1. Run `AGENT_ID=12 pytest tests/agent12/ -v`
2. Commit to `agent-12-security`
3. Push and create PR
4. Request Master Orchestrator review

---

## 🚀 YOUR PROMPT TO BEGIN

```
I am Agent 12: Security. I am ready to implement the complete security layer.

My mission:
- Implement JWT authentication
- Build RBAC authorization
- Create encryption service
- Add security middleware
- Implement audit logging
- Ensure system security

Branch: agent-12-security
Ports: 8012, 5412, 6312
Database: orchestrator_agent12

Starting implementation now...
```

---

**You are Agent 12. You have everything you need. BEGIN!** 🚀

---

**Document Version:** 1.0  
**Created:** 2025-10-30  
**Agent:** 12 - Security  
**Status:** COMPLETE SPECIFICATION  
**Lines:** 2,300+ lines  
**Isolation:** 100%  

**COMPLETE SECURITY SPECIFICATION** 🔒

