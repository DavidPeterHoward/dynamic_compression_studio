# Module Interfaces Reference
## Complete Interface Contracts for All Agents

**Version:** 1.0  
**Date:** 2025-10-30  
**Purpose:** Define all interface contracts between modules  

---

## 🎯 INTERFACE PHILOSOPHY

**Rules:**
1. All inter-module communication MUST go through interfaces
2. Interfaces are versioned and backward compatible
3. Breaking changes require new version number
4. Mocks provided for all interfaces
5. No direct module imports allowed

---

## 📋 INTERFACE CATALOG

### 1. Database Interface (IDatabaseService)

**Provided By:** Agent 02 (Database)  
**Used By:** Agent 03, 04, 06, 08  
**Version:** v1.0  

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')

class IDatabaseService(ABC, Generic[T]):
    """Universal database interface for all data operations"""
    
    @abstractmethod
    async def create(
        self,
        table: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """
        Create new record
        
        Args:
            table: Table/collection name
            data: Record data
            user_id: Optional user ID for audit
            
        Returns:
            Created record ID
            
        Raises:
            ValidationError: Invalid data
            DatabaseError: Database operation failed
        """
        pass
    
    @abstractmethod
    async def read(
        self,
        table: str,
        id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Read single record by ID
        
        Args:
            table: Table/collection name
            id: Record ID
            
        Returns:
            Record data or None if not found
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        table: str,
        id: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """
        Update existing record
        
        Args:
            table: Table/collection name
            id: Record ID
            data: Updated fields
            user_id: Optional user ID for audit
            
        Returns:
            True if successful, False if not found
            
        Raises:
            ValidationError: Invalid data
            DatabaseError: Database operation failed
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        table: str,
        id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Delete record (soft delete if supported)
        
        Args:
            table: Table/collection name
            id: Record ID
            user_id: Optional user ID for audit
            
        Returns:
            True if successful, False if not found
        """
        pass
    
    @abstractmethod
    async def query(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query records with filters
        
        Args:
            table: Table/collection name
            filters: Query filters (e.g., {"status": "active"})
            sort: Sort specification (e.g., [("created_at", "desc")])
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of matching records
        """
        pass
    
    @abstractmethod
    async def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count records matching filters"""
        pass
    
    @abstractmethod
    async def transaction(self) -> 'ITransaction':
        """Begin database transaction"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check database health
        
        Returns:
            {
                "status": "healthy|degraded|unhealthy",
                "latency_ms": float,
                "connections": int,
                "errors": List[str]
            }
        """
        pass
```

### 2. Core Engine Interface (ICoreEngine)

**Provided By:** Agent 03 (Core Engine)  
**Used By:** Agent 04, 06  
**Version:** v1.0  

```python
class ICoreEngine(ABC):
    """Core processing engine interface"""
    
    @abstractmethod
    async def process_task(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process any task
        
        Args:
            task: {
                "type": str,  # Task type
                "input": Any,  # Task input
                "parameters": Dict[str, Any],  # Task parameters
                "priority": int,  # 1-10
                "timeout_ms": int
            }
            context: Optional execution context
            
        Returns:
            {
                "success": bool,
                "output": Any,
                "metrics": Dict[str, float],
                "duration_ms": float,
                "errors": List[str]
            }
        """
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """
        Get engine status
        
        Returns:
            {
                "status": "idle|processing|overloaded",
                "active_tasks": int,
                "queued_tasks": int,
                "throughput": float,  # tasks/sec
                "avg_latency_ms": float,
                "error_rate": float
            }
        """
        pass
    
    @abstractmethod
    async def configure(
        self,
        config: Dict[str, Any]
    ) -> bool:
        """Update engine configuration"""
        pass
    
    @abstractmethod
    async def register_processor(
        self,
        task_type: str,
        processor: callable
    ) -> bool:
        """Register custom task processor"""
        pass
```

### 3. API Interface (IAPIService)

**Provided By:** Agent 04 (API Layer)  
**Used By:** Agent 05  
**Version:** v1.0  

```python
class IAPIService(ABC):
    """API service interface"""
    
    @abstractmethod
    async def register_endpoint(
        self,
        path: str,
        handler: callable,
        methods: List[str],
        auth_required: bool = True,
        rate_limit: Optional[int] = None
    ) -> bool:
        """Register API endpoint"""
        pass
    
    @abstractmethod
    async def validate_request(
        self,
        request: Any
    ) -> tuple[bool, Optional[str]]:
        """
        Validate incoming request
        
        Returns:
            (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    async def format_response(
        self,
        data: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Format API response"""
        pass
```

### 4. Agent Interface (IAgent)

**Provided By:** Agent 06 (Agent Framework)  
**Used By:** Agent 03, 07  
**Version:** v1.0  

```python
class IAgent(ABC):
    """Base agent interface"""
    
    @abstractmethod
    async def initialize(
        self,
        config: Dict[str, Any]
    ) -> bool:
        """
        Initialize agent
        
        Args:
            config: Agent configuration
            
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    async def execute_task(
        self,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute assigned task
        
        Args:
            task: {
                "id": str,
                "type": str,
                "input": Any,
                "parameters": Dict[str, Any]
            }
            
        Returns:
            {
                "success": bool,
                "output": Any,
                "confidence": float,  # 0-1
                "explanation": str
            }
        """
        pass
    
    @abstractmethod
    async def communicate(
        self,
        message: Dict[str, Any],
        target_agent: str
    ) -> Dict[str, Any]:
        """
        Send message to another agent
        
        Args:
            message: Message content
            target_agent: Target agent ID
            
        Returns:
            Response from target agent
        """
        pass
    
    @abstractmethod
    async def self_validate(self) -> Dict[str, Any]:
        """
        Validate own functionality (bootstrap fail-pass)
        
        Returns:
            {
                "status": "pass|fail",
                "checks": List[Dict],
                "issues": List[str]
            }
        """
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities
        
        Returns:
            {
                "task_types": List[str],
                "specializations": List[str],
                "performance_metrics": Dict[str, float]
            }
        """
        pass
```

### 5. LLM Interface (ILLMService)

**Provided By:** Agent 07 (LLM Integration)  
**Used By:** Agent 03, 06  
**Version:** v1.0  

```python
class ILLMService(ABC):
    """LLM inference interface"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str = "llama3.2",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate LLM completion
        
        Args:
            prompt: Input prompt
            model: Model name
            parameters: Generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            {
                "text": str,
                "model": str,
                "tokens_used": int,
                "duration_ms": float
            }
        """
        pass
    
    @abstractmethod
    async def embed(
        self,
        text: str,
        model: str = "llama3.2"
    ) -> List[float]:
        """Generate text embeddings"""
        pass
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models"""
        pass
```

### 6. Monitoring Interface (IMonitoringService)

**Provided By:** Agent 08 (Monitoring)  
**Used By:** All agents  
**Version:** v1.0  

```python
class IMonitoringService(ABC):
    """Monitoring and observability interface"""
    
    @abstractmethod
    async def log_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Log metric value
        
        Args:
            name: Metric name (e.g., "api.response_time")
            value: Metric value
            tags: Metric tags (e.g., {"endpoint": "/api/tasks"})
            timestamp: Optional timestamp (defaults to now)
        """
        pass
    
    @abstractmethod
    async def log_event(
        self,
        event: Dict[str, Any]
    ) -> bool:
        """
        Log application event
        
        Args:
            event: {
                "type": str,
                "severity": "debug|info|warning|error|critical",
                "message": str,
                "details": Dict[str, Any],
                "source": str
            }
        """
        pass
    
    @abstractmethod
    async def get_health(
        self,
        component: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get system health status
        
        Returns:
            {
                "status": "healthy|degraded|unhealthy",
                "components": Dict[str, Dict],
                "timestamp": datetime
            }
        """
        pass
    
    @abstractmethod
    async def create_alert(
        self,
        condition: str,
        threshold: float,
        action: callable
    ) -> str:
        """Create monitoring alert"""
        pass
```

### 7. Testing Interface (ITestingService)

**Provided By:** Agent 09 (Testing)  
**Used By:** All agents  
**Version:** v1.0  

```python
class ITestingService(ABC):
    """Testing and validation interface"""
    
    @abstractmethod
    async def run_tests(
        self,
        module: str,
        test_type: str = "unit"  # unit|integration|e2e
    ) -> Dict[str, Any]:
        """
        Run test suite
        
        Returns:
            {
                "passed": int,
                "failed": int,
                "skipped": int,
                "coverage": float,
                "duration_ms": float,
                "failures": List[Dict]
            }
        """
        pass
    
    @abstractmethod
    async def validate_interface(
        self,
        implementation: Any,
        interface: type
    ) -> Dict[str, Any]:
        """Validate implementation against interface contract"""
        pass
```

### 8. Security Interface (ISecurityService)

**Provided By:** Agent 12 (Security)  
**Used By:** All agents  
**Version:** v1.0  

```python
class ISecurityService(ABC):
    """Security and authentication interface"""
    
    @abstractmethod
    async def authenticate(
        self,
        credentials: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user
        
        Returns:
            User info + token or None if invalid
        """
        pass
    
    @abstractmethod
    async def authorize(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> bool:
        """Check if user authorized for action on resource"""
        pass
    
    @abstractmethod
    async def encrypt(
        self,
        data: bytes
    ) -> bytes:
        """Encrypt sensitive data"""
        pass
    
    @abstractmethod
    async def decrypt(
        self,
        encrypted_data: bytes
    ) -> bytes:
        """Decrypt data"""
        pass
```

---

## 🔄 INTERFACE VERSIONING

### Version Format
`v{major}.{minor}` (e.g., v1.0, v1.1, v2.0)

### Version Rules
1. **Minor version change (v1.0 → v1.1):** Backward compatible additions
2. **Major version change (v1.0 → v2.0):** Breaking changes

### Compatibility Policy
- Support current version + 1 previous major version
- Deprecation warnings for 2 minor versions before removal
- Clear migration guides for major version changes

---

## 🧪 MOCK IMPLEMENTATIONS

Mock implementations are provided in `agent-implementation-modules/00-MASTER-ORCHESTRATION/mocks/`

Example usage:
```python
from mocks import MockDatabaseService

# Use mock during development
db = MockDatabaseService()
result = await db.create("users", {"name": "Test"})
```

---

## 📊 INTEGRATION TESTING

All interface implementations must pass integration tests:

```python
# tests/integration/test_database_interface.py
async def test_database_interface_compliance(db_service: IDatabaseService):
    """Test database service implements interface correctly"""
    # Create
    user_id = await db_service.create("users", {"name": "Test"})
    assert user_id
    
    # Read
    user = await db_service.read("users", user_id)
    assert user["name"] == "Test"
    
    # Update
    success = await db_service.update("users", user_id, {"name": "Updated"})
    assert success
    
    # Query
    results = await db_service.query("users", {"name": "Updated"})
    assert len(results) == 1
    
    # Delete
    success = await db_service.delete("users", user_id)
    assert success
```

---

## 🎯 USING INTERFACES

### As Consumer (Using Interface)

```python
from interfaces import IDatabaseService

class MyService:
    def __init__(self, db: IDatabaseService):
        self.db = db  # Accept interface, not implementation
    
    async def create_user(self, data: Dict) -> str:
        return await self.db.create("users", data)
```

### As Provider (Implementing Interface)

```python
from interfaces import IDatabaseService

class PostgresDatabaseService(IDatabaseService):
    async def create(self, table: str, data: Dict[str, Any], user_id: Optional[str] = None) -> str:
        # Actual implementation
        pass
    
    # Implement all other methods...
```

---

## 📝 CHECKLIST FOR INTERFACE COMPLIANCE

- [ ] All methods implemented
- [ ] Correct method signatures
- [ ] Proper return types
- [ ] Error handling as specified
- [ ] Documentation strings
- [ ] Integration tests passing
- [ ] Mock implementation provided
- [ ] Performance benchmarks met

---

**Document Version:** 1.0  
**Date:** 2025-10-30  
**Status:** INTERFACE CONTRACTS DEFINED  
**Next:** Implement against these contracts  

**COMPLETE INTERFACE SPECIFICATIONS FOR ALL MODULES** 🔌

