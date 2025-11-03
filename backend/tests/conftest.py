"""
Pytest configuration and fixtures.

Provides common fixtures for all tests including:
- Database setup/teardown
- Test client
- Mock Ollama service
- Test data fixtures
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Import app components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import Base, get_db_session
from app.main import app


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create test database for each test function.
    
    Uses in-memory SQLite for speed.
    Tears down after each test for isolation.
    """
    # Create engine
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create test client with database dependency override.
    
    Overrides the get_db dependency to use test database.
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def ollama_models():
    """
    Fixture providing available Ollama models.
    
    Returns actual models from Ollama instance.
    """
    return [
        {
            "name": "magistral:24b",
            "parameter_size": "23.6B",
            "purpose": "complex_reasoning"
        },
        {
            "name": "llama3.1:8b",
            "parameter_size": "8.0B",
            "purpose": "general"
        },
        {
            "name": "qwen2.5-coder:1.5b-base",
            "parameter_size": "1.5B",
            "purpose": "code_generation"
        },
        {
            "name": "deepseek-coder-v2:latest",
            "parameter_size": "15.7B",
            "purpose": "advanced_code"
        }
    ]


@pytest.fixture(scope="function")
def mock_ollama_response():
    """
    Mock Ollama API responses for testing without actual model calls.
    """
    return {
        "model": "llama3.1:8b",
        "created_at": "2025-10-30T12:00:00Z",
        "response": "This is a test response from the mock Ollama service.",
        "done": True
    }


@pytest.fixture(scope="function")
def sample_compression_data():
    """
    Sample data for compression testing.
    """
    return {
        "text": "This is sample text content " * 100,  # Repetitive for good compression
        "json": '{"key": "value", "array": [1, 2, 3, 4, 5]}',
        "random": os.urandom(1024),  # Random data (poor compression)
        "structured": "Row 1: Value A\nRow 2: Value B\n" * 50
    }


# Test data fixtures
@pytest.fixture
def sample_algorithm():
    """Sample compression algorithm data."""
    return {
        "name": "test_algo",
        "category": "experimental",
        "description": "Test algorithm for unit testing",
        "bestFor": ["testing", "development"],
        "compressionLevels": [1, 2, 3],
        "parameters": {"param1": "value1"},
        "characteristics": {
            "speed": "fast",
            "compression": "good",
            "memoryUsage": "low",
            "compatibility": "limited"
        },
        "isEnabled": True,
        "version": "1.0.0"
    }


@pytest.fixture
def sample_metrics():
    """Sample system metrics data."""
    return {
        "cpu": 45.5,
        "memory": 60.2,
        "disk": 75.0,
        "network": 1024000,
        "compressionEfficiency": 85.5,
        "throughput": 5000000,
        "successRate": 98.5,
        "errorRate": 1.5,
        "averageCompressionRatio": 3.2,
        "responseTime": 150,
        "systemHealth": "healthy",
        "activeConnections": 50,
        "queueLength": 10,
        "algorithmPerformance": {
            "gzip": 95.0,
            "zstd": 98.5
        }
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "requires_ollama: marks tests requiring Ollama to be running"
    )
