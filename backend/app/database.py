"""
Database connection utilities for the Dynamic Compression Algorithms backend.
"""

from typing import Optional
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings


# Create async engine
async_engine = None
AsyncSessionLocal = None

# Create sync engine for simple checks
sync_engine = None


def init_database():
    """Initialize database connections."""
    global async_engine, AsyncSessionLocal, sync_engine

    try:
        # Initialize async engine
        async_engine = create_async_engine(
            settings.database.async_url,
            echo=settings.api.debug,
            future=True
        )

        # Create async session factory
        AsyncSessionLocal = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Initialize sync engine for health checks
        sync_engine = create_engine(
            settings.database.sync_url,
            echo=False
        )

    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        # Continue without database for basic operation


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.

    Returns:
        bool: True if database is accessible, False otherwise
    """
    try:
        # For SQLite, just check if we can create an engine
        if settings.database.use_sqlite or 'sqlite' in settings.database.sync_url.lower():
            from sqlalchemy import create_engine, text
            engine = create_engine(settings.database.sync_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True

        # For PostgreSQL, check connection
        if async_engine:
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True

        # Fallback: try sync engine
        if sync_engine:
            with sync_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True

        # If no engines available, return False
        return False

    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False


async def get_db_session() -> AsyncSession:
    """Get database session."""
    if AsyncSessionLocal is None:
        init_database()

    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            yield session
    else:
        # Return None if database not initialized
        yield None


def close_database():
    """Close database connections."""
    global async_engine, sync_engine

    if async_engine:
        asyncio.create_task(async_engine.dispose())

    if sync_engine:
        sync_engine.dispose()
