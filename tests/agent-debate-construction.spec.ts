/**
 * Agent Debate Construction E2E Tests
 *
 * Comprehensive Playwright tests for constructing two agents to debate a conversation.
 * Tests cover the complete workflow from agent creation to debate initialization and execution.
 *
 * Test Strategy:
 * - Component-level testing for individual UI interactions
 * - Integration testing for agent creation workflow
 * - End-to-end testing for complete debate construction
 * - Error handling and edge case testing
 * - Accessibility testing with keyboard navigation
 * - Performance testing for agent operations
 * - Cross-browser compatibility testing
 */

import { BrowserContext, expect, Page, test } from '@playwright/test'
import { AgentDebateTestHelper } from './helpers/agent-debate-test-helper'

// Test configuration
const TEST_CONFIG = {
  baseUrl: process.env.TEST_BASE_URL || 'http://localhost:8449',
  apiUrl: process.env.TEST_API_URL || 'http://localhost:8443',
  timeout: 60000,
  retries: 2,
  workers: 1, // Sequential execution for state-dependent tests
}

// Test data fixtures
const TEST_AGENTS = {
  logicalAnalyst: {
    type: 'logical_analyst',
    name: 'Test Logical Analyst',
    template: 'custom',
    capabilities: ['ANALYSIS', 'LOGIC'],
    parameters: {
      reasoning_depth: 3,
      evidence_threshold: 0.8,
      max_fallacies: 2
    }
  },
  creativeInnovator: {
    type: 'creative_innovator',
    name: 'Test Creative Innovator',
    template: 'custom',
    capabilities: ['CREATIVITY', 'INNOVATION'],
    parameters: {
      creativity_weight: 0.9,
      risk_tolerance: 0.7,
      novelty_threshold: 0.6
    }
  }
}

const TEST_DEBATE = {
  topic: 'The Impact of Artificial Intelligence on Human Employment',
  problemStatement: `As AI systems become increasingly sophisticated, there is growing debate about their impact on human employment. Some argue that AI will create new opportunities and enhance productivity, while others fear widespread job displacement and economic disruption. Consider the following aspects:

1. Historical precedents of technological unemployment
2. The nature of AI capabilities vs human skills
3. Economic adaptation and retraining possibilities
4. Societal and ethical implications
5. Potential for new job creation in AI-related fields

Debate the potential outcomes and propose balanced approaches to managing this transition.`,
  mode: 'structured',
  maxRounds: 3,
  consensusThreshold: 0.75,
  rules: {
    allow_ad_hominem: false,
    require_evidence: true,
    enable_fact_checking: true,
    allow_creativity: true,
    enforce_formality: true,
    evidence_threshold: 0.7,
    creativity_weight: 0.4,
    max_fallacies_per_argument: 1
  }
}

// Test helper class
class AgentDebateTestHelper {
  private page: Page
  private context: BrowserContext

  constructor(page: Page, context: BrowserContext) {
    this.page = page
    this.context = context
  }

  // Navigation helpers
  async navigateToAgentsTab() {
    await this.page.goto(TEST_CONFIG.baseUrl)
    await this.page.click('[data-testid="agents-tab"]')
    await this.page.waitForSelector('[data-testid="agents-content"]')
  }

  async navigateToDebateSystem() {
    await this.page.click('[data-testid="debate-tab"]')
    await this.page.waitForSelector('[data-testid="debate-system"]')
  }

  // Agent creation helpers
  async createAgent(agentConfig: typeof TEST_AGENTS.logicalAnalyst) {
    // Open create agent modal
    await this.page.click('[data-testid="create-agent-btn"]')
    await this.page.waitForSelector('[data-testid="create-agent-modal"]')

    // Select agent template
    await this.page.selectOption('[data-testid="agent-template-select"]', agentConfig.template)

    // Fill agent details
    await this.page.fill('[data-testid="agent-name-input"]', agentConfig.name)
    await this.page.selectOption('[data-testid="agent-type-select"]', agentConfig.type)

    // Configure capabilities
    for (const capability of agentConfig.capabilities) {
      await this.page.check(`[data-testid="capability-${capability}"]`)
    }

    // Configure parameters
    for (const [param, value] of Object.entries(agentConfig.parameters)) {
      if (typeof value === 'number') {
        await this.page.fill(`[data-testid="param-${param}"]`, value.toString())
      } else if (typeof value === 'boolean') {
        if (value) {
          await this.page.check(`[data-testid="param-${param}"]`)
        } else {
          await this.page.uncheck(`[data-testid="param-${param}"]`)
        }
      }
    }

    // Submit agent creation
    await this.page.click('[data-testid="create-agent-submit"]')

    // Wait for success notification
    await this.page.waitForSelector('[data-testid="notification-success"]')

    // Return agent ID from notification or API response
    const notification = await this.page.locator('[data-testid="notification-success"]').textContent()
    const agentIdMatch = notification?.match(/Agent (\w+) created successfully/)
    return agentIdMatch ? agentIdMatch[1] : null
  }

  // Debate setup helpers
  async setupDebateConfiguration(debateConfig: typeof TEST_DEBATE) {
    // Navigate to debate setup
    await this.navigateToDebateSystem()
    await this.page.click('[data-testid="debate-setup-tab"]')

    // Fill debate configuration
    await this.page.fill('[data-testid="debate-topic-input"]', debateConfig.topic)
    await this.page.fill('[data-testid="debate-problem-textarea"]', debateConfig.problemStatement)
    await this.page.selectOption('[data-testid="debate-mode-select"]', debateConfig.mode)
    await this.page.fill('[data-testid="max-rounds-input"]', debateConfig.maxRounds.toString())
    await this.page.fill('[data-testid="consensus-threshold-input"]', debateConfig.consensusThreshold.toString())

    // Configure debate rules
    await this.page.click('[data-testid="advanced-rules-toggle"]')

    for (const [rule, value] of Object.entries(debateConfig.rules)) {
      if (typeof value === 'boolean') {
        if (value) {
          await this.page.check(`[data-testid="rule-${rule}"]`)
        } else {
          await this.page.uncheck(`[data-testid="rule-${rule}"]`)
        }
      } else if (typeof value === 'number') {
        await this.page.fill(`[data-testid="rule-${rule}"]`, value.toString())
      }
    }
  }

  async selectDebateAgents(agentIds: string[]) {
    for (const agentId of agentIds) {
      await this.page.check(`[data-testid="agent-select-${agentId}"]`)
    }
  }

  async initializeDebate() {
    await this.page.click('[data-testid="initialize-debate-btn"]')
    await this.page.waitForSelector('[data-testid="debate-active"]')
  }

  // Monitoring and validation helpers
  async waitForWebSocketConnection() {
    await this.page.waitForSelector('[data-testid="websocket-connected"]')
  }

  async verifyAgentHealth(agentId: string) {
    const healthIndicator = this.page.locator(`[data-testid="agent-health-${agentId}"]`)
    await expect(healthIndicator).toHaveAttribute('data-health', 'healthy')
  }

  async verifyOllamaConnection() {
    await this.page.waitForSelector('[data-testid="ollama-connected"]')
    const status = await this.page.locator('[data-testid="ollama-status"]').textContent()
    expect(status).toContain('connected')
  }

  async captureDebateMetrics() {
    const metrics = await this.page.evaluate(() => {
      return {
        roundNumber: document.querySelector('[data-testid="current-round"]')?.textContent,
        consensusScore: document.querySelector('[data-testid="consensus-score"]')?.textContent,
        argumentsCount: document.querySelectorAll('[data-testid="debate-argument"]').length,
        activeParticipants: document.querySelectorAll('[data-testid="active-participant"]').length,
      }
    })
    return metrics
  }
}

// Global test setup
test.describe.configure({
  mode: 'serial',
  timeout: TEST_CONFIG.timeout,
  retries: TEST_CONFIG.retries,
})

let testHelper: AgentDebateTestHelper

test.beforeEach(async ({ page, context }) => {
  testHelper = new AgentDebateTestHelper(page, context)

  // Set up API mocking for consistent test environment
  await context.route('**/api/v1/agents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        agents: [
          { id: '01', type: 'infrastructure', capabilities: ['MONITORING'] },
          { id: '02', type: 'database', capabilities: ['ANALYSIS'] },
          { id: '11', type: 'logical_analyst', capabilities: ['ANALYSIS', 'LOGIC'] },
          { id: '17', type: 'creative_innovator', capabilities: ['CREATIVITY'] }
        ]
      })
    })
  })

  // Mock Ollama models endpoint
  await context.route('**/api/v1/ollama/models', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        models: [
          { name: 'llama2:13b', size: '13.0 GB', modified_at: new Date().toISOString() },
          { name: 'mistral:7b', size: '4.1 GB', modified_at: new Date().toISOString() },
          { name: 'codellama:13b', size: '13.0 GB', modified_at: new Date().toISOString() }
        ],
        status: 'connected'
      })
    })
  })
})

test.describe('Agent Management System - Ollama Integration', () => {
  test('should verify Ollama service connectivity and model availability', async ({ page }) => {
    await testHelper.navigateToAgentsTab()

    // Check Ollama connection status
    await testHelper.verifyOllamaConnection()

    // Verify model loading
    await page.click('[data-testid="ollama-models-btn"]')
    await page.waitForSelector('[data-testid="model-list"]')

    const modelCount = await page.locator('[data-testid="model-item"]').count()
    expect(modelCount).toBeGreaterThan(0)

    // Verify model details are displayed
    const firstModel = page.locator('[data-testid="model-item"]').first()
    await expect(firstModel).toContainText('llama2:13b')
    await expect(firstModel).toContainText('GB') // Size information
  })

  test('should handle Ollama service disconnection gracefully', async ({ page, context }) => {
    // Mock Ollama service failure
    await context.route('**/api/v1/ollama/models', async (route) => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Ollama service unavailable',
          status: 'disconnected'
        })
      })
    })

    await testHelper.navigateToAgentsTab()

    // Should show disconnected state
    await page.waitForSelector('[data-testid="ollama-disconnected"]')

    // Should show error notification
    await page.waitForSelector('[data-testid="notification-error"]')
    const notification = await page.locator('[data-testid="notification-error"]').textContent()
    expect(notification).toContain('Ollama service unavailable')
  })
})

test.describe('Agent Creation Workflow', () => {
  test('should create a logical analyst agent successfully', async ({ page }) => {
    await testHelper.navigateToAgentsTab()

    const agentId = await testHelper.createAgent(TEST_AGENTS.logicalAnalyst)
    expect(agentId).toBeTruthy()

    // Verify agent appears in agent list
    await page.waitForSelector(`[data-testid="agent-card-${agentId}"]`)

    // Verify agent health
    await testHelper.verifyAgentHealth(agentId!)

    // Verify agent capabilities
    const capabilities = await page.locator(`[data-testid="agent-capabilities-${agentId}"]`).textContent()
    expect(capabilities).toContain('ANALYSIS')
    expect(capabilities).toContain('LOGIC')
  })

  test('should create a creative innovator agent successfully', async ({ page }) => {
    await testHelper.navigateToAgentsTab()

    const agentId = await testHelper.createAgent(TEST_AGENTS.creativeInnovator)
    expect(agentId).toBeTruthy()

    // Verify agent appears in agent list
    await page.waitForSelector(`[data-testid="agent-card-${agentId}"]`)

    // Verify agent health
    await testHelper.verifyAgentHealth(agentId!)

    // Verify agent capabilities
    const capabilities = await page.locator(`[data-testid="agent-capabilities-${agentId}"]`).textContent()
    expect(capabilities).toContain('CREATIVITY')
  })

  test('should validate agent creation form inputs', async ({ page }) => {
    await testHelper.navigateToAgentsTab()

    // Open create agent modal
    await page.click('[data-testid="create-agent-btn"]')

    // Try to submit without required fields
    await page.click('[data-testid="create-agent-submit"]')

    // Should show validation errors
    await page.waitForSelector('[data-testid="validation-error-name"]')
    await page.waitForSelector('[data-testid="validation-error-type"]')

    // Fill required fields and verify errors disappear
    await page.fill('[data-testid="agent-name-input"]', 'Test Agent')
    await page.selectOption('[data-testid="agent-type-select"]', 'logical_analyst')

    // Validation errors should disappear
    await expect(page.locator('[data-testid="validation-error-name"]')).not.toBeVisible()
    await expect(page.locator('[data-testid="validation-error-type"]')).not.toBeVisible()
  })

  test('should handle agent creation errors gracefully', async ({ page, context }) => {
    // Mock agent creation failure
    await context.route('**/api/v1/agents/*/execute', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'Agent creation failed',
          status: 'failed'
        })
      })
    })

    await testHelper.navigateToAgentsTab()

    // Attempt to create agent
    await page.click('[data-testid="create-agent-btn"]')
    await page.fill('[data-testid="agent-name-input"]', 'Failing Agent')
    await page.selectOption('[data-testid="agent-type-select"]', 'logical_analyst')
    await page.click('[data-testid="create-agent-submit"]')

    // Should show error notification
    await page.waitForSelector('[data-testid="notification-error"]')
    const notification = await page.locator('[data-testid="notification-error"]').textContent()
    expect(notification).toContain('Agent creation failed')
  })
})

test.describe('Debate Construction and Execution', () => {
  let logicalAgentId: string | null
  let creativeAgentId: string | null

  test.beforeAll(async ({ page }) => {
    await testHelper.navigateToAgentsTab()

    // Create test agents
    logicalAgentId = await testHelper.createAgent(TEST_AGENTS.logicalAnalyst)
    creativeAgentId = await testHelper.createAgent(TEST_AGENTS.creativeInnovator)
  })

  test('should configure debate with custom rules and agents', async ({ page }) => {
    await testHelper.setupDebateConfiguration(TEST_DEBATE)

    // Select the created agents for debate
    await testHelper.selectDebateAgents([logicalAgentId!, creativeAgentId!])

    // Verify agent selection
    await expect(page.locator(`[data-testid="selected-agent-${logicalAgentId}"]`)).toBeChecked()
    await expect(page.locator(`[data-testid="selected-agent-${creativeAgentId}"]`)).toBeChecked()

    // Verify debate rules configuration
    await expect(page.locator('[data-testid="rule-require_evidence"]')).toBeChecked()
    await expect(page.locator('[data-testid="rule-enable_fact_checking"]')).toBeChecked()
    await expect(page.locator('[data-testid="rule-allow_creativity"]')).toBeChecked()

    // Verify rule values
    const evidenceThreshold = await page.locator('[data-testid="rule-evidence_threshold"]').inputValue()
    expect(evidenceThreshold).toBe('0.7')
  })

  test('should initialize debate session successfully', async ({ page }) => {
    await testHelper.initializeDebate()

    // Verify debate session is active
    await page.waitForSelector('[data-testid="debate-session-active"]')

    // Verify session details
    const topic = await page.locator('[data-testid="debate-topic-display"]').textContent()
    expect(topic).toContain(TEST_DEBATE.topic)

    // Verify participants
    const participantCount = await page.locator('[data-testid="debate-participant"]').count()
    expect(participantCount).toBe(2) // Two agents selected

    // Verify initial metrics
    const metrics = await testHelper.captureDebateMetrics()
    expect(metrics.roundNumber).toBe('1')
    expect(metrics.consensusScore).toBe('0.00')
    expect(metrics.activeParticipants).toBe(2)
  })

  test('should execute debate rounds with agent interactions', async ({ page }) => {
    // Start the debate
    await page.click('[data-testid="start-debate-btn"]')

    // Wait for first round to complete
    await page.waitForSelector('[data-testid="round-1-complete"]', { timeout: 30000 })

    // Verify arguments were generated
    const initialMetrics = await testHelper.captureDebateMetrics()
    expect(initialMetrics.argumentsCount).toBeGreaterThan(0)

    // Wait for second round
    await page.waitForSelector('[data-testid="round-2-active"]', { timeout: 30000 })

    // Verify ongoing debate progress
    const progressMetrics = await testHelper.captureDebateMetrics()
    expect(progressMetrics.roundNumber).toBe('2')
    expect(progressMetrics.argumentsCount).toBeGreaterThan(initialMetrics.argumentsCount)

    // Verify agent interactions (rebuttals, counter-arguments)
    const rebuttalElements = await page.locator('[data-testid="argument-rebuttal"]').count()
    expect(rebuttalElements).toBeGreaterThan(0)
  })

  test('should display real-time debate analytics', async ({ page }) => {
    // Switch to analysis tab
    await page.click('[data-testid="debate-analysis-tab"]')

    // Verify analytics components are present
    await page.waitForSelector('[data-testid="debate-analytics"]')

    // Check agent performance metrics
    const logicalAgentMetrics = await page.locator(`[data-testid="agent-metrics-${logicalAgentId}"]`)
    await expect(logicalAgentMetrics).toContainText('Logical Analyst')

    const creativeAgentMetrics = await page.locator(`[data-testid="agent-metrics-${creativeAgentId}"]`)
    await expect(creativeAgentMetrics).toContainText('Creative Innovator')

    // Verify argument quality indicators
    const qualityIndicators = await page.locator('[data-testid="argument-quality"]').count()
    expect(qualityIndicators).toBeGreaterThan(0)

    // Check consensus tracking
    const consensusChart = await page.locator('[data-testid="consensus-chart"]')
    await expect(consensusChart).toBeVisible()
  })

  test('should handle debate interruption and recovery', async ({ page }) => {
    // Pause the debate
    await page.click('[data-testid="pause-debate-btn"]')
    await page.waitForSelector('[data-testid="debate-paused"]')

    // Resume debate
    await page.click('[data-testid="resume-debate-btn"]')
    await page.waitForSelector('[data-testid="debate-active"]')

    // Verify debate continues from where it left off
    const metrics = await testHelper.captureDebateMetrics()
    expect(metrics.roundNumber).toBeGreaterThan('1')
  })

  test('should complete debate and show final results', async ({ page }) => {
    // Wait for debate completion
    await page.waitForSelector('[data-testid="debate-completed"]', { timeout: 60000 })

    // Verify final results
    const finalMetrics = await testHelper.captureDebateMetrics()
    expect(finalMetrics.consensusScore).toBeGreaterThan('0.00')

    // Check winner determination or consensus reached
    const consensusElement = await page.locator('[data-testid="debate-consensus"]')
    await expect(consensusElement).toBeVisible()

    // Verify comprehensive debate summary
    await page.waitForSelector('[data-testid="debate-summary"]')
    const summary = await page.locator('[data-testid="debate-summary"]').textContent()
    expect(summary).toContain('debate')
    expect(summary).toContain('conclusion')
  })
})

test.describe('Accessibility and Keyboard Navigation', () => {
  test('should support full keyboard navigation for agent creation', async ({ page }) => {
    await testHelper.navigateToAgentsTab()

    // Focus management test
    await page.keyboard.press('Tab')
    const activeElement = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'))
    expect(activeElement).toBe('create-agent-btn')

    // Open modal with keyboard
    await page.keyboard.press('Enter')
    await page.waitForSelector('[data-testid="create-agent-modal"]')

    // Navigate form with Tab
    await page.keyboard.press('Tab')
    const firstInput = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'))
    expect(firstInput).toBe('agent-name-input')

    // Fill form with keyboard
    await page.keyboard.type('Test Keyboard Agent')
    await page.keyboard.press('Tab')

    // Select agent type with keyboard
    await page.keyboard.press('ArrowDown')
    await page.keyboard.press('Enter')

    // Submit form
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')

    // Verify success notification
    await page.waitForSelector('[data-testid="notification-success"]')
  })

  test('should support keyboard navigation for debate setup', async ({ page }) => {
    await testHelper.navigateToDebateSystem()

    // Navigate to setup tab
    await page.keyboard.press('Tab')
    await page.keyboard.press('ArrowRight') // Navigate to debate tab
    await page.keyboard.press('Enter')

    // Navigate setup form
    await page.keyboard.press('Tab')
    const topicInput = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'))
    expect(topicInput).toBe('debate-topic-input')

    // Fill debate topic
    await page.keyboard.type(TEST_DEBATE.topic)
    await page.keyboard.press('Tab')

    // Navigate to agent selection
    await page.keyboard.press('Tab')
    const agentCheckbox = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'))
    expect(agentCheckbox?.startsWith('agent-select-')).toBe(true)

    // Select agents with spacebar
    await page.keyboard.press('Space')
    await page.keyboard.press('Tab')
    await page.keyboard.press('Space')
  })
})

test.describe('Performance and Error Handling', () => {
  test('should handle network timeouts gracefully', async ({ page, context }) => {
    // Mock slow network response
    await context.route('**/api/v1/agents/*/execute', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 35000)) // Longer than timeout
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'completed' })
      })
    })

    await testHelper.navigateToAgentsTab()

    // Attempt operation that will timeout
    await page.click('[data-testid="agent-action-btn"]')

    // Should show timeout error
    await page.waitForSelector('[data-testid="notification-error"]')
    const notification = await page.locator('[data-testid="notification-error"]').textContent()
    expect(notification).toContain('timeout')
  })

  test('should handle WebSocket reconnection', async ({ page }) => {
    await testHelper.navigateToAgentsTab()
    await testHelper.waitForWebSocketConnection()

    // Simulate WebSocket disconnection
    await page.evaluate(() => {
      // Force WebSocket disconnection
      const ws = (window as any).testWebSocket
      if (ws) ws.close()
    })

    // Should show disconnection notification
    await page.waitForSelector('[data-testid="notification-warning"]')

    // Should attempt reconnection
    await page.waitForSelector('[data-testid="websocket-reconnecting"]')

    // Should eventually reconnect
    await page.waitForSelector('[data-testid="websocket-connected"]')
  })

  test('should maintain state during page refresh', async ({ page }) => {
    await testHelper.navigateToAgentsTab()

    // Create an agent
    const agentId = await testHelper.createAgent(TEST_AGENTS.logicalAnalyst)

    // Refresh page
    await page.reload()
    await testHelper.navigateToAgentsTab()

    // Agent should still be present
    await page.waitForSelector(`[data-testid="agent-card-${agentId}"]`)
    await expect(page.locator(`[data-testid="agent-card-${agentId}"]`)).toBeVisible()
  })
})

test.describe('Cross-browser Compatibility', () => {
  test('should work correctly in different browsers', async ({ page, browserName }) => {
    // Skip this test if not running cross-browser
    test.skip(browserName === 'chromium', 'Cross-browser test')

    await testHelper.navigateToAgentsTab()

    // Basic functionality test
    await page.click('[data-testid="create-agent-btn"]')
    await page.waitForSelector('[data-testid="create-agent-modal"]')

    // Verify modal is accessible
    const modal = await page.locator('[data-testid="create-agent-modal"]')
    await expect(modal).toBeVisible()

    // Test keyboard navigation
    await page.keyboard.press('Escape')
    await expect(modal).not.toBeVisible()
  })
})

// Performance tests
test.describe('Performance Tests', () => {
  test('should load agent management interface within performance budget', async ({ page }) => {
    const startTime = Date.now()

    await page.goto(TEST_CONFIG.baseUrl)
    await page.click('[data-testid="agents-tab"]')

    // Wait for content to load
    await page.waitForSelector('[data-testid="agents-content"]')

    const loadTime = Date.now() - startTime
    expect(loadTime).toBeLessThan(3000) // 3 second budget
  })

  test('should handle multiple concurrent agent operations', async ({ page }) => {
    await testHelper.navigateToAgentsTab()

    // Create multiple agents concurrently
    const createPromises = [
      testHelper.createAgent({...TEST_AGENTS.logicalAnalyst, name: 'Agent 1'}),
      testHelper.createAgent({...TEST_AGENTS.creativeInnovator, name: 'Agent 2'}),
      testHelper.createAgent({...TEST_AGENTS.logicalAnalyst, name: 'Agent 3'})
    ]

    const startTime = Date.now()
    const agentIds = await Promise.all(createPromises)
    const totalTime = Date.now() - startTime

    // Should complete within reasonable time
    expect(totalTime).toBeLessThan(15000) // 15 seconds for 3 concurrent operations

    // All agents should be created
    for (const agentId of agentIds) {
      expect(agentId).toBeTruthy()
      await page.waitForSelector(`[data-testid="agent-card-${agentId}"]`)
    }
  })

  test('should maintain smooth debate execution performance', async ({ page }) => {
    // Setup debate with performance monitoring
    await testHelper.setupDebateConfiguration(TEST_DEBATE)
    await testHelper.selectDebateAgents(['agent1', 'agent2'])
    await testHelper.initializeDebate()

    const startTime = Date.now()
    await page.click('[data-testid="start-debate-btn"]')

    // Monitor first round completion
    await page.waitForSelector('[data-testid="round-1-complete"]', { timeout: 30000 })
    const roundTime = Date.now() - startTime

    // First round should complete within reasonable time
    expect(roundTime).toBeLessThan(25000) // 25 seconds

    // Monitor memory usage (if browser supports it)
    const memoryUsage = await page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0
    })

    // Memory usage should be reasonable (< 100MB)
    expect(memoryUsage).toBeLessThan(100 * 1024 * 1024)
  })
})

// Cleanup after all tests
test.afterAll(async ({ page }) => {
  // Clean up any test data
  await page.evaluate(() => {
    // Clear local storage, session storage, etc.
    localStorage.clear()
    sessionStorage.clear()
  })
})
