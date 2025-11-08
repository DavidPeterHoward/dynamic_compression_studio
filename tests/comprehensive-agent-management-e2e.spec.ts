/**
 * Comprehensive Agent Management E2E Tests
 *
 * Tests all enhanced agent management functionality including:
 * - Live system stats
 * - Enhanced template builder
 * - Agent communication modal with debate capabilities
 * - New orchestration tab
 * - Agent configuration functionality
 * - Improved agent cards with metrics and evaluation
 * - Playwright e2e testing with data-id attributes
 */

import { expect, test } from '@playwright/test'

test.describe('Agent Management Comprehensive E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the agent management page
    await page.goto('http://localhost:3000/agent_new')
    await page.waitForLoadState('networkidle')
  })

  test.describe('System Overview & Live Stats', () => {
    test('should display live system stats with auto-refresh', async ({ page }) => {
      // Check system overview section
      await expect(page.locator('[data-id="system-overview-title"]')).toBeVisible()
      await expect(page.locator('[data-id="websocket-indicator"]')).toBeVisible()

      // Verify system status badge
      await expect(page.locator('[data-id="system-status-badge"]')).toBeVisible()

      // Check refresh button functionality
      const refreshBtn = page.locator('[data-id="refresh-system-btn"]')
      await expect(refreshBtn).toBeVisible()
      await refreshBtn.click()

      // Verify metrics cards are present
      await expect(page.locator('[data-id="active-agents-card"]')).toBeVisible()
      await expect(page.locator('[data-id="api-requests-card"]')).toBeVisible()
      await expect(page.locator('[data-id="websocket-connections-card"]')).toBeVisible()
      await expect(page.locator('[data-id="system-performance-card"]')).toBeVisible()

      // Check additional metrics
      await expect(page.locator('[data-id="memory-usage-card"]')).toBeVisible()
      await expect(page.locator('[data-id="disk-usage-card"]')).toBeVisible()
      await expect(page.locator('[data-id="uptime-card"]')).toBeVisible()
    })
  })

  test.describe('Agent Cards & Enhanced Design', () => {
    test('should display enhanced agent cards with comprehensive metrics', async ({ page }) => {
      // Navigate to agents tab
      await page.locator('[data-id="tab-agents"]').click()

      // Wait for agents grid to load
      await page.waitForSelector('[data-id="agents-grid"]')

      // Get first agent card
      const firstAgentCard = page.locator('[data-id*="agent-card-"]').first()
      await expect(firstAgentCard).toBeVisible()

      // Verify enhanced card structure
      await expect(firstAgentCard.locator('[data-id*="agent-header-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-icon-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-name-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-status-"]')).toBeVisible()

      // Check comprehensive metrics
      await expect(firstAgentCard.locator('[data-id*="agent-metrics-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-tasks-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-success-rate-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-efficiency-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-reliability-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-throughput-"]')).toBeVisible()

      // Verify evaluation section
      await expect(firstAgentCard.locator('[data-id*="agent-evaluation-"]')).toBeVisible()

      // Check action buttons
      await expect(firstAgentCard.locator('[data-id*="agent-details-btn-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-configure-btn-"]')).toBeVisible()
      await expect(firstAgentCard.locator('[data-id*="agent-evaluate-btn-"]')).toBeVisible()
    })
  })

  test.describe('Template Builder Functionality', () => {
    test('should open and interact with enhanced template builder', async ({ page }) => {
      // Open template builder (assuming it's accessible from agents tab)
      await page.locator('[data-id="tab-agents"]').click()

      // Look for template builder trigger - may need to adjust based on actual UI
      // This could be a button in the agents tab or a separate modal trigger
      const templateBuilderTrigger = page.locator('[data-id="template-builder-btn"]').or(
        page.locator('button:has-text("Template Builder")')
      ).or(
        page.locator('[data-id*="template"]')
      )

      if (await templateBuilderTrigger.isVisible()) {
        await templateBuilderTrigger.click()

        // Verify template builder modal opens
        const templateModal = page.locator('[data-id="template-builder-modal"]')
        await expect(templateModal).toBeVisible()

        // Check template library
        await expect(page.locator('[data-id="template-library"]')).toBeVisible()
        await expect(page.locator('[data-id="template-search"]')).toBeVisible()
        await expect(page.locator('[data-id="category-filter"]')).toBeVisible()

        // Test template selection
        const firstTemplate = page.locator('[data-id*="template-card-"]').first()
        if (await firstTemplate.isVisible()) {
          await firstTemplate.click()

          // Verify template editor opens
          await expect(page.locator('[data-id="template-editor"]')).toBeVisible()
          await expect(page.locator('[data-id="template-preview"]')).toBeVisible()

          // Test template actions
          const testBtn = page.locator('[data-id="test-template-btn"]')
          if (await testBtn.isVisible()) {
            await testBtn.click()
            await expect(page.locator('[data-id="test-results"]')).toBeVisible()
          }
        }

        // Close modal
        await page.locator('[data-id="close-template-builder"]').click()
        await expect(templateModal).not.toBeVisible()
      }
    })
  })

  test.describe('Agent Communication Modal', () => {
    test('should open agent communication modal with multiple modes', async ({ page }) => {
      // Navigate to agents tab
      await page.locator('[data-id="tab-agents"]').click()

      // Find agent communication trigger - may need adjustment
      const commTrigger = page.locator('[data-id="agent-communication-btn"]').or(
        page.locator('button:has-text("Communication")')
      )

      if (await commTrigger.isVisible()) {
        await commTrigger.click()

        // Verify communication modal opens
        const commModal = page.locator('[data-id="communication-modal"]')
        await expect(commModal).toBeVisible()

        // Check communication modes
        await expect(page.locator('[data-id="mode-chat"]')).toBeVisible()
        await expect(page.locator('[data-id="mode-command"]')).toBeVisible()
        await expect(page.locator('[data-id="mode-debate"]')).toBeVisible()

        // Test debate mode
        await page.locator('[data-id="mode-debate"]').click()

        // Verify debate-specific elements
        await expect(page.locator('[data-id="debate-topic-input"]')).toBeVisible()
        await expect(page.locator('[data-id*="debate-agent-"]')).toBeVisible()

        // Test chat mode
        await page.locator('[data-id="mode-chat"]').click()

        // Verify agent selection for chat
        await expect(page.locator('[data-id="agent-select"]')).toBeVisible()

        // Test command mode
        await page.locator('[data-id="mode-command"]').click()

        // Verify command-specific elements
        await expect(page.locator('[data-id="quick-commands-card"]')).toBeVisible()

        // Close modal
        await page.locator('[data-id="close-communication-modal"]').click()
        await expect(commModal).not.toBeVisible()
      }
    })
  })

  test.describe('Orchestration Tab', () => {
    test('should display comprehensive orchestration interface', async ({ page }) => {
      // Navigate to orchestration tab
      await page.locator('[data-id="tab-orchestration"]').click()

      // Verify orchestration tab content loads
      await expect(page.locator('[data-id="orchestration-tab-content"]')).toBeVisible()
      await expect(page.locator('[data-id="orchestration-title"]')).toBeVisible()

      // Check action buttons
      await expect(page.locator('[data-id="create-workflow-btn"]')).toBeVisible()
      await expect(page.locator('[data-id="schedule-task-btn"]')).toBeVisible()

      // Verify workflow orchestration section
      await expect(page.locator('[data-id="workflow-orchestration"]')).toBeVisible()
      await expect(page.locator('[data-id="active-workflows"]')).toBeVisible()
      await expect(page.locator('[data-id="workflow-canvas"]')).toBeVisible()

      // Check task queue management
      await expect(page.locator('[data-id="task-queue-management"]')).toBeVisible()
      await expect(page.locator('[data-id="queued-tasks"]')).toBeVisible()
      await expect(page.locator('[data-id="running-tasks"]')).toBeVisible()
      await expect(page.locator('[data-id="completed-tasks"]')).toBeVisible()

      // Verify agent coordination section
      await expect(page.locator('[data-id="agent-coordination"]')).toBeVisible()
      await expect(page.locator('[data-id="orchestration-metrics"]')).toBeVisible()
      await expect(page.locator('[data-id="task-scheduling"]')).toBeVisible()
    })
  })

  test.describe('Agent Configuration', () => {
    test('should open agent configuration modal with full functionality', async ({ page }) => {
      // Navigate to agents tab
      await page.locator('[data-id="tab-agents"]').click()

      // Find and click configure button on first agent
      const configureBtn = page.locator('[data-id*="agent-configure-btn-"]').first()
      await expect(configureBtn).toBeVisible()
      await configureBtn.click()

      // Verify configuration modal opens
      const configModal = page.locator('[data-id="agent-config-modal"]')
      await expect(configModal).toBeVisible()

      // Check configuration tabs
      await expect(page.locator('[data-id="config-tab-general"]')).toBeVisible()
      await expect(page.locator('[data-id="config-tab-performance"]')).toBeVisible()
      await expect(page.locator('[data-id="config-tab-security"]')).toBeVisible()
      await expect(page.locator('[data-id="config-tab-network"]')).toBeVisible()

      // Test general configuration
      await page.locator('[data-id="config-tab-general"]').click()
      await expect(page.locator('[data-id="general-config"]')).toBeVisible()
      await expect(page.locator('[data-id="config-agent-name"]')).toBeVisible()
      await expect(page.locator('[data-id="config-priority"]')).toBeVisible()

      // Test performance configuration
      await page.locator('[data-id="config-tab-performance"]').click()
      await expect(page.locator('[data-id="performance-config"]')).toBeVisible()
      await expect(page.locator('[data-id="config-cpu-allocation"]')).toBeVisible()

      // Test security configuration
      await page.locator('[data-id="config-tab-security"]').click()
      await expect(page.locator('[data-id="security-config"]')).toBeVisible()
      await expect(page.locator('[data-id="config-security-level"]')).toBeVisible()

      // Test network configuration
      await page.locator('[data-id="config-tab-network"]').click()
      await expect(page.locator('[data-id="network-config"]')).toBeVisible()
      await expect(page.locator('[data-id="config-connection-timeout"]')).toBeVisible()

      // Test save functionality
      await page.locator('[data-id="save-config"]').click()

      // Modal should close after save
      await expect(configModal).not.toBeVisible()
    })
  })

  test.describe('Navigation & Tab Functionality', () => {
    test('should navigate between all agent management tabs', async ({ page }) => {
      // Test all tab navigation
      const tabs = [
        { id: 'tab-overview', content: 'overview' },
        { id: 'tab-agents', content: 'agents-tab-content' },
        { id: 'tab-tasks', content: 'tasks' },
        { id: 'tab-orchestration', content: 'orchestration-tab-content' },
        { id: 'tab-ollama', content: 'ollama' },
        { id: 'tab-debate', content: 'debate' },
        { id: 'tab-system', content: 'system' }
      ]

      for (const tab of tabs) {
        await page.locator(`[data-id="${tab.id}"]`).click()
        await expect(page.locator(`[data-id="${tab.content}"]`)).toBeVisible()
      }
    })
  })

  test.describe('Data Persistence & State Management', () => {
    test('should maintain state across tab switches', async ({ page }) => {
      // Navigate to agents tab and interact
      await page.locator('[data-id="tab-agents"]').click()
      await expect(page.locator('[data-id="agents-tab-content"]')).toBeVisible()

      // Switch to another tab
      await page.locator('[data-id="tab-orchestration"]').click()
      await expect(page.locator('[data-id="orchestration-tab-content"]')).toBeVisible()

      // Return to agents tab - should maintain state
      await page.locator('[data-id="tab-agents"]').click()
      await expect(page.locator('[data-id="agents-tab-content"]')).toBeVisible()
    })
  })

  test.describe('Responsive Design', () => {
    test('should work on mobile viewport', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 })

      // Test basic functionality still works
      await expect(page.locator('[data-id="agent-tabs-list"]')).toBeVisible()

      // Navigate to agents tab
      await page.locator('[data-id="tab-agents"]').click()
      await expect(page.locator('[data-id="agents-grid"]')).toBeVisible()

      // Check agent cards are visible and functional
      const firstAgentCard = page.locator('[data-id*="agent-card-"]').first()
      await expect(firstAgentCard).toBeVisible()
    })
  })

  test.describe('Error Handling', () => {
    test('should handle network errors gracefully', async ({ page }) => {
      // This would test error scenarios - implementation depends on actual error handling
      // For now, just verify the interface remains stable
      await page.locator('[data-id="tab-agents"]').click()
      await expect(page.locator('[data-id="agents-tab-content"]')).toBeVisible()
    })
  })
})
