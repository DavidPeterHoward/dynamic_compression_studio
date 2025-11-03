"""
Database connection management for the Dynamic Compression Algorithms backend.
"""

import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging

from ..config import settings

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database.async_url,
    echo=settings.api.debug,
    poolclass=QueuePool,
    pool_size=settings.database.pool_size if hasattr(settings.database, 'pool_size') else 20,
    max_overflow=settings.database.max_overflow if hasattr(settings.database, 'max_overflow') else 30,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    connect_args={
        "check_same_thread": False
    } if "sqlite" in settings.database.async_url else {}
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session_optional() -> Optional[AsyncSession]:
    """
    Get an optional database session for background tasks.
    
    Returns:
        Optional[AsyncSession]: Database session or None
    """
    try:
        return AsyncSessionLocal()
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        return None


async def init_db():
    """Initialize database tables."""
    from ..database.base import AsyncBase
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(AsyncBase.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db():
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")


# Event listeners for connection management
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance."""
    if "sqlite" in settings.database.async_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
        cursor.close()


# Dependency for FastAPI
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


# Alias for compatibility
get_db = get_async_db


async def check_db_connection():
    """Check if database connection is working."""
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.fetchone()
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


@event.listens_for(Engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout."""
    if settings.api.debug:
        logger.debug(f"Database connection checked out: {connection_record.info}")


@event.listens_for(Engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    """Log connection checkin."""
    if settings.api.debug:
        logger.debug(f"Database connection checked in: {connection_record.info}")


# Health check function
async def check_db_health() -> dict:
    """
    Check database health and connection status.
    
    Returns:
        dict: Health status information
    """
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1"))
            result.fetchone()
            
        return {
            "status": "healthy",
            "message": "Database connection is working",
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow()
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
            "error": str(e)
        }


# Database statistics
async def get_db_stats() -> dict:
    """
    Get database statistics and performance metrics.
    
    Returns:
        dict: Database statistics
    """
    try:
        async with AsyncSessionLocal() as session:
            # Get table row counts
            tables = [
                "algorithms", "experiments", "system_metrics", 
                "sensors", "sensor_readings", "sensor_fusion"
            ]
            stats = {}
            
            for table in tables:
                try:
                    from sqlalchemy import text
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    stats[f"{table}_count"] = count
                except Exception as e:
                    logger.warning(f"Could not get count for table {table}: {e}")
                    stats[f"{table}_count"] = 0
            
            # Add connection pool stats
            stats.update({
                "pool_size": engine.pool.size(),
                "pool_checked_in": engine.pool.checkedin(),
                "pool_checked_out": engine.pool.checkedout(),
                "pool_overflow": engine.pool.overflow()
            })
            
            return stats
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {"error": str(e)}


# Migration helper
async def run_migrations():
    """Run database migrations."""
    try:
        # This would typically use Alembic
        # For now, we'll just create tables
        await init_db()
        logger.info("Database migrations completed")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


# Backup helper
async def create_backup(backup_path: str):
    """
    Create database backup.
    
    Args:
        backup_path: Path to save backup
    """
    try:
        if "sqlite" in settings.database.async_url:
            # For SQLite, just copy the file
            import shutil
            import os
            
            db_path = settings.database.async_url.replace("sqlite+aiosqlite:///", "")
            if os.path.exists(db_path):
                shutil.copy2(db_path, backup_path)
                logger.info(f"SQLite backup created: {backup_path}")
            else:
                logger.warning(f"Database file not found: {db_path}")
        else:
            # For PostgreSQL, use pg_dump
            import subprocess
            
            cmd = [
                "pg_dump",
                f"--host={settings.database.host}",
                f"--port={settings.database.port}",
                f"--username={settings.database.username}",
                f"--dbname={settings.database.database}",
                f"--file={backup_path}"
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = settings.database.password
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"PostgreSQL backup created: {backup_path}")
            else:
                logger.error(f"PostgreSQL backup failed: {result.stderr}")
                raise Exception(f"Backup failed: {result.stderr}")
                
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        raise






