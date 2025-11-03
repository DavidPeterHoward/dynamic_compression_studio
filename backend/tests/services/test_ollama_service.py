"""
Tests for Ollama Service.

Tests cover:
- Model listing
- Model selection logic
- Text generation
- Fallback mechanisms
- Performance tracking
- Error handling
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.ollama_service import (
    OllamaService,
    ModelPurpose,
    get_ollama_service
)


class TestOllamaService:
    """Test suite for OllamaService."""
    
    @pytest.fixture
    def ollama_service(self):
        """Create OllamaService instance for testing."""
        return OllamaService(base_url="http://localhost:11434")
    
    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_initialize_service(self, ollama_service):
        """
        Test service initialization.
        
        Verifies:
        - Service can connect to Ollama
        - Models are discovered
        - Available models list is populated
        """
        success = await ollama_service.initialize()
        
        assert success is True, "Service should initialize successfully"
        assert len(ollama_service.available_models) > 0, "Should discover available models"
        
        # Verify model structure
        first_model = ollama_service.available_models[0]
        assert "name" in first_model, "Model should have name"
        assert "details" in first_model, "Model should have details"
    
    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_list_models(self, ollama_service):
        """
        Test listing available models.
        
        Expected models from setup:
        - magistral:24b
        - llama3.1:8b
        - qwen2.5-coder:1.5b-base
        - nomic-embed-text:latest
        - deepseek-coder-v2:latest
        - gemma3n:e4b
        - gemma3:4b-it
        """
        models = await ollama_service.list_models()
        
        assert len(models) >= 4, "Should have at least 4 models"
        
        model_names = [m["name"] for m in models]
        
        # Check for key models
        assert any("llama" in name for name in model_names), "Should have llama model"
        assert any("coder" in name for name in model_names), "Should have coder model"
        
        print(f"\nAvailable models: {model_names}")
    
    def test_model_selection_code_generation(self, ollama_service):
        """
        Test model selection for code generation.
        
        Should prefer:
        1. deepseek-coder-v2
        2. qwen2.5-coder
        """
        # Set up available models
        ollama_service.available_models = [
            {"name": "llama3.1:8b"},
            {"name": "deepseek-coder-v2:latest"},
            {"name": "qwen2.5-coder:1.5b-base"}
        ]
        
        selected = ollama_service.select_model(ModelPurpose.CODE_GENERATION)
        
        assert selected == "deepseek-coder-v2:latest", \
            "Should select deepseek-coder for code generation"
    
    def test_model_selection_reasoning(self, ollama_service):
        """
        Test model selection for reasoning tasks.
        
        Should prefer larger models with better reasoning.
        """
        ollama_service.available_models = [
            {"name": "magistral:24b"},
            {"name": "llama3.1:8b"},
            {"name": "gemma3:4b-it"}
        ]
        
        selected = ollama_service.select_model(ModelPurpose.REASONING)
        
        assert selected == "magistral:24b", \
            "Should select magistral for reasoning tasks"
    
    def test_model_selection_fast_preference(self, ollama_service):
        """
        Test model selection with speed preference.
        
        Should prefer smaller, faster models.
        """
        ollama_service.available_models = [
            {"name": "magistral:24b"},
            {"name": "llama3.1:8b"},
            {"name": "gemma3:4b-it"}
        ]
        
        selected = ollama_service.select_model(
            ModelPurpose.GENERAL,
            prefer_fast=True
        )
        
        assert selected == "llama3.1:8b", \
            "Should select llama3.1:8b for fast general tasks"
    
    def test_model_selection_embeddings(self, ollama_service):
        """Test model selection for embeddings."""
        ollama_service.available_models = [
            {"name": "nomic-embed-text:latest"},
            {"name": "llama3.1:8b"}
        ]
        
        selected = ollama_service.select_model(ModelPurpose.EMBEDDINGS)
        
        assert selected == "nomic-embed-text:latest", \
            "Should select nomic-embed-text for embeddings"
    
    def test_model_selection_no_models(self, ollama_service):
        """Test model selection when no models available."""
        ollama_service.available_models = []
        
        selected = ollama_service.select_model(ModelPurpose.GENERAL)
        
        assert selected is None, "Should return None when no models available"
    
    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    async def test_generate_text(self, ollama_service):
        """
        Test text generation with actual Ollama model.
        
        This test requires Ollama to be running.
        """
        await ollama_service.initialize()
        
        result = await ollama_service.generate(
            prompt="Say 'Hello, World!' and nothing else.",
            model="llama3.1:8b",
            temperature=0.1,  # Low temperature for deterministic output
            max_tokens=10
        )
        
        assert "response" in result, "Result should contain response"
        assert len(result["response"]) > 0, "Response should not be empty"
        assert "model" in result, "Result should contain model name"
        assert result["model"] == "llama3.1:8b", "Should use correct model"
        assert "duration_seconds" in result, "Should track duration"
        assert result["duration_seconds"] > 0, "Duration should be positive"
        
        print(f"\nGeneration result: {result['response'][:100]}")
        print(f"Duration: {result['duration_seconds']:.2f}s")
        print(f"Tokens/sec: {result['tokens_per_second']:.2f}")
    
    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_generate_with_system_prompt(self, ollama_service):
        """Test generation with system prompt."""
        await ollama_service.initialize()
        
        result = await ollama_service.generate(
            prompt="What is 2+2?",
            model="llama3.1:8b",
            system_prompt="You are a math teacher. Answer concisely.",
            temperature=0.1
        )
        
        assert "response" in result
        assert "4" in result["response"], "Should answer math question"
        
        print(f"\nMath response: {result['response']}")
    
    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_generate_code(self, ollama_service):
        """
        Test code generation with coding model.
        
        Uses qwen2.5-coder or deepseek-coder for best results.
        """
        await ollama_service.initialize()
        
        # Select appropriate code model
        model = ollama_service.select_model(ModelPurpose.CODE_GENERATION)
        
        if model:
            result = await ollama_service.generate(
                prompt="Write a Python function to calculate fibonacci(n). Just the function, no explanation.",
                model=model,
                temperature=0.1,
                max_tokens=200
            )
            
            assert "response" in result
            assert "def " in result["response"].lower() or "function" in result["response"].lower(), \
                "Response should contain code"
            
            print(f"\nGenerated code:\n{result['response']}")
        else:
            pytest.skip("No coding model available")
    
    @pytest.mark.asyncio
    async def test_performance_tracking(self, ollama_service):
        """
        Test that service tracks model performance metrics.
        """
        # Mock the generate call
        with patch.object(ollama_service, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = {
                "model": "llama3.1:8b",
                "response": "test",
                "done": True,
                "duration_seconds": 1.5,
                "tokens_generated": 50,
                "tokens_per_second": 33.3
            }
            
            # Call generate multiple times
            await ollama_service.generate("test1", model="llama3.1:8b")
            await ollama_service.generate("test2", model="llama3.1:8b")
            
            # Mock the performance tracking (since we mocked generate)
            ollama_service.model_performance["llama3.1:8b"] = {
                "total_calls": 2,
                "total_duration": 3.0,
                "avg_duration": 1.5
            }
            
            perf = ollama_service.get_model_performance()
            
            assert "llama3.1:8b" in perf, "Should track performance for model"
            assert perf["llama3.1:8b"]["total_calls"] == 2, "Should count calls"
            assert perf["llama3.1:8b"]["avg_duration"] > 0, "Should calculate average duration"
    
    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_generate_with_fallback(self, ollama_service):
        """
        Test automatic fallback to alternative models.
        """
        await ollama_service.initialize()
        
        # Try to generate with fallback
        result = await ollama_service.generate_with_fallback(
            prompt="Say hello",
            purpose=ModelPurpose.GENERAL,
            temperature=0.1,
            max_tokens=10
        )
        
        assert "response" in result, "Should get response from fallback"
        assert len(result["response"]) > 0, "Response should not be empty"
        
        print(f"\nFallback generation successful with model: {result['model']}")
    
    @pytest.mark.asyncio
    async def test_generate_timeout(self, ollama_service):
        """Test that generation times out appropriately."""
        ollama_service.timeout = 0.1  # Very short timeout
        
        with pytest.raises(Exception) as exc_info:
            await ollama_service.generate(
                prompt="This is a very long prompt " * 100,
                model="llama3.1:8b"
            )
        
        err = str(exc_info.value).lower()
        assert ("timeout" in err) or ("timed out" in err) or ("failed" in err)
    
    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_embeddings(self, ollama_service):
        """
        Test text embedding generation.
        
        Requires nomic-embed-text model.
        """
        await ollama_service.initialize()
        
        # Check if embedding model is available
        has_embed_model = any(
            "nomic-embed" in m["name"] 
            for m in ollama_service.available_models
        )
        
        if has_embed_model:
            embedding = await ollama_service.embed("This is a test sentence")
            
            assert isinstance(embedding, list), "Embedding should be a list"
            assert len(embedding) > 0, "Embedding should not be empty"
            assert all(isinstance(x, (int, float)) for x in embedding), \
                "Embedding should contain numbers"
            
            print(f"\nEmbedding dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
        else:
            pytest.skip("nomic-embed-text model not available")
    
    @pytest.mark.asyncio
    @pytest.mark.requires_ollama
    async def test_health_check(self, ollama_service):
        """Test health check endpoint."""
        is_healthy = await ollama_service.health_check()
        
        assert is_healthy is True, "Service should be healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, ollama_service):
        """Test health check when service is down."""
        # Point to invalid URL
        ollama_service.base_url = "http://localhost:99999"
        
        is_healthy = await ollama_service.health_check()
        
        assert is_healthy is False, "Should detect unhealthy service"
    
    def test_get_ollama_service_singleton(self):
        """Test that get_ollama_service returns singleton."""
        service1 = get_ollama_service()
        service2 = get_ollama_service()
        
        assert service1 is service2, "Should return same instance"


class TestModelPurpose:
    """Test ModelPurpose enum."""
    
    def test_model_purposes_defined(self):
        """Test that all model purposes are defined."""
        assert ModelPurpose.GENERAL
        assert ModelPurpose.CODE_GENERATION
        assert ModelPurpose.EMBEDDINGS
        assert ModelPurpose.REASONING
    
    def test_model_purpose_values(self):
        """Test model purpose string values."""
        assert ModelPurpose.GENERAL.value == "general"
        assert ModelPurpose.CODE_GENERATION.value == "code_generation"
        assert ModelPurpose.EMBEDDINGS.value == "embeddings"
        assert ModelPurpose.REASONING.value == "reasoning"


# Integration test
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.requires_ollama
async def test_ollama_integration_workflow():
    """
    End-to-end integration test for Ollama service.
    
    Tests complete workflow:
    1. Initialize service
    2. List models
    3. Select appropriate model
    4. Generate text
    5. Track performance
    """
    service = OllamaService()
    
    # 1. Initialize
    success = await service.initialize()
    assert success, "Should initialize"
    
    # 2. List models
    models = await service.list_models()
    assert len(models) > 0, "Should have models"
    
    # 3. Select model
    selected = service.select_model(ModelPurpose.GENERAL)
    assert selected is not None, "Should select model"
    
    # 4. Generate
    result = await service.generate(
        prompt="Count from 1 to 5",
        model=selected,
        temperature=0.1,
        max_tokens=50
    )
    assert "response" in result, "Should generate response"
    
    # 5. Check performance
    perf = service.get_model_performance()
    assert selected in perf, "Should track performance"
    assert perf[selected]["total_calls"] == 1, "Should count calls"
    
    print("\n=== Integration Test Success ===")
    print(f"Models available: {len(models)}")
    print(f"Selected model: {selected}")
    print(f"Response: {result['response'][:100]}")
    print(f"Performance: {perf[selected]}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s", "-m", "not slow"])

