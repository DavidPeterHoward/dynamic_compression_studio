/**
 * Agent Debate Test Helper
 *
 * Comprehensive helper class for testing agent debate construction workflows.
 * Provides utilities for setting up test scenarios, mocking responses,
 * and validating complex multi-agent interactions.
 */

import { BrowserContext, expect, Page } from '@playwright/test'

export interface AgentConfig {
  id?: string
  type: string
  name: string
  template: string
  capabilities: string[]
  parameters: Record<string, any>
  health?: 'healthy' | 'warning' | 'error'
  status?: 'idle' | 'working' | 'error' | 'initializing' | 'shutdown' | 'degraded'
}

export interface DebateConfig {
  topic: string
  problemStatement: string
  mode: 'structured' | 'freeform' | 'autonomous'
  maxRounds: number
  consensusThreshold: number
  rules: {
    allow_ad_hominem: boolean
    require_evidence: boolean
    enable_fact_checking: boolean
    allow_creativity: boolean
    enforce_formality: boolean
    evidence_threshold: number
    creativity_weight: number
    max_fallacies_per_argument: number
  }
}

export interface MockResponse {
  status?: number
  contentType?: string
  body?: string | object
  headers?: Record<string, string>
  delay?: number
}

export class AgentDebateTestHelper {
  private page: Page
  private context: BrowserContext
  private createdAgents: Map<string, AgentConfig> = new Map()
  private activeDebates: Map<string, DebateConfig> = new Map()

  constructor(page: Page, context: BrowserContext) {
    this.page = page
    this.context = context
  }

  // Navigation helpers
  async navigateToAgentsTab(): Promise<void> {
    await this.page.goto(process.env.TEST_BASE_URL || 'http://localhost:8449')
    await this.page.click('[data-testid="agents-nav-button"]', { timeout: 10000 })
    await this.page.waitForSelector('[data-testid="agents-content"]', { timeout: 10000 })
  }

  async navigateToDebateSystem(): Promise<void> {
    // Debate system is a tab within the Agents tab
    await this.page.click('[data-testid="debate-tab"]', { timeout: 5000 })
    await this.page.waitForSelector('[data-testid="debate-system"]', { timeout: 10000 })
  }

  // Agent management helpers
  async createAgent(agentConfig: Omit<AgentConfig, 'id'>): Promise<string> {
    // Open create agent modal
    await this.page.click('[data-testid="create-agent-btn"]', { timeout: 5000 })
    await this.page.waitForSelector('[data-testid="create-agent-modal"]', { timeout: 5000 })

    // Select agent template
    await this.page.selectOption('[data-testid="agent-template-select"]', agentConfig.template, { timeout: 5000 })

    // Fill agent details
    await this.page.fill('[data-testid="agent-name-input"]', agentConfig.name, { timeout: 5000 })
    await this.page.selectOption('[data-testid="agent-type-select"]', agentConfig.type, { timeout: 5000 })

    // Configure capabilities
    for (const capability of agentConfig.capabilities) {
      await this.page.check(`[data-testid="capability-${capability}"]`, { timeout: 2000 })
    }

    // Configure parameters
    for (const [param, value] of Object.entries(agentConfig.parameters)) {
      const paramSelector = `[data-testid="param-${param}"]`
      if (typeof value === 'number') {
        await this.page.fill(paramSelector, value.toString(), { timeout: 2000 })
      } else if (typeof value === 'boolean') {
        if (value) {
          await this.page.check(paramSelector, { timeout: 2000 })
        } else {
          await this.page.uncheck(paramSelector, { timeout: 2000 })
        }
      } else if (typeof value === 'string') {
        await this.page.fill(paramSelector, value, { timeout: 2000 })
      }
    }

    // Submit agent creation
    await this.page.click('[data-testid="create-agent-submit"]', { timeout: 5000 })

    // Wait for success notification
    await this.page.waitForSelector('[data-testid="notification-success"]', { timeout: 10000 })

    // Extract agent ID from notification or response
    const notification = await this.page.locator('[data-testid="notification-success"]').textContent({ timeout: 5000 })
    const agentIdMatch = notification?.match(/Agent (\w+) created successfully/)
    const agentId = agentIdMatch ? agentIdMatch[1] : `test-agent-${Date.now()}`

    // Store created agent for cleanup
    this.createdAgents.set(agentId, { ...agentConfig, id: agentId })

    return agentId
  }

  async deleteAgent(agentId: string): Promise<void> {
    await this.page.click(`[data-testid="agent-delete-${agentId}"]`, { timeout: 5000 })
    await this.page.click('[data-testid="confirm-delete"]', { timeout: 5000 })
    await this.page.waitForSelector('[data-testid="notification-success"]', { timeout: 5000 })
    this.createdAgents.delete(agentId)
  }

  async verifyAgentExists(agentId: string): Promise<void> {
    await this.page.waitForSelector(`[data-testid="agent-card-${agentId}"]`, { timeout: 5000 })
    await expect(this.page.locator(`[data-testid="agent-card-${agentId}"]`)).toBeVisible()
  }

  async verifyAgentHealth(agentId: string, expectedHealth: 'healthy' | 'warning' | 'error' = 'healthy'): Promise<void> {
    const healthIndicator = this.page.locator(`[data-testid="agent-health-${agentId}"]`)
    await expect(healthIndicator).toHaveAttribute('data-health', expectedHealth, { timeout: 5000 })
  }

  // Debate setup helpers
  async setupDebateConfiguration(debateConfig: DebateConfig): Promise<void> {
    // Navigate to debate setup
    await this.navigateToDebateSystem()
    await this.page.click('[data-testid="debate-setup-tab"]', { timeout: 5000 })

    // Fill debate configuration
    await this.page.fill('[data-testid="debate-topic-input"]', debateConfig.topic, { timeout: 5000 })
    await this.page.fill('[data-testid="debate-problem-textarea"]', debateConfig.problemStatement, { timeout: 5000 })
    await this.page.selectOption('[data-testid="debate-mode-select"]', debateConfig.mode, { timeout: 5000 })
    await this.page.fill('[data-testid="max-rounds-input"]', debateConfig.maxRounds.toString(), { timeout: 5000 })
    await this.page.fill('[data-testid="consensus-threshold-input"]', debateConfig.consensusThreshold.toString(), { timeout: 5000 })

    // Configure debate rules
    await this.page.click('[data-testid="advanced-rules-toggle"]', { timeout: 5000 })

    for (const [rule, value] of Object.entries(debateConfig.rules)) {
      const ruleSelector = `[data-testid="rule-${rule}"]`
      if (typeof value === 'boolean') {
        if (value) {
          await this.page.check(ruleSelector, { timeout: 2000 })
        } else {
          await this.page.uncheck(ruleSelector, { timeout: 2000 })
        }
      } else if (typeof value === 'number') {
        await this.page.fill(ruleSelector, value.toString(), { timeout: 2000 })
      }
    }

    // Store debate config for validation
    this.activeDebates.set(debateConfig.topic, debateConfig)
  }

  async selectDebateAgents(agentIds: string[]): Promise<void> {
    for (const agentId of agentIds) {
      await this.page.check(`[data-testid="agent-select-${agentId}"]`, { timeout: 2000 })
    }
  }

  async initializeDebate(): Promise<string> {
    await this.page.click('[data-testid="initialize-debate-btn"]', { timeout: 5000 })
    await this.page.waitForSelector('[data-testid="debate-active"]', { timeout: 10000 })

    // Extract debate session ID
    const debateElement = await this.page.locator('[data-testid="debate-session-id"]').textContent()
    const sessionId = debateElement || `debate-session-${Date.now()}`

    return sessionId
  }

  // WebSocket and real-time helpers
  async waitForWebSocketConnection(timeout: number = 5000): Promise<void> {
    await this.page.waitForSelector('[data-testid="websocket-connected"]', { timeout })
  }

  async waitForWebSocketDisconnection(timeout: number = 5000): Promise<void> {
    await this.page.waitForSelector('[data-testid="websocket-disconnected"]', { timeout })
  }

  async verifyWebSocketMessage(expectedType: string, timeout: number = 5000): Promise<void> {
    await this.page.waitForSelector(`[data-testid="ws-message-${expectedType}"]`, { timeout })
  }

  // Ollama integration helpers
  async verifyOllamaConnection(): Promise<void> {
    await this.page.waitForSelector('[data-testid="ollama-connected"]', { timeout: 5000 })
    const status = await this.page.locator('[data-testid="ollama-status"]').textContent()
    expect(status).toContain('connected')
  }

  async loadOllamaModels(): Promise<string[]> {
    await this.page.click('[data-testid="ollama-models-btn"]', { timeout: 5000 })
    await this.page.waitForSelector('[data-testid="model-list"]', { timeout: 5000 })

    const modelElements = await this.page.locator('[data-testid="model-item"]').allTextContents()
    return modelElements
  }

  async selectOllamaModel(modelName: string): Promise<void> {
    await this.page.selectOption('[data-testid="ollama-model-select"]', modelName, { timeout: 5000 })
  }

  // Validation helpers
  async captureDebateMetrics(): Promise<{
    roundNumber: string
    consensusScore: string
    argumentsCount: number
    activeParticipants: number
    totalFallacies: number
    evidenceQuality: number
  }> {
    const metrics = await this.page.evaluate(() => {
      return {
        roundNumber: document.querySelector('[data-testid="current-round"]')?.textContent || '0',
        consensusScore: document.querySelector('[data-testid="consensus-score"]')?.textContent || '0.00',
        argumentsCount: document.querySelectorAll('[data-testid="debate-argument"]').length,
        activeParticipants: document.querySelectorAll('[data-testid="active-participant"]').length,
        totalFallacies: document.querySelectorAll('[data-testid="fallacy-indicator"]').length,
        evidenceQuality: parseFloat(document.querySelector('[data-testid="evidence-quality-score"]')?.textContent || '0'),
      }
    })
    return metrics
  }

  async verifyDebateRulesApplied(rules: Partial<DebateConfig['rules']>): Promise<void> {
    for (const [rule, expectedValue] of Object.entries(rules)) {
      if (typeof expectedValue === 'boolean') {
        const checkbox = this.page.locator(`[data-testid="rule-${rule}"]`)
        if (expectedValue) {
          await expect(checkbox).toBeChecked()
        } else {
          await expect(checkbox).not.toBeChecked()
        }
      } else if (typeof expectedValue === 'number') {
        const input = this.page.locator(`[data-testid="rule-${rule}"]`)
        const value = await input.inputValue()
        expect(parseFloat(value)).toBe(expectedValue)
      }
    }
  }

  // Mock and API helpers
  async mockApiResponse(url: string, response: MockResponse): Promise<void> {
    await this.context.route(url, async (route) => {
      if (response.delay) {
        await new Promise(resolve => setTimeout(resolve, response.delay))
      }

      await route.fulfill({
        status: response.status || 200,
        contentType: response.contentType || 'application/json',
        body: typeof response.body === 'object' ? JSON.stringify(response.body) : response.body,
        headers: response.headers,
      })
    })
  }

  async mockAgentCreationFailure(): Promise<void> {
    await this.mockApiResponse('**/api/v1/agents/*/execute', {
      status: 500,
      body: {
        error: 'Agent creation failed',
        status: 'failed'
      }
    })
  }

  async mockOllamaFailure(): Promise<void> {
    await this.mockApiResponse('**/api/v1/ollama/models', {
      status: 503,
      body: {
        error: 'Ollama service unavailable',
        status: 'disconnected'
      }
    })
  }

  async mockDebateInitializationFailure(): Promise<void> {
    await this.mockApiResponse('**/api/v1/debate/initialize', {
      status: 500,
      body: {
        error: 'Failed to initialize debate'
      }
    })
  }

  // Performance monitoring helpers
  async measurePageLoadTime(): Promise<number> {
    const startTime = Date.now()
    await this.page.waitForLoadState('networkidle', { timeout: 30000 })
    return Date.now() - startTime
  }

  async measureActionTime(action: () => Promise<void>): Promise<number> {
    const startTime = Date.now()
    await action()
    return Date.now() - startTime
  }

  async getMemoryUsage(): Promise<number> {
    return await this.page.evaluate(() => {
      return (performance as any).memory?.usedJSHeapSize || 0
    })
  }

  // Accessibility helpers
  async checkKeyboardNavigation(): Promise<void> {
    // Test Tab navigation
    await this.page.keyboard.press('Tab')
    let activeElement = await this.page.evaluate(() => document.activeElement?.getAttribute('data-testid'))
    expect(activeElement).toBeTruthy()

    // Test Enter key activation
    await this.page.keyboard.press('Enter')
    await this.page.waitForTimeout(500)

    // Test Escape key
    await this.page.keyboard.press('Escape')
    await this.page.waitForTimeout(500)
  }

  async checkScreenReaderSupport(): Promise<void> {
    // Check for ARIA labels
    const ariaLabels = await this.page.locator('[aria-label], [aria-labelledby]').count()
    expect(ariaLabels).toBeGreaterThan(0)

    // Check for proper heading structure
    const headings = await this.page.locator('h1, h2, h3, h4, h5, h6').count()
    expect(headings).toBeGreaterThan(0)
  }

  // Cleanup helpers
  async cleanupTestData(): Promise<void> {
    // Delete created agents
    for (const [agentId] of this.createdAgents) {
      try {
        await this.deleteAgent(agentId)
      } catch (error) {
        console.warn(`Failed to cleanup agent ${agentId}:`, error)
      }
    }
    this.createdAgents.clear()

    // Cleanup active debates (if any)
    for (const [debateId] of this.activeDebates) {
      try {
        await this.page.click(`[data-testid="debate-stop-${debateId}"]`, { timeout: 2000 })
      } catch (error) {
        console.warn(`Failed to cleanup debate ${debateId}:`, error)
      }
    }
    this.activeDebates.clear()
  }

  // Test assertion helpers
  async assertNotification(type: 'success' | 'error' | 'warning' | 'info', message?: string): Promise<void> {
    const selector = `[data-testid="notification-${type}"]`
    await this.page.waitForSelector(selector, { timeout: 5000 })

    if (message) {
      const notificationText = await this.page.locator(selector).textContent()
      expect(notificationText).toContain(message)
    }
  }

  async assertLoadingState(isLoading: boolean): Promise<void> {
    if (isLoading) {
      await this.page.waitForSelector('[data-testid="loading-spinner"]', { timeout: 2000 })
    } else {
      await this.page.waitForSelector('[data-testid="loading-spinner"]', { state: 'hidden', timeout: 2000 })
    }
  }

  async assertModalState(modalId: string, isOpen: boolean): Promise<void> {
    const modal = this.page.locator(`[data-testid="${modalId}"]`)
    if (isOpen) {
      await expect(modal).toBeVisible()
    } else {
      await expect(modal).not.toBeVisible()
    }
  }

  // Advanced test utilities
  async simulateNetworkDelay(delayMs: number): Promise<void> {
    await this.page.route('**/api/**', async (route) => {
      await new Promise(resolve => setTimeout(resolve, delayMs))
      await route.continue()
    })
  }

  async simulateWebSocketDisconnect(): Promise<void> {
    await this.page.evaluate(() => {
      // Force disconnect any active WebSocket connections
      const wsInstances = (window as any).activeWebSockets || []
      wsInstances.forEach((ws: WebSocket) => ws.close())
    })
  }

  async interceptAndModifyResponse(url: string, modifier: (data: any) => any): Promise<void> {
    await this.context.route(url, async (route) => {
      const response = await route.fetch()
      const json = await response.json()
      const modifiedJson = modifier(json)

      await route.fulfill({
        response,
        json: modifiedJson,
      })
    })
  }
}

// Utility functions for common test scenarios
export const createTestAgent = (overrides: Partial<AgentConfig> = {}): Omit<AgentConfig, 'id'> => ({
  type: 'logical_analyst',
  name: 'Test Agent',
  template: 'custom',
  capabilities: ['ANALYSIS', 'LOGIC'],
  parameters: {
    reasoning_depth: 3,
    evidence_threshold: 0.8,
    max_fallacies: 2
  },
  health: 'healthy',
  status: 'idle',
  ...overrides
})

export const createTestDebate = (overrides: Partial<DebateConfig> = {}): DebateConfig => ({
  topic: 'Test Debate Topic',
  problemStatement: 'Test problem statement for debate validation.',
  mode: 'structured',
  maxRounds: 2,
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
  },
  ...overrides
})

export const waitForCondition = async (
  condition: () => Promise<boolean>,
  timeout: number = 5000,
  interval: number = 100
): Promise<void> => {
  const startTime = Date.now()

  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return
    }
    await new Promise(resolve => setTimeout(resolve, interval))
  }

  throw new Error(`Condition not met within ${timeout}ms`)
}
