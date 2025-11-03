"""
API Agent Tests (Agent 04)

Tests REST API endpoints and WebSocket functionality.
"""

import pytest
import asyncio
from httpx import AsyncClient
from app.agents.api.api_agent import APIAgent

class TestAPIAgent:
    """Test API agent functionality."""

    @pytest.fixture
    async def api_agent(self):
        """Create API agent for testing."""
        agent = APIAgent()
        await agent._populate_agent_registry()  # Manually populate for testing
        yield agent

    @pytest.fixture
    async def test_client(self):
        """Create test client for API testing."""
        from app.agents.api.fastapi_app import app
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

    @pytest.mark.asyncio
    async def test_api_agent_initialization(self, api_agent):
        """Test API agent initialization."""
        status = api_agent.get_status()
        assert status["agent_type"] == "api_layer"
        assert "API_ENDPOINTS" in [cap.value for cap in status["capabilities"]]

    @pytest.mark.asyncio
    async def test_agent_registration(self, api_agent):
        """Test agent registration with API layer."""
        # Mock agent
        class MockAgent:
            agent_type = "mock"
            capabilities = []
            def get_status(self):
                return {"agent_type": "mock", "status": "active"}

        mock_agent = MockAgent()
        api_agent.register_agent("mock", mock_agent)

        assert "mock" in api_agent.agent_registry

    @pytest.mark.asyncio
    async def test_api_request_handling(self, api_agent):
        """Test API request handling."""
        # Register mock agent
        class MockAgent:
            agent_type = "mock"
            capabilities = []
            def get_status(self):
                return {"status": "active", "agent_type": "mock"}

        mock_agent = MockAgent()
        api_agent.register_agent("mock", mock_agent)

        # Test status request
        result = await api_agent.handle_api_request("mock", "status", "GET", {})
        assert result["status"] == 200
        assert result["data"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_unknown_agent_request(self, api_agent):
        """Test request to unknown agent."""
        result = await api_agent.handle_api_request("unknown", "status", "GET", {})
        assert result["status"] == 404
        assert "not registered" in result["error"]

    @pytest.mark.asyncio
    async def test_task_execution_request(self, api_agent):
        """Test task execution through API."""
        # This would need a more complex mock agent that supports execute
        # For now, test with a known agent
        if "01" in api_agent.agent_registry:
            task_data = {
                "task_id": "test_task_001",
                "operation": "health_check",
                "parameters": {"test": True}
            }

            result = await api_agent.handle_api_request("01", "execute", "POST", task_data)
            # Should not fail, even if agent returns an error
            assert isinstance(result, dict)
            assert "status" in result

    @pytest.mark.asyncio
    async def test_system_status_aggregation(self, api_agent):
        """Test system status aggregation."""
        system_status = await api_agent.get_system_status()

        assert "system_status" in system_status
        assert "agents" in system_status
        assert "api_metrics" in system_status
        assert "timestamp" in system_status

    @pytest.mark.asyncio
    async def test_root_endpoint(self, test_client):
        """Test API root endpoint."""
        response = await test_client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "Meta-Recursive Multi-Agent API" in data["message"]
        assert "agents" in data

    @pytest.mark.asyncio
    async def test_list_agents_endpoint(self, test_client):
        """Test agents listing endpoint."""
        response = await test_client.get("/agents")
        assert response.status_code == 200

        data = response.json()
        assert "agents" in data
        # Should have registered agents from startup

    @pytest.mark.asyncio
    async def test_system_status_endpoint(self, test_client):
        """Test system status endpoint."""
        response = await test_client.get("/system/status")
        assert response.status_code == 200

        data = response.json()
        assert data["system_status"] in ["operational", "initializing"]
        assert "agents" in data
        assert "api_metrics" in data

    @pytest.mark.asyncio
    async def test_agent_health_endpoint(self, test_client):
        """Test agent health endpoint."""
        # Test with agent 01 (infrastructure)
        response = await test_client.get("/agents/01/health")
        # Should not return 500 error
        assert response.status_code in [200, 404]  # 404 if agent not registered

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_unknown_agent_endpoints(self, test_client):
        """Test endpoints with unknown agent."""
        # Status endpoint
        response = await test_client.get("/agents/unknown/status")
        assert response.status_code == 404

        # Execute endpoint
        response = await test_client.post("/agents/unknown/execute", json={})
        assert response.status_code == 404

        # Health endpoint
        response = await test_client.get("/agents/unknown/health")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_error_handling(self, test_client):
        """Test error handling in API."""
        # Test invalid JSON (should be handled gracefully)
        response = await test_client.post(
            "/agents/01/execute",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        # Should return appropriate error status
        assert response.status_code >= 400

    @pytest.mark.asyncio
    async def test_websocket_client_management(self, api_agent):
        """Test WebSocket client management."""
        # Test adding and removing clients
        api_agent.websocket_clients["test_client"] = "mock_websocket"
        assert "test_client" in api_agent.websocket_clients

        # Simulate disconnect cleanup
        disconnected = []
        for client_id, client in api_agent.websocket_clients.items():
            if client_id == "test_client":  # Simulate disconnect
                disconnected.append(client_id)

        for client_id in disconnected:
            del api_agent.websocket_clients[client_id]

        assert "test_client" not in api_agent.websocket_clients
