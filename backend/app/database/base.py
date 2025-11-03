"""
SQLAlchemy base model for the database.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs

Base = declarative_base()


class TimestampMixin:
    """Mixin to add timestamp fields to models."""
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AsyncBase(AsyncAttrs, Base):
    """Base class for async SQLAlchemy models."""
    
    __abstract__ = True






