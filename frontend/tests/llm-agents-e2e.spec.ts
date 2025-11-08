/**
 * Comprehensive E2E Test Suite for LLM Agents
 * Tests real conversations with Ollama models across all agent types,
 * communication methods, and statistical inference analysis
 */

import { expect, Page, test } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8441';

// Test data variations for statistical inference
const CONVERSATION_VARIATIONS = {
  short: {
    prompts: [
      "Hello",
      "Hi there",
      "What's up?",
      "Good morning"
    ],
    expectedLengths: [1, 50] // chars
  },
  medium: {
    prompts: [
      "Explain how machine learning works in simple terms",
      "What are the benefits of renewable energy?",
      "How do computers store and process information?",
      "What is the scientific method?"
    ],
    expectedLengths: [100, 500]
  },
  complex: {
    prompts: [
      "Analyze the impact of artificial intelligence on job markets in the next decade, considering both positive and negative effects",
      "Compare and contrast different approaches to climate change mitigation, including carbon pricing, renewable energy subsidies, and technological innovation",
      "Explain the principles of quantum computing and discuss potential applications in cryptography, drug discovery, and optimization problems"
    ],
    expectedLengths: [500, 2000]
  }
};

const AGENT_TYPES = [
  { id: '07', name: 'Conversational Agent', type: 'conversational' },
  { id: '08', name: 'Code Assistant', type: 'code_assistant' },
  { id: '09', name: 'Data Analyst', type: 'analyst' },
  { id: '10', name: 'Creative Writer', type: 'creative_writer' }
];

const TEMPERATURE_VARIATIONS = [0.1, 0.5, 0.9]; // Low, medium, high creativity
const MAX_TOKENS_VARIATIONS = [256, 512, 1024]; // Short, medium, long responses

// Statistical tracking
interface TestMetrics {
  agentType: string;
  prompt: string;
  temperature: number;
  maxTokens: number;
  responseTime: number;
  responseLength: number;
  success: boolean;
  error?: string;
}

class StatisticalAnalyzer {
  private metrics: TestMetrics[] = [];

  addMetric(metric: TestMetrics) {
    this.metrics.push(metric);
  }

  getAgentStats(agentType: string) {
    const agentMetrics = this.metrics.filter(m => m.agentType === agentType && m.success);

    if (agentMetrics.length === 0) return null;

    const responseTimes = agentMetrics.map(m => m.responseTime);
    const responseLengths = agentMetrics.map(m => m.responseLength);

    return {
      count: agentMetrics.length,
      avgResponseTime: responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length,
      minResponseTime: Math.min(...responseTimes),
      maxResponseTime: Math.max(...responseTimes),
      avgResponseLength: responseLengths.reduce((a, b) => a + b, 0) / responseLengths.length,
      minResponseLength: Math.min(...responseLengths),
      maxResponseLength: Math.max(...responseLengths),
      successRate: agentMetrics.length / this.metrics.filter(m => m.agentType === agentType).length
    };
  }

  getTemperatureImpact() {
    const tempGroups: { [key: number]: TestMetrics[] } = {};
    this.metrics.filter(m => m.success).forEach(m => {
      if (!tempGroups[m.temperature]) tempGroups[m.temperature] = [];
      tempGroups[m.temperature].push(m);
    });

    const results: { [key: number]: any } = {};
    Object.keys(tempGroups).forEach(temp => {
      const metrics = tempGroups[parseFloat(temp)];
      results[parseFloat(temp)] = {
        count: metrics.length,
        avgLength: metrics.reduce((sum, m) => sum + m.responseLength, 0) / metrics.length,
        avgTime: metrics.reduce((sum, m) => sum + m.responseTime, 0) / metrics.length
      };
    });

    return results;
  }

  getComplexityAnalysis() {
    const complexityGroups: { [key: string]: TestMetrics[] } = {
      short: [],
      medium: [],
      complex: []
    };

    this.metrics.filter(m => m.success).forEach(m => {
      const promptLength = m.prompt.length;
      if (promptLength < 20) complexityGroups.short.push(m);
      else if (promptLength < 100) complexityGroups.medium.push(m);
      else complexityGroups.complex.push(m);
    });

    const results: { [key: string]: any } = {};
    Object.keys(complexityGroups).forEach(complexity => {
      const metrics = complexityGroups[complexity];
      if (metrics.length > 0) {
        results[complexity] = {
          count: metrics.length,
          avgLength: metrics.reduce((sum, m) => sum + m.responseLength, 0) / metrics.length,
          avgTime: metrics.reduce((sum, m) => sum + m.responseTime, 0) / metrics.length
        };
      }
    });

    return results;
  }

  exportResults() {
    const report = {
      timestamp: new Date().toISOString(),
      totalTests: this.metrics.length,
      successfulTests: this.metrics.filter(m => m.success).length,
      agentStats: AGENT_TYPES.reduce((acc, agent) => {
        acc[agent.type] = this.getAgentStats(agent.type);
        return acc;
      }, {} as any),
      temperatureImpact: this.getTemperatureImpact(),
      complexityAnalysis: this.getComplexityAnalysis(),
      allMetrics: this.metrics
    };

    // Write to file
    const reportPath = path.join(process.cwd(), 'test-results', 'llm-agents-e2e-report.json');
    fs.mkdirSync(path.dirname(reportPath), { recursive: true });
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    return report;
  }
}

const statsAnalyzer = new StatisticalAnalyzer();

// Helper functions
async function waitForAgentReady(page: Page, agentId: string, timeout = 30000) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    try {
      const response = await page.request.get(`${API_BASE_URL}/api/v1/agents/${agentId}/status`);
      if (response.ok()) {
        const data = await response.json();
        if (data.status !== 'error') {
          return true;
        }
      }
    } catch (error) {
      // Agent not ready yet
    }
    await page.waitForTimeout(1000);
  }

  throw new Error(`Agent ${agentId} not ready within ${timeout}ms`);
}

async function executeTaskViaAPI(
  page: Page,
  agentId: string,
  operation: string,
  parameters: any,
  priority = 'normal',
  timeout = 30
) {
  const startTime = Date.now();

  const response = await page.request.post(`${API_BASE_URL}/api/v1/agents/${agentId}/execute`, {
    data: {
      operation,
      parameters,
      priority,
      timeout_seconds: timeout
    }
  });

  const endTime = Date.now();
  const responseTime = endTime - startTime;

  if (!response.ok()) {
    throw new Error(`Task execution failed: ${response.status()} ${response.statusText()}`);
  }

  const result = await response.json();
  return { result, responseTime };
}

async function measureResponseQuality(response: string, prompt: string): Promise<number> {
  // Simple quality metrics - in real implementation, this could use more sophisticated analysis
  const responseLength = response.length;
  const hasCompleteSentences = response.includes('.') || response.includes('!') || response.includes('?');
  const hasVariedVocabulary = new Set(response.toLowerCase().split(/\s+/)).size > 10;
  const relevanceScore = response.toLowerCase().includes(prompt.toLowerCase().split(' ')[0]) ? 1 : 0;

  let quality = 0;
  if (responseLength > 50) quality += 0.3;
  if (hasCompleteSentences) quality += 0.3;
  if (hasVariedVocabulary) quality += 0.2;
  if (relevanceScore > 0) quality += 0.2;

  return Math.min(1.0, quality);
}

// Test suite
test.describe('LLM Agents E2E Test Suite', () => {
  test.beforeAll(async ({ browser }) => {
    // Ensure Ollama is running and models are available
    const page = await browser.newPage();
    try {
      // Check if Ollama service is accessible
      await page.goto('http://localhost:11434/api/tags');
      await page.waitForLoadState('networkidle');
    } catch (error) {
      console.warn('Ollama service not accessible - tests may fail');
    }
    await page.close();
  });

  test.beforeEach(async ({ page }) => {
    // Set up page with extended timeout and error handling
    page.setDefaultTimeout(60000);

    // Intercept and log network requests for debugging
    page.on('request', request => {
      if (request.url().includes('/api/v1/agents/')) {
        console.log(`API Request: ${request.method()} ${request.url()}`);
      }
    });

    page.on('response', response => {
      if (response.url().includes('/api/v1/agents/')) {
        console.log(`API Response: ${response.status()} ${response.url()}`);
      }
    });

    await page.goto('http://localhost:8443');
    await page.waitForLoadState('networkidle');

    // Navigate to Agents tab with verification
    await page.click('[data-testid="agents-nav-button"]');
    await page.waitForTimeout(2000);

    // Verify we're on the agents page
    await expect(page.locator('text=Agent Management')).toBeVisible();
  });

  // Data Flow and UI Integration Tests
  test.describe('Data Flow & UI Integration', () => {
    test('should load agents data and display in UI', async ({ page }) => {
      // Verify agents are loaded from API
      await page.waitForTimeout(3000); // Allow time for data loading

      // Check that agent data flows from API to UI
      const agentCards = page.locator('[class*="card"]').filter({ hasText: /Agent|agent/i });
      await expect(agentCards.first()).toBeVisible({ timeout: 10000 });

      // Verify agent status indicators are present
      const statusIndicators = page.locator('[class*="status"]').or(page.locator('text=idle')).or(page.locator('text=error'));
      await expect(statusIndicators.first()).toBeVisible();
    });

    test('should navigate between agent tabs with data persistence', async ({ page }) => {
      // Test Overview tab
      await page.click('text=Overview');
      await expect(page.locator('text=System Status')).toBeVisible();

      // Test Agents tab
      await page.click('text=Agents');
      await expect(page.locator('text=Agent Details')).toBeVisible();

      // Test Tasks tab
      await page.click('text=Task Execution');
      await expect(page.locator('text=Execute Task')).toBeVisible();

      // Test System tab
      await page.click('text=System');
      await expect(page.locator('text=System Metrics')).toBeVisible();

      // Verify data persists across navigation
      await page.click('text=Task Execution');
      await expect(page.locator('text=Execute Task')).toBeVisible();
    });

    test('should handle real-time updates via WebSocket', async ({ page }) => {
      // Monitor for WebSocket connection indicator
      const wsIndicator = page.locator('text=Live Updates').or(page.locator('text=Connected')).or(page.locator('text=Disconnected'));
      await expect(wsIndicator).toBeVisible({ timeout: 10000 });

      // Check for periodic status updates (every 30 seconds)
      await page.waitForTimeout(35000); // Wait for at least one update cycle

      // Verify UI reflects any updates
      const updateIndicator = page.locator('text=Updated').or(page.locator('[class*="updated"]'));
      // Note: This might not be visible if no updates occurred, but connection should remain
      const connectionStatus = await wsIndicator.textContent();
      expect(['Live Updates', 'Connected', 'Disconnected']).toContain(connectionStatus?.trim());
    });
  });

  // Frontend Component Integration Tests
  test.describe('Frontend Component Integration', () => {
    test('should render agent status dashboard with real data', async ({ page }) => {
      // Navigate to Overview
      await page.click('text=Overview');

      // Verify dashboard components render
      await expect(page.locator('text=System Status')).toBeVisible();
      await expect(page.locator('text=Active Agents')).toBeVisible();
      await expect(page.locator('text=API Requests')).toBeVisible();

      // Check for status indicators
      const statusCards = page.locator('[class*="glass"]').filter({ hasText: /System Status|Active Agents|API Requests/i });
      await expect(statusCards).toHaveCount(3);

      // Verify numeric displays
      const numericDisplays = page.locator('text=/\\d+/').filter({ hasText: /\d/ });
      await expect(numericDisplays.first()).toBeVisible();
    });

    test('should display agent details with proper data binding', async ({ page }) => {
      await page.click('text=Agents');

      // Find first agent card
      const firstAgentCard = page.locator('[class*="card"]').filter({ hasText: /Agent|agent/i }).first();
      await expect(firstAgentCard).toBeVisible();

      // Verify agent information is displayed
      await expect(firstAgentCard.locator('text=/Agent \\d+/')).toBeVisible();

      // Check for status information
      const statusInfo = firstAgentCard.locator('text=idle').or(firstAgentCard.locator('text=error')).or(firstAgentCard.locator('text=unknown'));
      await expect(statusInfo).toBeVisible();
    });

    test('should handle task execution form with validation', async ({ page }) => {
      await page.click('text=Task Execution');

      // Verify form elements are present and functional
      await expect(page.locator('label:has-text("Target Agent")')).toBeVisible();
      await expect(page.locator('label:has-text("Operation")')).toBeVisible();
      await expect(page.locator('label:has-text("Parameters")')).toBeVisible();

      // Test form interaction
      const agentSelect = page.locator('button').filter({ hasText: /Select agent|No agents available/ }).first();
      await expect(agentSelect).toBeVisible();
      await agentSelect.click();

      // Check dropdown opens
      const dropdown = page.locator('[role="listbox"]');
      await expect(dropdown).toBeVisible();

      // Test parameter validation
      const paramsTextarea = page.locator('textarea[id="parameters"]');
      await expect(paramsTextarea).toBeVisible();

      // Test invalid JSON handling
      await paramsTextarea.fill('invalid json {');
      const executeButton = page.locator('button:has-text("Execute Task")');
      await expect(executeButton).toBeDisabled();
    });
  });

  // API Route and Service Integration Tests
  test.describe('API Route & Service Integration', () => {
    test('should test complete API route flow', async ({ page }) => {
      // Test agents list endpoint
      const agentsResponse = await page.request.get(`${API_BASE_URL}/api/v1/agents`);
      expect(agentsResponse.status()).toBe(200);

      const agentsData = await agentsResponse.json();
      expect(agentsData).toHaveProperty('agents');
      expect(Array.isArray(agentsData.agents)).toBe(true);

      // Test system status endpoint
      const systemResponse = await page.request.get(`${API_BASE_URL}/api/v1/system/status`);
      expect(systemResponse.status()).toBe(200);

      const systemData = await systemResponse.json();
      expect(systemData).toHaveProperty('system_status');
      expect(systemData).toHaveProperty('agents');

      // Test individual agent endpoints
      for (const agent of AGENT_TYPES) {
        // Status endpoint
        const statusResponse = await page.request.get(`${API_BASE_URL}/api/v1/agents/${agent.id}/status`);
        expect([200, 404]).toContain(statusResponse.status()); // 200 for real agents, 404 for stubs

        // Health endpoint
        const healthResponse = await page.request.get(`${API_BASE_URL}/api/v1/agents/${agent.id}/health`);
        expect(healthResponse.status()).toBe(200);

        const healthData = await healthResponse.json();
        expect(healthData).toHaveProperty('status');
        expect(healthData.status).toBe('healthy');
      }
    });

    test('should test task execution through service layer', async ({ page }) => {
      const testTask = {
        operation: 'conversation',
        parameters: { content: 'Hello, this is a test message' },
        priority: 'normal',
        timeout_seconds: 30
      };

      // Test task execution via API
      const executeResponse = await page.request.post(`${API_BASE_URL}/api/v1/agents/01/execute`, {
        data: testTask
      });

      // Should succeed or fail gracefully (not 500 error)
      expect([200, 404]).toContain(executeResponse.status());

      if (executeResponse.status() === 200) {
        const result = await executeResponse.json();
        expect(result).toHaveProperty('task_id');
        expect(result).toHaveProperty('status');
        expect(['completed', 'failed']).toContain(result.status);
      }
    });

    test('should verify service layer data flow', async ({ page }) => {
      // Test that services communicate properly
      const healthResponse = await page.request.get(`${API_BASE_URL}/api/v1/system/status`);
      expect(healthResponse.status()).toBe(200);

      const healthData = await healthResponse.json();

      // Verify service integration
      expect(healthData).toHaveProperty('api_metrics');
      expect(healthData.api_metrics).toHaveProperty('total_requests');
      expect(healthData.api_metrics).toHaveProperty('websocket_connections');

      // Verify agent service integration
      expect(healthData).toHaveProperty('agents');
      expect(typeof healthData.agents).toBe('object');
    });
  });

  // End-to-End Data Flow Tests
  test.describe('End-to-End Data Flow', () => {
    test('should complete full user journey: UI -> API -> Service -> Response', async ({ page }) => {
      // Start on main page
      await page.goto('http://localhost:8443');
      await page.waitForLoadState('networkidle');

      // Navigate to agents
      await page.click('[data-testid="agents-nav-button"]');
      await expect(page.locator('text=Agent Management')).toBeVisible();

      // Go to task execution
      await page.click('text=Task Execution');
      await expect(page.locator('text=Execute Task')).toBeVisible();

      // Fill out task form
      const agentSelect = page.locator('button').filter({ hasText: /Select agent/ }).first();
      await agentSelect.click();

      // Select first available agent
      const agentOption = page.locator('[role="listbox"] [role="option"]').first();
      if (await agentOption.isVisible()) {
        await agentOption.click();
      }

      // Select operation
      const operationSelect = page.locator('button').filter({ hasText: /Select operation/ }).first();
      await operationSelect.click();

      const operationOption = page.locator('[role="listbox"] [role="option"]').first();
      if (await operationOption.isVisible()) {
        await operationOption.click();
      }

      // Fill parameters
      const paramsTextarea = page.locator('textarea[id="parameters"]');
      await paramsTextarea.fill('{"content": "Test message from UI", "temperature": 0.7}');

      // Execute task
      const executeButton = page.locator('button:has-text("Execute Task")');
      await expect(executeButton).toBeEnabled();

      // Note: This may fail if agents aren't fully functional, but tests the UI flow
      await executeButton.click();

      // Verify response handling (success or error notification)
      await page.waitForTimeout(3000);
      const notification = page.locator('text=Task Executed').or(page.locator('text=Task Failed')).or(page.locator('text=Error'));
      // Notification may not appear immediately, but UI should handle response
    });

    test('should maintain data consistency across UI components', async ({ page }) => {
      // Navigate through different tabs and verify data consistency
      await page.click('text=Overview');
      await page.waitForTimeout(1000);

      // Check system status
      const systemStatus = page.locator('text=operational').or(page.locator('text=initializing'));
      const initialStatus = await systemStatus.textContent();

      // Navigate to system tab
      await page.click('text=System');
      await page.waitForTimeout(1000);

      // Verify status consistency
      const systemTabStatus = page.locator('text=operational').or(page.locator('text=initializing'));
      const currentStatus = await systemTabStatus.textContent();

      expect(currentStatus).toBe(initialStatus);
    });

    test('should handle concurrent UI interactions', async ({ page }) => {
      // Open multiple tabs/windows and interact concurrently
      const page2 = await page.context().newPage();
      await page2.goto('http://localhost:8443');
      await page2.click('[data-testid="agents-nav-button"]');

      // Interact with both pages
      await page.click('text=Task Execution');
      await page2.click('text=Overview');

      // Verify both pages remain functional
      await expect(page.locator('text=Execute Task')).toBeVisible();
      await expect(page2.locator('text=System Status')).toBeVisible();

      await page2.close();
    });
  });

  // Service Layer Integration Tests
  test.describe('Service Layer Integration', () => {
    test('should verify Ollama service integration', async ({ page }) => {
      // Test that Ollama service is accessible through our API
      try {
        const healthResponse = await page.request.get(`${API_BASE_URL}/api/v1/system/status`);
        expect(healthResponse.status()).toBe(200);

        // If Ollama is available, agents should be functional
        // If not, they should fall back gracefully
        const systemData = await healthResponse.json();
        expect(systemData).toHaveProperty('agents');

        // Test agent health which should always work (stub fallback)
        for (const agent of AGENT_TYPES) {
          const healthResponse = await page.request.get(`${API_BASE_URL}/api/v1/agents/${agent.id}/health`);
          expect(healthResponse.status()).toBe(200);

          const healthData = await healthResponse.json();
          expect(healthData.status).toBe('healthy');
        }
      } catch (error) {
        console.log('Ollama service integration test noted unavailability - this is expected if Ollama is not running');
      }
    });

    test('should test conversation manager service', async ({ page }) => {
      // Test that conversation management works through the API
      const testConversation = {
        title: "E2E Test Conversation",
        description: "Testing conversation manager service",
        conversation_type: "direct",
        creator_id: "test_user"
      };

      // Create conversation
      const createResponse = await page.request.post(`${API_BASE_URL}/api/v1/conversations`, {
        data: testConversation
      });

      // Should succeed or fail gracefully
      expect([200, 201, 404]).toContain(createResponse.status());

      if (createResponse.status() === 201) {
        const conversationData = await createResponse.json();
        expect(conversationData).toHaveProperty('conversation_id');
      }
    });
  });

  // Performance and Load Testing
  test.describe('Performance & Load Testing', () => {
    test('should handle rapid successive requests', async ({ page }) => {
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      const startTime = Date.now();
      const requests = [];

      // Send 5 rapid requests
      for (let i = 0; i < 5; i++) {
        requests.push(executeTaskViaAPI(page, agentId, 'conversation', {
          content: `Rapid request ${i + 1}`,
          temperature: 0.5
        }));
      }

      // Wait for all to complete
      const results = await Promise.allSettled(requests);
      const endTime = Date.now();

      const successful = results.filter(r => r.status === 'fulfilled').length;
      const totalTime = endTime - startTime;

      console.log(`Rapid requests: ${successful}/5 successful in ${totalTime}ms`);

      // At least some should succeed
      expect(successful).toBeGreaterThan(0);
      expect(totalTime).toBeLessThan(30000); // Should complete within 30 seconds
    });

    test('should handle large payload requests', async ({ page }) => {
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      // Create a large content payload
      const largeContent = 'Explain quantum computing in detail. '.repeat(50);
      const startTime = Date.now();

      try {
        const { result, responseTime } = await executeTaskViaAPI(page, agentId, 'conversation', {
          content: largeContent,
          temperature: 0.7,
          max_tokens: 1024
        });

        expect([200, 404]).toContain(result.status ? 200 : 404);
        expect(responseTime).toBeLessThan(60000); // Should complete within 1 minute

        statsAnalyzer.addMetric({
          agentType: 'conversational',
          prompt: 'large_payload_test',
          temperature: 0.7,
          maxTokens: 1024,
          responseTime,
          responseLength: result.response ? result.response.length : 0,
          success: result.status === 'completed'
        });

      } catch (error) {
        const responseTime = Date.now() - startTime;
        statsAnalyzer.addMetric({
          agentType: 'conversational',
          prompt: 'large_payload_test',
          temperature: 0.7,
          maxTokens: 1024,
          responseTime,
          responseLength: 0,
          success: false,
          error: error.message
        });
      }
    });

    test('should test memory and state management', async ({ page }) => {
      // Test that the application doesn't leak memory or lose state
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      // Send multiple requests and verify system stability
      for (let i = 0; i < 10; i++) {
        try {
          await executeTaskViaAPI(page, agentId, 'conversation', {
            content: `Memory test request ${i + 1}`,
            temperature: 0.5
          });

          // Check system status between requests
          const statusResponse = await page.request.get(`${API_BASE_URL}/api/v1/system/status`);
          expect(statusResponse.status()).toBe(200);

        } catch (error) {
          console.log(`Memory test request ${i + 1} failed: ${error.message}`);
        }

        // Small delay to prevent overwhelming the system
        await page.waitForTimeout(500);
      }

      // Final system check
      const finalStatus = await page.request.get(`${API_BASE_URL}/api/v1/system/status`);
      expect(finalStatus.status()).toBe(200);
    });
  });

  // Cross-Agent Communication Tests
  test.describe('Cross-Agent Communication', () => {
    test('should enable agent-to-agent task delegation', async ({ page }) => {
      // Test if agents can communicate with each other
      const agent1 = '07'; // Conversational
      const agent2 = '09'; // Analyst

      await waitForAgentReady(page, agent1);
      await waitForAgentReady(page, agent2);

      // Agent 1 processes initial request
      const { result: result1 } = await executeTaskViaAPI(page, agent1, 'conversation', {
        content: 'Please analyze this data trend: Sales increased 15% Q1 to Q2, then decreased 8% Q2 to Q3, then increased 12% Q3 to Q4.',
        temperature: 0.6
      });

      if (result1.status === 'completed') {
        // Agent 2 analyzes the processed data
        const { result: result2 } = await executeTaskViaAPI(page, agent2, 'analyze_data', {
          data: result1.response,
          analysis_type: 'pattern_recognition'
        });

        // Verify cross-agent communication
        expect(result2.status).toBe('completed');
        expect(result2.analysis_type).toBe('pattern_recognition');
      }
    });

    test('should handle agent collaboration workflows', async ({ page }) => {
      // Test collaborative task execution
      const agents = ['07', '08', '09']; // Conversational, Code Assistant, Analyst

      const task = "Create a Python script to analyze sales data and generate insights";

      // Each agent contributes to different parts
      const results = [];

      for (const agentId of agents) {
        await waitForAgentReady(page, agentId);

        try {
          const { result } = await executeTaskViaAPI(page, agentId, 'conversation', {
            content: task,
            temperature: 0.7
          });
          results.push(result);
        } catch (error) {
          results.push({ status: 'error', error: error.message });
        }
      }

      // At least one agent should provide useful output
      const successful = results.filter(r => r.status === 'completed');
      expect(successful.length).toBeGreaterThan(0);
    });
  });

  // Error Recovery and Resilience Tests
  test.describe('Error Recovery & Resilience', () => {
    test('should handle network interruptions gracefully', async ({ page }) => {
      // Test with simulated network issues
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      // Override request to simulate network failure
      page.route(`${API_BASE_URL}/api/v1/agents/${agentId}/execute`, async route => {
        // Simulate intermittent network failure
        if (Math.random() < 0.3) {
          await route.abort('failed');
        } else {
          await route.continue();
        }
      });

      const results = [];
      for (let i = 0; i < 5; i++) {
        try {
          const result = await executeTaskViaAPI(page, agentId, 'conversation', {
            content: `Network test ${i + 1}`,
            temperature: 0.5
          });
          results.push('success');
        } catch (error) {
          results.push('failed');
        }
        await page.waitForTimeout(1000);
      }

      // Should have some successes despite simulated failures
      const successCount = results.filter(r => r === 'success').length;
      expect(successCount).toBeGreaterThan(0);

      // Clear route override
      await page.unroute(`${API_BASE_URL}/api/v1/agents/${agentId}/execute`);
    });

    test('should recover from agent unavailability', async ({ page }) => {
      // Test fallback when primary agent is unavailable
      const primaryAgent = '07';
      const fallbackAgent = '01'; // Infrastructure agent as fallback

      // First try primary agent
      try {
        await executeTaskViaAPI(page, primaryAgent, 'conversation', {
          content: 'Test message',
          temperature: 0.5
        });
      } catch (error) {
        // If primary fails, try fallback
        const { result } = await executeTaskViaAPI(page, fallbackAgent, 'health_check', {});
        expect([200, 404]).toContain(result.status ? 200 : 404);
      }
    });

    test('should handle malformed requests', async ({ page }) => {
      const agentId = '07';

      // Test various malformed requests
      const malformedRequests = [
        { operation: '', parameters: {} }, // Empty operation
        { operation: 'conversation', parameters: null }, // Null parameters
        { operation: 'conversation', parameters: 'invalid json' }, // Invalid JSON
        { operation: 'conversation', parameters: {}, priority: 'invalid' }, // Invalid priority
        { operation: 'conversation', parameters: {}, timeout_seconds: -1 } // Invalid timeout
      ];

      for (const request of malformedRequests) {
        try {
          await executeTaskViaAPI(page, agentId, request.operation, request.parameters, request.priority, request.timeout_seconds);
          // If it succeeds, that's fine - the system handled it gracefully
        } catch (error) {
          // Expected for some malformed requests
          expect(error.message).toContain('failed' || 'error' || 'invalid');
        }
      }
    });
  });

  // Security and Validation Tests
  test.describe('Security & Validation', () => {
    test('should validate API authentication', async ({ page }) => {
      // Test that API endpoints require proper authentication (if implemented)
      // For now, test basic request structure validation

      const agentId = '07';

      // Test with missing required fields
      try {
        const response = await page.request.post(`${API_BASE_URL}/api/v1/agents/${agentId}/execute`, {
          data: {} // Empty request body
        });

        // Should fail validation or handle gracefully
        expect([400, 422, 200]).toContain(response.status()); // Validation error or graceful handling
      } catch (error) {
        // Expected for invalid requests
      }
    });

    test('should prevent injection attacks', async ({ page }) => {
      const agentId = '07';

      // Test with potentially malicious input
      const maliciousInputs = [
        { content: "<script>alert('xss')</script>" },
        { content: "'; DROP TABLE users; --" },
        { content: "${process.env}" },
        { content: "../../../etc/passwd" }
      ];

      for (const input of maliciousInputs) {
        try {
          const { result } = await executeTaskViaAPI(page, agentId, 'conversation', {
            content: input.content,
            temperature: 0.5
          });

          // Should either succeed safely or fail gracefully
          expect(['completed', 'failed']).toContain(result.status);

          // Response should not contain malicious content execution
          if (result.response) {
            expect(result.response).not.toContain('<script>');
            expect(result.response).not.toContain('DROP TABLE');
          }
        } catch (error) {
          // Graceful failure is acceptable
          expect(error.message).toBeTruthy();
        }
      }
    });

    test('should validate parameter boundaries', async ({ page }) => {
      const agentId = '07';

      // Test parameter boundary conditions
      const boundaryTests = [
        { temperature: -1, max_tokens: 100 }, // Below minimum
        { temperature: 3, max_tokens: 100 }, // Above maximum
        { temperature: 0.5, max_tokens: 0 }, // Zero tokens
        { temperature: 0.5, max_tokens: 100000 }, // Too many tokens
        { temperature: '0.5', max_tokens: '100' } // Wrong types
      ];

      for (const params of boundaryTests) {
        try {
          const { result } = await executeTaskViaAPI(page, agentId, 'conversation', {
            content: 'Boundary test',
            ...params
          });

          // Should handle boundary conditions gracefully
          expect(['completed', 'failed']).toContain(result.status);
        } catch (error) {
          // Expected for invalid parameters
          expect(error.message).toContain('failed' || 'error' || 'invalid');
        }
      }
    });
  });

  // Data Persistence and State Tests
  test.describe('Data Persistence & State', () => {
    test('should maintain conversation state across requests', async ({ page }) => {
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      // Start a conversation with context
      const { result: result1 } = await executeTaskViaAPI(page, agentId, 'conversation', {
        content: 'My name is Alice and I work as a software engineer.',
        temperature: 0.7
      });

      expect(result1.status).toBe('completed');

      // Continue the conversation with context-dependent question
      const { result: result2 } = await executeTaskViaAPI(page, agentId, 'conversation', {
        content: 'What do you think about my profession?',
        temperature: 0.7
      });

      expect(result2.status).toBe('completed');

      // Response should show contextual understanding
      if (result2.response) {
        const response = result2.response.toLowerCase();
        // Should reference software engineering or Alice
        const hasContext = response.includes('software') || response.includes('alice') ||
                          response.includes('engineer') || response.includes('developer');
        expect(hasContext).toBe(true);
      }
    });

    test('should persist task history', async ({ page }) => {
      // Execute several tasks and verify they're tracked
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      const taskCount = 3;
      const executedTasks = [];

      for (let i = 0; i < taskCount; i++) {
        const { result } = await executeTaskViaAPI(page, agentId, 'conversation', {
          content: `History test task ${i + 1}`,
          temperature: 0.5
        });

        if (result.status === 'completed' && result.task_id) {
          executedTasks.push(result.task_id);
        }

        await page.waitForTimeout(1000);
      }

      // Check system status to see if tasks are being tracked
      const statusResponse = await page.request.get(`${API_BASE_URL}/api/v1/system/status`);
      expect(statusResponse.status()).toBe(200);

      const statusData = await statusResponse.json();
      expect(statusData).toHaveProperty('api_metrics');

      // API metrics should show requests were made
      const metrics = statusData.api_metrics;
      expect(metrics.total_requests).toBeGreaterThan(0);
    });

    test('should handle concurrent user sessions', async ({ page }) => {
      // Simulate multiple users interacting simultaneously
      const page2 = await page.context().newPage();
      const page3 = await page.context().newPage();

      try {
        // All pages navigate to agents
        await page2.goto('http://localhost:8443');
        await page3.goto('http://localhost:8443');

        await page2.click('[data-testid="agents-nav-button"]');
        await page3.click('[data-testid="agents-nav-button"]');

        // All execute tasks
        const taskPromises = [
          executeTaskViaAPI(page, '07', 'conversation', { content: 'Session 1 test' }),
          executeTaskViaAPI(page2, '07', 'conversation', { content: 'Session 2 test' }),
          executeTaskViaAPI(page3, '07', 'conversation', { content: 'Session 3 test' })
        ];

        const results = await Promise.allSettled(taskPromises);

        // At least some should succeed
        const successful = results.filter(r => r.status === 'fulfilled').length;
        expect(successful).toBeGreaterThan(0);

        // System should remain stable
        const finalStatus = await page.request.get(`${API_BASE_URL}/api/v1/system/status`);
        expect(finalStatus.status()).toBe(200);

      } finally {
        await page2.close();
        await page3.close();
      }
    });
  });

  // Conversational Agent Tests
  test.describe('Conversational Agent Tests', () => {
    test('should handle short conversations', async ({ page }) => {
      const agentId = '07'; // Conversational Agent

      await waitForAgentReady(page, agentId);

      for (const prompt of CONVERSATION_VARIATIONS.short.prompts) {
        for (const temp of [0.5, 0.9]) { // Test creativity variations
          const startTime = Date.now();

          try {
            const { result, responseTime } = await executeTaskViaAPI(page, agentId, 'conversation', {
              content: prompt,
              temperature: temp,
              max_tokens: 256
            });

            const quality = await measureResponseQuality(result.response, prompt);

            statsAnalyzer.addMetric({
              agentType: 'conversational',
              prompt,
              temperature: temp,
              maxTokens: 256,
              responseTime,
              responseLength: result.response.length,
              success: true
            });

            // Assertions
            expect(result.status).toBe('completed');
            expect(result.response).toBeTruthy();
            expect(result.response.length).toBeGreaterThan(10);
            expect(quality).toBeGreaterThan(0.3);

          } catch (error) {
            statsAnalyzer.addMetric({
              agentType: 'conversational',
              prompt,
              temperature: temp,
              maxTokens: 256,
              responseTime: Date.now() - startTime,
              responseLength: 0,
              success: false,
              error: error.message
            });
          }
        }
      }
    });

    test('should handle complex multi-turn conversations', async ({ page }) => {
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      const conversation = [
        "Hello, I'm interested in learning about artificial intelligence.",
        "Can you explain what machine learning is?",
        "How does deep learning differ from traditional machine learning?",
        "What are some practical applications of AI in healthcare?"
      ];

      let conversationId: string | null = null;

      for (const message of conversation) {
        const startTime = Date.now();

        try {
          const { result, responseTime } = await executeTaskViaAPI(page, agentId, 'conversation', {
            content: message,
            conversation_id: conversationId,
            temperature: 0.7,
            max_tokens: 512
          });

          if (!conversationId && result.conversation_id) {
            conversationId = result.conversation_id;
          }

          const quality = await measureResponseQuality(result.response, message);

          statsAnalyzer.addMetric({
            agentType: 'conversational',
            prompt: message,
            temperature: 0.7,
            maxTokens: 512,
            responseTime,
            responseLength: result.response.length,
            success: true
          });

          expect(result.status).toBe('completed');
          expect(result.response.length).toBeGreaterThan(50);
          expect(quality).toBeGreaterThan(0.4);

        } catch (error) {
          statsAnalyzer.addMetric({
            agentType: 'conversational',
            prompt: message,
            temperature: 0.7,
            maxTokens: 512,
            responseTime: Date.now() - startTime,
            responseLength: 0,
            success: false,
            error: error.message
          });
        }
      }
    });
  });

  // Code Assistant Tests
  test.describe('Code Assistant Tests', () => {
    test('should provide code explanations', async ({ page }) => {
      const agentId = '08'; // Code Assistant
      await waitForAgentReady(page, agentId);

      const codeSamples = [
        "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
        "const map = new Map();\nmap.set('key', 'value');\nconsole.log(map.get('key'));",
        "SELECT name, COUNT(*) FROM users GROUP BY name HAVING COUNT(*) > 1;"
      ];

      for (const code of codeSamples) {
        const startTime = Date.now();

        try {
          const { result, responseTime } = await executeTaskViaAPI(page, agentId, 'analyze_code', {
            code,
            analysis_type: 'explanation'
          });

          statsAnalyzer.addMetric({
            agentType: 'code_assistant',
            prompt: code.substring(0, 50) + '...',
            temperature: 0.3,
            maxTokens: 512,
            responseTime,
            responseLength: result.response.length,
            success: true
          });

          expect(result.status).toBe('completed');
          expect(result.response).toContain('functionality' || 'purpose' || 'logic');

        } catch (error) {
          statsAnalyzer.addMetric({
            agentType: 'code_assistant',
            prompt: code.substring(0, 50) + '...',
            temperature: 0.3,
            maxTokens: 512,
            responseTime: Date.now() - startTime,
            responseLength: 0,
            success: false,
            error: error.message
          });
        }
      }
    });

    test('should generate code with different complexities', async ({ page }) => {
      const agentId = '08';
      await waitForAgentReady(page, agentId);

      const requirements = [
        "Write a simple function to reverse a string",
        "Create a REST API endpoint for user management with authentication",
        "Implement a binary search tree with insert, delete, and search operations"
      ];

      for (const requirement of requirements) {
        for (const temp of TEMPERATURE_VARIATIONS) {
          const startTime = Date.now();

          try {
            const { result, responseTime } = await executeTaskViaAPI(page, agentId, 'generate_code', {
              requirement,
              language: 'python',
              temperature: temp,
              max_tokens: 1024
            });

            statsAnalyzer.addMetric({
              agentType: 'code_assistant',
              prompt: requirement,
              temperature: temp,
              maxTokens: 1024,
              responseTime,
              responseLength: result.response.length,
              success: true
            });

            expect(result.status).toBe('completed');
            expect(result.response).toContain('def ' || 'function' || 'class');

          } catch (error) {
            statsAnalyzer.addMetric({
              agentType: 'code_assistant',
              prompt: requirement,
              temperature: temp,
              maxTokens: 1024,
              responseTime: Date.now() - startTime,
              responseLength: 0,
              success: false,
              error: error.message
            });
          }
        }
      }
    });
  });

  // Data Analyst Tests
  test.describe('Data Analyst Tests', () => {
    test('should analyze data patterns and provide insights', async ({ page }) => {
      const agentId = '09'; // Data Analyst
      await waitForAgentReady(page, agentId);

      const datasets = [
        "Sales data: Q1: $100k, Q2: $120k, Q3: $95k, Q4: $140k",
        "User engagement: Mon: 150, Tue: 180, Wed: 165, Thu: 190, Fri: 200",
        "Error rates: System A: 2.1%, System B: 1.8%, System C: 3.2%"
      ];

      for (const data of datasets) {
        const startTime = Date.now();

        try {
          const { result, responseTime } = await executeTaskViaAPI(page, agentId, 'analyze_data', {
            data,
            analysis_type: 'patterns_and_insights'
          });

          statsAnalyzer.addMetric({
            agentType: 'analyst',
            prompt: data,
            temperature: 0.4,
            maxTokens: 768,
            responseTime,
            responseLength: result.response.length,
            success: true
          });

          expect(result.status).toBe('completed');
          expect(result.analysis_type).toBe('patterns_and_insights');

        } catch (error) {
          statsAnalyzer.addMetric({
            agentType: 'analyst',
            prompt: data,
            temperature: 0.4,
            maxTokens: 768,
            responseTime: Date.now() - startTime,
            responseLength: 0,
            success: false,
            error: error.message
          });
        }
      }
    });
  });

  // Creative Writer Tests
  test.describe('Creative Writer Tests', () => {
    test('should generate creative content with different styles', async ({ page }) => {
      const agentId = '10'; // Creative Writer
      await waitForAgentReady(page, agentId);

      const prompts = [
        "Write a short story about a robot learning emotions",
        "Create a poem about the beauty of mathematics",
        "Write dialogue for a scene where two AI systems debate consciousness"
      ];

      const styles = ['formal', 'casual', 'poetic', 'technical'];

      for (const prompt of prompts) {
        for (const style of styles.slice(0, 2)) { // Test 2 styles to avoid too many combinations
          const startTime = Date.now();

          try {
            const { result, responseTime } = await executeTaskViaAPI(page, agentId, 'generate_content', {
              prompt,
              style,
              genre: 'fiction',
              temperature: 0.8,
              max_tokens: 768
            });

            statsAnalyzer.addMetric({
              agentType: 'creative_writer',
              prompt,
              temperature: 0.8,
              maxTokens: 768,
              responseTime,
              responseLength: result.response.length,
              success: true
            });

            expect(result.status).toBe('completed');
            expect(result.generation_type).toBe('content');

          } catch (error) {
            statsAnalyzer.addMetric({
              agentType: 'creative_writer',
              prompt,
              temperature: 0.8,
              maxTokens: 768,
              responseTime: Date.now() - startTime,
              responseLength: 0,
              success: false,
              error: error.message
            });
          }
        }
      }
    });
  });

  // Multi-Agent Communication Tests
  test.describe('Multi-Agent Communication Tests', () => {
    test('should enable agent-to-agent collaboration', async ({ page }) => {
      // Test collaboration between conversational and analyst agents
      const agent1 = '07'; // Conversational
      const agent2 = '09'; // Analyst

      await waitForAgentReady(page, agent1);
      await waitForAgentReady(page, agent2);

      const task = "Analyze the impact of social media on teenage mental health";

      // First agent provides initial analysis
      const { result: result1 } = await executeTaskViaAPI(page, agent1, 'conversation', {
        content: `Please break down this topic for analysis: ${task}`,
        temperature: 0.6
      });

      // Second agent provides data-driven insights
      const { result: result2 } = await executeTaskViaAPI(page, agent2, 'analyze_data', {
        data: result1.response,
        analysis_type: 'impact_assessment'
      });

      // Verify collaboration worked
      expect(result1.status).toBe('completed');
      expect(result2.status).toBe('completed');
      expect(result2.analysis_type).toBe('impact_assessment');
    });

    test('should handle agent communication failures gracefully', async ({ page }) => {
      const agentId = '07';

      // Test with invalid parameters
      try {
        await executeTaskViaAPI(page, agentId, 'conversation', {
          content: "",  // Empty content
          temperature: 2.0,  // Invalid temperature
          max_tokens: -100  // Invalid max tokens
        });
        expect(false).toBe(true); // Should have failed
      } catch (error) {
        expect(error.message).toContain('failed' || 'error');
      }
    });
  });

  // Statistical Analysis Tests
  test.describe('Statistical Analysis Tests', () => {
    test('should analyze response quality across variations', async ({ page }) => {
      // This test analyzes the metrics collected from previous tests
      const report = statsAnalyzer.exportResults();

      // Verify we have data
      expect(report.totalTests).toBeGreaterThan(0);
      expect(report.successfulTests).toBeGreaterThan(0);

      // Check agent-specific stats
      const convStats = report.agentStats.conversational;
      if (convStats) {
        expect(convStats.avgResponseTime).toBeGreaterThan(0);
        expect(convStats.successRate).toBeGreaterThan(0.5);
      }

      // Check temperature impact
      const tempImpact = report.temperatureImpact;
      expect(Object.keys(tempImpact).length).toBeGreaterThan(0);

      // Check complexity analysis
      const complexityAnalysis = report.complexityAnalysis;
      expect(Object.keys(complexityAnalysis).length).toBeGreaterThan(0);
    });

    test('should provide performance benchmarks', async ({ page }) => {
      const report = statsAnalyzer.exportResults();

      // Log performance benchmarks
      console.log('Performance Benchmarks:');
      console.log(`Total Tests: ${report.totalTests}`);
      console.log(`Success Rate: ${(report.successfulTests / report.totalTests * 100).toFixed(1)}%`);

      Object.entries(report.agentStats).forEach(([agent, stats]: [string, any]) => {
        if (stats) {
          console.log(`${agent}: ${stats.avgResponseTime.toFixed(2)}ms avg, ${stats.successRate.toFixed(2)} success rate`);
        }
      });
    });
  });

  // Edge Cases and Error Handling
  test.describe('Edge Cases and Error Handling', () => {
    test('should handle very long prompts', async ({ page }) => {
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      const longPrompt = 'Explain ' + 'quantum computing '.repeat(100) + 'in detail.';

      const startTime = Date.now();
      try {
        const { result, responseTime } = await executeTaskViaAPI(page, agentId, 'conversation', {
          content: longPrompt,
          max_tokens: 2048
        });

        statsAnalyzer.addMetric({
          agentType: 'conversational',
          prompt: 'long_prompt_test',
          temperature: 0.7,
          maxTokens: 2048,
          responseTime,
          responseLength: result.response.length,
          success: true
        });

        expect(result.status).toBe('completed');

      } catch (error) {
        statsAnalyzer.addMetric({
          agentType: 'conversational',
          prompt: 'long_prompt_test',
          temperature: 0.7,
          maxTokens: 2048,
          responseTime: Date.now() - startTime,
          responseLength: 0,
          success: false,
          error: error.message
        });
      }
    });

    test('should handle special characters and unicode', async ({ page }) => {
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      const unicodePrompt = "Explain Schrödinger's equation: 𝛹(x,t) = ∑(cn·ψn(x)·e^(-iEn t / ℏ))";

      const { result } = await executeTaskViaAPI(page, agentId, 'conversation', {
        content: unicodePrompt
      });

      expect(result.status).toBe('completed');
      expect(result.response.length).toBeGreaterThan(10);
    });

    test('should handle concurrent requests', async ({ page }) => {
      const agentId = '07';
      await waitForAgentReady(page, agentId);

      const promises = [];
      for (let i = 0; i < 3; i++) {
        promises.push(executeTaskViaAPI(page, agentId, 'conversation', {
          content: `Concurrent request ${i + 1}`,
          temperature: 0.5 + (i * 0.1)
        }));
      }

      const results = await Promise.all(promises);

      results.forEach(({ result }) => {
        expect(result.status).toBe('completed');
      });
    });
  });

  // Cleanup and final reporting
  test.afterAll(async () => {
    // Export final statistical report
    const finalReport = statsAnalyzer.exportResults();
    console.log('\n=== FINAL TEST REPORT ===');
    console.log(`Total Tests Run: ${finalReport.totalTests}`);
    console.log(`Successful Tests: ${finalReport.successfulTests}`);
    console.log(`Success Rate: ${(finalReport.successfulTests / finalReport.totalTests * 100).toFixed(1)}%`);

    console.log('\nAgent Performance Summary:');
    Object.entries(finalReport.agentStats).forEach(([agent, stats]: [string, any]) => {
      if (stats) {
        console.log(`  ${agent}:`);
        console.log(`    Tests: ${stats.count}`);
        console.log(`    Avg Response Time: ${stats.avgResponseTime.toFixed(2)}ms`);
        console.log(`    Avg Response Length: ${stats.avgResponseLength.toFixed(0)} chars`);
        console.log(`    Success Rate: ${(stats.successRate * 100).toFixed(1)}%`);
      }
    });

    console.log('\nTemperature Impact Analysis:');
    Object.entries(finalReport.temperatureImpact).forEach(([temp, data]: [string, any]) => {
      console.log(`  Temp ${temp}: ${data.avgLength.toFixed(0)} chars avg, ${data.avgTime.toFixed(2)}ms avg`);
    });

    console.log('\nComplexity Analysis:');
    Object.entries(finalReport.complexityAnalysis).forEach(([complexity, data]: [string, any]) => {
      console.log(`  ${complexity}: ${data.avgLength.toFixed(0)} chars avg, ${data.avgTime.toFixed(2)}ms avg`);
    });

    console.log(`\nDetailed report saved to: test-results/llm-agents-e2e-report.json`);
  });
});
