"""
Pydantic models for user-related data structures.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime


class UserRole(str, Enum):
    """User roles in the system."""
    
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    ANALYST = "analyst"
    DEVELOPER = "developer"


class UserStatus(str, Enum):
    """User account status."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class User(BaseModel):
    """Model for user information."""
    
    id: str = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(default=None, description="Full name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")
    
    # Profile information
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")
    bio: Optional[str] = Field(default=None, description="User biography")
    location: Optional[str] = Field(default=None, description="User location")
    website: Optional[str] = Field(default=None, description="Website URL")
    
    # Preferences
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    settings: Dict[str, Any] = Field(default_factory=dict, description="User settings")
    
    # Statistics
    total_compressions: int = Field(default=0, description="Total number of compressions")
    total_files: int = Field(default=0, description="Total number of files uploaded")
    storage_used: int = Field(default=0, description="Storage used in bytes")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    last_login: Optional[datetime] = Field(default=None, description="Last login time")
    
    # Verification
    email_verified: bool = Field(default=False, description="Whether email is verified")
    two_factor_enabled: bool = Field(default=False, description="Whether 2FA is enabled")
    
    @validator('username')
    def validate_username(cls, v):
        if not v or len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v


class UserCreate(BaseModel):
    """Model for user creation requests."""
    
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    full_name: Optional[str] = Field(default=None, description="Full name")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    
    # Optional profile information
    bio: Optional[str] = Field(default=None, description="User biography")
    location: Optional[str] = Field(default=None, description="User location")
    website: Optional[str] = Field(default=None, description="Website URL")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Model for user update requests."""
    
    email: Optional[EmailStr] = Field(default=None, description="New email address")
    username: Optional[str] = Field(default=None, description="New username")
    full_name: Optional[str] = Field(default=None, description="New full name")
    role: Optional[UserRole] = Field(default=None, description="New user role")
    status: Optional[UserStatus] = Field(default=None, description="New user status")
    
    # Profile information
    avatar_url: Optional[str] = Field(default=None, description="New avatar URL")
    bio: Optional[str] = Field(default=None, description="New biography")
    location: Optional[str] = Field(default=None, description="New location")
    website: Optional[str] = Field(default=None, description="New website URL")
    
    # Preferences and settings
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="New preferences")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="New settings")
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if len(v) < 3 or len(v) > 50:
                raise ValueError('Username must be between 3 and 50 characters')
            if not v.replace('_', '').replace('-', '').isalnum():
                raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v


class UserLogin(BaseModel):
    """Model for user login requests."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(default=False, description="Whether to remember the user")
    two_factor_code: Optional[str] = Field(default=None, description="Two-factor authentication code")


class UserPasswordChange(BaseModel):
    """Model for password change requests."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def validate_confirm_password(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserProfile(BaseModel):
    """Model for user profile information."""
    
    user: User = Field(..., description="User information")
    
    # Extended profile information
    social_links: Dict[str, str] = Field(default_factory=dict, description="Social media links")
    skills: List[str] = Field(default_factory=list, description="User skills")
    interests: List[str] = Field(default_factory=list, description="User interests")
    
    # Activity information
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent activity")
    achievements: List[Dict[str, Any]] = Field(default_factory=list, description="User achievements")
    
    # Privacy settings
    profile_public: bool = Field(default=True, description="Whether profile is public")
    show_email: bool = Field(default=False, description="Whether to show email publicly")
    show_activity: bool = Field(default=True, description="Whether to show activity publicly")


class UserStats(BaseModel):
    """Model for user statistics."""
    
    user_id: str = Field(..., description="User identifier")
    
    # Compression statistics
    total_compressions: int = Field(..., description="Total number of compressions")
    successful_compressions: int = Field(..., description="Number of successful compressions")
    failed_compressions: int = Field(..., description="Number of failed compressions")
    average_compression_ratio: float = Field(..., description="Average compression ratio")
    
    # File statistics
    total_files: int = Field(..., description="Total number of files")
    total_file_size: int = Field(..., description="Total file size in bytes")
    average_file_size: float = Field(..., description="Average file size")
    
    # Usage statistics
    total_storage_used: int = Field(..., description="Total storage used in bytes")
    storage_limit: int = Field(..., description="Storage limit in bytes")
    storage_usage_percentage: float = Field(..., description="Storage usage percentage")
    
    # Time-based statistics
    compressions_today: int = Field(..., description="Compressions performed today")
    compressions_this_week: int = Field(..., description="Compressions performed this week")
    compressions_this_month: int = Field(..., description="Compressions performed this month")
    
    # Algorithm preferences
    favorite_algorithms: List[str] = Field(default_factory=list, description="Most used algorithms")
    algorithm_performance: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, 
        description="Performance by algorithm"
    )
    
    # Timestamps
    last_activity: Optional[datetime] = Field(default=None, description="Last activity time")
    stats_updated: datetime = Field(default_factory=datetime.utcnow, description="When stats were updated")


class UserListResponse(BaseModel):
    """Response model for user listing."""
    
    users: List[User] = Field(..., description="List of users")
    total_count: int = Field(..., description="Total number of users")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=20, description="Page size")
    total_pages: int = Field(..., description="Total number of pages")
    
    @validator('total_pages')
    def calculate_total_pages(cls, v, values):
        if 'total_count' in values and 'page_size' in values:
            return (values['total_count'] + values['page_size'] - 1) // values['page_size']
        return v


class UserSearchRequest(BaseModel):
    """Request model for user search."""
    
    query: Optional[str] = Field(default=None, description="Search query")
    role: Optional[UserRole] = Field(default=None, description="Filter by role")
    status: Optional[UserStatus] = Field(default=None, description="Filter by status")
    email_verified: Optional[bool] = Field(default=None, description="Filter by email verification")
    
    # Date filters
    created_after: Optional[datetime] = Field(default=None, description="Filter users created after date")
    created_before: Optional[datetime] = Field(default=None, description="Filter users created before date")
    last_login_after: Optional[datetime] = Field(default=None, description="Filter users who logged in after date")
    
    # Pagination
    page: int = Field(default=1, description="Page number")
    page_size: int = Field(default=20, description="Page size")
    
    # Sorting
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", description="Sort order (asc/desc)")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be at least 1')
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Page size must be between 1 and 100')
        return v






