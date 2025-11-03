"""
Pydantic models for file-related data structures.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
import os


class FileType(str, Enum):
    """Supported file types."""
    
    # Text files
    TXT = "txt"
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    YML = "yml"
    TOML = "toml"
    INI = "ini"
    CFG = "cfg"
    CONF = "conf"
    
    # Code files
    PY = "py"
    JS = "js"
    TS = "ts"
    HTML = "html"
    CSS = "css"
    MD = "md"
    SQL = "sql"
    LOG = "log"
    
    # Binary files
    BIN = "bin"
    DAT = "dat"
    
    # Archives
    ZIP = "zip"
    TAR = "tar"
    GZ = "gz"
    BZ2 = "bz2"
    XZ = "xz"
    
    # Other
    UNKNOWN = "unknown"


class FileStatus(str, Enum):
    """File processing status."""
    
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPRESSED = "compressed"
    ERROR = "error"
    DELETED = "deleted"


class FileUpload(BaseModel):
    """Model for file upload requests."""
    
    filename: str = Field(..., description="Original filename")
    content_type: Optional[str] = Field(default=None, description="MIME type")
    size: int = Field(..., description="File size in bytes")
    checksum: Optional[str] = Field(default=None, description="File checksum")
    
    # Optional metadata
    description: Optional[str] = Field(default=None, description="File description")
    tags: Optional[List[str]] = Field(default=None, description="File tags")
    
    @validator('size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('File size must be positive')
        if v > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError('File size exceeds maximum limit of 100MB')
        return v
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or len(v) > 255:
            raise ValueError('Filename must be between 1 and 255 characters')
        return v


class FileInfo(BaseModel):
    """Model for file information."""
    
    id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    file_type: FileType = Field(..., description="File type")
    size: int = Field(..., description="File size in bytes")
    content_type: Optional[str] = Field(default=None, description="MIME type")
    checksum: Optional[str] = Field(default=None, description="File checksum")
    
    # Status and metadata
    status: FileStatus = Field(default=FileStatus.UPLOADED, description="File status")
    upload_time: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    last_modified: Optional[datetime] = Field(default=None, description="Last modification time")
    
    # Storage information
    storage_path: Optional[str] = Field(default=None, description="Storage path")
    storage_size: Optional[int] = Field(default=None, description="Storage size")
    
    # Optional metadata
    description: Optional[str] = Field(default=None, description="File description")
    tags: Optional[List[str]] = Field(default=None, description="File tags")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @property
    def extension(self) -> str:
        """Get file extension."""
        return os.path.splitext(self.filename)[1].lower().lstrip('.')
    
    @property
    def name_without_extension(self) -> str:
        """Get filename without extension."""
        return os.path.splitext(self.filename)[0]


class FileMetadata(BaseModel):
    """Model for file metadata analysis."""
    
    file_id: str = Field(..., description="File identifier")
    
    # Content analysis
    content_type: Optional[str] = Field(default=None, description="Detected content type")
    language: Optional[str] = Field(default=None, description="Detected language")
    encoding: Optional[str] = Field(default=None, description="File encoding")
    
    # Statistical information
    line_count: Optional[int] = Field(default=None, description="Number of lines")
    word_count: Optional[int] = Field(default=None, description="Number of words")
    character_count: Optional[int] = Field(default=None, description="Number of characters")
    
    # Compression analysis
    entropy: Optional[float] = Field(default=None, description="Shannon entropy")
    compression_potential: Optional[float] = Field(default=None, description="Estimated compression potential")
    redundancy_ratio: Optional[float] = Field(default=None, description="Redundancy ratio")
    
    # Pattern analysis
    patterns: Optional[List[str]] = Field(default=None, description="Detected patterns")
    pattern_frequency: Optional[Dict[str, int]] = Field(default=None, description="Pattern frequencies")
    
    # Quality metrics
    quality_score: Optional[float] = Field(default=None, description="Overall quality score")
    complexity_score: Optional[float] = Field(default=None, description="Complexity score")
    
    # Timestamps
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    # Additional data
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional analysis data")


class FileListResponse(BaseModel):
    """Response model for file listing."""
    
    files: List[FileInfo] = Field(..., description="List of files")
    total_count: int = Field(..., description="Total number of files")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=20, description="Page size")
    total_pages: int = Field(..., description="Total number of pages")
    
    @validator('total_pages')
    def calculate_total_pages(cls, v, values):
        if 'total_count' in values and 'page_size' in values:
            return (values['total_count'] + values['page_size'] - 1) // values['page_size']
        return v


class FileSearchRequest(BaseModel):
    """Request model for file search."""
    
    query: Optional[str] = Field(default=None, description="Search query")
    file_type: Optional[FileType] = Field(default=None, description="Filter by file type")
    status: Optional[FileStatus] = Field(default=None, description="Filter by status")
    min_size: Optional[int] = Field(default=None, description="Minimum file size")
    max_size: Optional[int] = Field(default=None, description="Maximum file size")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    date_from: Optional[datetime] = Field(default=None, description="Filter from date")
    date_to: Optional[datetime] = Field(default=None, description="Filter to date")
    
    # Pagination
    page: int = Field(default=1, description="Page number")
    page_size: int = Field(default=20, description="Page size")
    
    # Sorting
    sort_by: Optional[str] = Field(default="upload_time", description="Sort field")
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


class FileDeleteRequest(BaseModel):
    """Request model for file deletion."""
    
    file_id: str = Field(..., description="File identifier to delete")
    force: bool = Field(default=False, description="Force deletion even if file is in use")


class FileUpdateRequest(BaseModel):
    """Request model for file updates."""
    
    filename: Optional[str] = Field(default=None, description="New filename")
    description: Optional[str] = Field(default=None, description="New description")
    tags: Optional[List[str]] = Field(default=None, description="New tags")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="New metadata")
    
    @validator('filename')
    def validate_filename(cls, v):
        if v is not None and (not v or len(v) > 255):
            raise ValueError('Filename must be between 1 and 255 characters')
        return v






