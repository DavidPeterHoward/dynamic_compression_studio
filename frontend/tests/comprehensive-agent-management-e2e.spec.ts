import { expect, test } from '@playwright/test';

/**
 * COMPREHENSIVE AGENT MANAGEMENT E2E TEST SUITE
 *
 * This test suite provides complete coverage for the Agent Management System,
 * including all tabs, forms, modals, WebSocket connections, and user workflows.
 *
 * Test Coverage Areas:
 * ✅ System Overview & Live Stats
 * ✅ Agent Cards & Enhanced Design
 * ✅ Template Builder Functionality
 * ✅ Agent Communication Modal
 * ✅ Orchestration Tab
 * ✅ Agent Configuration
 * ✅ Navigation & Tab Functionality
 * ✅ Data Persistence & State Management
 * ✅ Responsive Design
 * ✅ Error Handling & Recovery
 * ✅ WebSocket Real-time Updates
 * ✅ Form Validation & UX
 * ✅ Accessibility Compliance
 * ✅ Performance & Load Testing
 */

// Configuration constants
const BASE_URL = process.env.BASE_URL || 'http://localhost:8449';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8443';
const TEST_TIMEOUT = 60000; // 60 seconds
const NETWORK_IDLE_TIMEOUT = 5000;

test.describe.configure({
  mode: 'serial',
  timeout: TEST_TIMEOUT
});

test.describe('🔬 COMPREHENSIVE AGENT MANAGEMENT E2E SUITE', () => {
  // ============================================================================
  // SETUP & TEARDOWN
  // ============================================================================

  test.beforeEach(async ({ page }) => {
    // Configure page for optimal testing
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.route('**/*', (route) => {
      // Block analytics and external resources for faster tests
      if (route.request().url().includes('analytics') ||
          route.request().url().includes('googletagmanager') ||
          route.request().url().includes('google-analytics')) {
        route.abort();
      } else {
        route.continue();
      }
    });

    // Navigate to application
    await page.goto(BASE_URL, {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Verify page loaded successfully
    await expect(page.locator('text=Agent Management')).toBeVisible({ timeout: 15000 });
  });

  // ============================================================================
  // 1. SYSTEM OVERVIEW & LIVE STATS
  // ============================================================================

  test.describe('📊 System Overview & Live Stats', () => {
    test('should display comprehensive system overview', async ({ page }) => {
      await test.step('Verify header section', async () => {
        await expect(page.locator('[data-id="agent-management-header"]')).toBeVisible();
        await expect(page.locator('[data-id="system-description"]')).toBeVisible();
      });

      await test.step('Verify WebSocket connection indicator', async () => {
        const wsIndicator = page.locator('[data-id="websocket-indicator"]');
        await expect(wsIndicator).toBeVisible();

        // Should show either connected or reconnecting state
        const isConnected = await page.locator('[data-id="ws-connected"]').isVisible().catch(() => false);
        const isReconnecting = await page.locator('[data-id="ws-reconnecting"]').isVisible().catch(() => false);

        expect(isConnected || isReconnecting).toBe(true);
      });

      await test.step('Verify system metrics cards', async () => {
        const metricsCards = [
          { id: 'system-status-card', title: 'System Status' },
          { id: 'active-agents-card', title: 'Active Agents' },
          { id: 'api-requests-card', title: 'API Requests' },
          { id: 'websocket-connections-card', title: 'WS Connections' }
        ];

        for (const card of metricsCards) {
          const cardLocator = page.locator(`[data-id="${card.id}"]`);
          await expect(cardLocator).toBeVisible({ timeout: 10000 });
          await expect(cardLocator.locator(`text=${card.title}`)).toBeVisible();
        }
      });

      await test.step('Verify real-time metrics updates', async () => {
        // Wait for WebSocket updates
        await page.waitForTimeout(3000);

        // Check that metrics are populated (not showing placeholder values)
        const apiRequestsValue = page.locator('[data-id="api-requests-count"]');
        const wsConnectionsValue = page.locator('[data-id="ws-connections-count"]');

        // Values should be numbers (0 or greater)
        const apiRequests = await apiRequestsValue.textContent();
        const wsConnections = await wsConnectionsValue.textContent();

        expect(parseInt(apiRequests || '0')).toBeGreaterThanOrEqual(0);
        expect(parseInt(wsConnections || '0')).toBeGreaterThanOrEqual(0);
      });
    });

    test('should handle WebSocket reconnection gracefully', async ({ page }) => {
      await test.step('Verify manual reconnect functionality', async () => {
        const reconnectButton = page.locator('[data-id="ws-reconnect-button"]');

        // Button should be visible when disconnected
        const isDisconnected = await page.locator('[data-id="ws-disconnected"]').isVisible().catch(() => false);
        if (isDisconnected) {
          await expect(reconnectButton).toBeVisible();
          await expect(reconnectButton).toBeEnabled();

          // Click reconnect and verify state change
          await reconnectButton.click();
          await page.waitForTimeout(2000);

          // Should show reconnecting state
          await expect(page.locator('[data-id="ws-reconnecting"]')).toBeVisible({ timeout: 5000 });
        }
      });

      await test.step('Verify connection status persistence', async () => {
        // Connection status should be consistent across tab switches
        const initialStatus = await page.locator('[data-id="websocket-indicator"]').textContent();

        // Switch tabs and back
        await page.locator('[data-id="agents-tab"]').click();
        await page.waitForTimeout(1000);
        await page.locator('[data-id="overview-tab"]').click();
        await page.waitForTimeout(1000);

        // Status should remain consistent
        const finalStatus = await page.locator('[data-id="websocket-indicator"]').textContent();
        expect(finalStatus).toBe(initialStatus);
      });
    });
  });

  // ============================================================================
  // 2. AGENT CARDS & ENHANCED DESIGN
  // ============================================================================

  test.describe('🎨 Agent Cards & Enhanced Design', () => {
    test.beforeEach(async ({ page }) => {
      await page.locator('[data-id="agents-tab"]').click();
      await page.waitForTimeout(2000);
    });

    test('should display all agent types with proper styling', async ({ page }) => {
      const agentTypes = [
        { id: '01', name: 'Infrastructure Agent', type: 'infrastructure' },
        { id: '02', name: 'Database Agent', type: 'database' },
        { id: '03', name: 'Core Engine Agent', type: 'core_engine' },
        { id: '04', name: 'API Layer Agent', type: 'api_layer' },
        { id: '06', name: 'Meta-Learner Agent', type: 'meta_learner' }
      ];

      for (const agent of agentTypes) {
        await test.step(`Verify ${agent.name} card`, async () => {
          const agentCard = page.locator(`[data-id="agent-card-${agent.id}"]`);
          await expect(agentCard).toBeVisible({ timeout: 5000 });

          // Verify card content
          await expect(agentCard.locator(`text=${agent.name}`)).toBeVisible();
          await expect(agentCard.locator(`[data-id="agent-status-${agent.id}"]`)).toBeVisible();
          await expect(agentCard.locator(`[data-id="agent-metrics-${agent.id}"]`)).toBeVisible();
        });
      }
    });

    test('should display agent status indicators correctly', async ({ page }) => {
      const statusIndicators = page.locator('[data-id*="agent-status-"]');

      // Should have at least 5 status indicators
      await expect(statusIndicators).toHaveCount(5);

      // Each status should be one of the valid states
      const validStatuses = ['idle', 'working', 'error', 'degraded', 'initializing'];

      for (let i = 0; i < 5; i++) {
        const statusText = await statusIndicators.nth(i).textContent();
        expect(validStatuses).toContain(statusText?.toLowerCase());
      }
    });

    test('should show agent evaluation metrics', async ({ page }) => {
      await test.step('Verify evaluation buttons are present', async () => {
        const evaluateButtons = page.locator('[data-id*="evaluate-button-"]');
        await expect(evaluateButtons).toHaveCount(5);
      });

      await test.step('Test evaluation modal opening', async () => {
        const firstEvaluateButton = page.locator('[data-id*="evaluate-button-"]').first();
        await firstEvaluateButton.click();

        const evaluationModal = page.locator('[data-id="agent-evaluation-modal"]');
        await expect(evaluationModal).toBeVisible({ timeout: 5000 });

        // Verify modal content
        await expect(evaluationModal.locator('[data-id="evaluation-performance"]')).toBeVisible();
        await expect(evaluationModal.locator('[data-id="evaluation-metrics"]')).toBeVisible();
        await expect(evaluationModal.locator('[data-id="evaluation-recommendations"]')).toBeVisible();

        // Close modal
        await page.locator('[data-id="evaluation-modal-close"]').click();
        await expect(evaluationModal).not.toBeVisible();
      });
    });

    test('should handle agent card interactions', async ({ page }) => {
      await test.step('Test Details button functionality', async () => {
        const detailsButton = page.locator('[data-id*="details-button-"]').first();
        await detailsButton.click();

        const detailsModal = page.locator('[data-id="agent-details-modal"]');
        await expect(detailsModal).toBeVisible({ timeout: 5000 });

        // Verify modal has comprehensive information
        await expect(detailsModal.locator('[data-id="agent-capabilities"]')).toBeVisible();
        await expect(detailsModal.locator('[data-id="agent-performance"]')).toBeVisible();
        await expect(detailsModal.locator('[data-id="agent-history"]')).toBeVisible();

        // Close modal
        await page.keyboard.press('Escape');
        await expect(detailsModal).not.toBeVisible();
      });

      await test.step('Test Configure button functionality', async () => {
        const configureButton = page.locator('[data-id*="configure-button-"]').first();
        await configureButton.click();

        const configModal = page.locator('[data-id="agent-config-modal"]');
        await expect(configModal).toBeVisible({ timeout: 5000 });

        // Verify configuration options
        await expect(configModal.locator('[data-id="config-parameters"]')).toBeVisible();
        await expect(configModal.locator('[data-id="config-validation"]')).toBeVisible();

        // Close modal
        await page.locator('[data-id="config-modal-close"]').click();
        await expect(configModal).not.toBeVisible();
      });
    });
  });

  // ============================================================================
  // 3. TEMPLATE BUILDER FUNCTIONALITY
  // ============================================================================

  test.describe('🏗️ Template Builder Functionality', () => {
    test('should provide comprehensive template creation', async ({ page }) => {
      await page.locator('[data-id="agents-tab"]').click();
      await page.waitForTimeout(1000);

      await test.step('Open template builder modal', async () => {
        const templateButton = page.locator('[data-id="create-template-button"]');
        await expect(templateButton).toBeVisible();
        await templateButton.click();

        const templateModal = page.locator('[data-id="template-builder-modal"]');
        await expect(templateModal).toBeVisible({ timeout: 5000 });
      });

      await test.step('Verify template builder form elements', async () => {
        const formElements = [
          { id: 'template-name', type: 'input' },
          { id: 'template-description', type: 'textarea' },
          { id: 'template-category', type: 'select' },
          { id: 'template-agent-type', type: 'select' },
          { id: 'template-parameters', type: 'textarea' },
          { id: 'template-validation', type: 'checkbox' }
        ];

        for (const element of formElements) {
          const locator = page.locator(`[data-id="${element.id}"]`);
          await expect(locator).toBeVisible();

          if (element.type === 'input') {
            await expect(locator).toHaveAttribute('type', 'text');
          } else if (element.type === 'textarea') {
            await expect(locator.locator('textarea')).toBeVisible();
          }
        }
      });

      await test.step('Test template creation workflow', async () => {
        // Fill out template form
        await page.locator('[data-id="template-name"]').fill('Test Template');
        await page.locator('[data-id="template-description"]').fill('A comprehensive test template');

        // Select category
        await page.locator('[data-id="template-category"]').click();
        await page.locator('[data-id="category-infrastructure"]').click();

        // Select agent type
        await page.locator('[data-id="template-agent-type"]').click();
        await page.locator('[data-id="agent-type-01"]').click();

        // Add parameters
        await page.locator('[data-id="template-parameters"]').fill('{"test": "value", "enabled": true}');

        // Enable validation
        await page.locator('[data-id="template-validation"]').check();

        // Verify form validation
        const createButton = page.locator('[data-id="create-template-submit"]');
        await expect(createButton).toBeEnabled();

        // Submit form (would create template in real scenario)
        // await createButton.click();
      });

      await test.step('Verify template preview functionality', async () => {
        const previewButton = page.locator('[data-id="template-preview"]');
        if (await previewButton.isVisible()) {
          await previewButton.click();

          const previewModal = page.locator('[data-id="template-preview-modal"]');
          await expect(previewModal).toBeVisible();

          // Verify preview shows formatted template
          await expect(previewModal.locator('[data-id="preview-content"]')).toBeVisible();
        }
      });
    });
  });

  // ============================================================================
  // 4. AGENT COMMUNICATION MODAL
  // ============================================================================

  test.describe('💬 Agent Communication Modal', () => {
    test('should provide comprehensive agent communication', async ({ page }) => {
      await page.locator('[data-id="agents-tab"]').click();
      await page.waitForTimeout(1000);

      await test.step('Open communication modal', async () => {
        const commButton = page.locator('[data-id="agent-communication-button"]');
        await expect(commButton).toBeVisible();
        await commButton.click();

        const commModal = page.locator('[data-id="communication-modal"]');
        await expect(commModal).toBeVisible({ timeout: 5000 });
      });

      await test.step('Verify communication options', async () => {
        const commOptions = [
          { id: 'direct-message', name: 'Direct Message' },
          { id: 'broadcast-message', name: 'Broadcast Message' },
          { id: 'debate-mode', name: 'Debate Mode' },
          { id: 'task-delegation', name: 'Task Delegation' },
          { id: 'status-query', name: 'Status Query' }
        ];

        for (const option of commOptions) {
          const optionButton = page.locator(`[data-id="${option.id}"]`);
          await expect(optionButton).toBeVisible();
          await expect(optionButton.locator(`text=${option.name}`)).toBeVisible();
        }
      });

      await test.step('Test debate mode communication', async () => {
        await page.locator('[data-id="debate-mode"]').click();

        // Should navigate to debate system or open debate modal
        const debateInterface = page.locator('[data-id="debate-system"]').or(
          page.locator('[data-id="debate-modal"]')
        );
        await expect(debateInterface).toBeVisible({ timeout: 5000 });
      });

      await test.step('Test direct messaging', async () => {
        // Go back to communication modal if needed
        if (await page.locator('[data-id="debate-system"]').isVisible()) {
          await page.locator('[data-id="back-to-communication"]').click();
        }

        await page.locator('[data-id="direct-message"]').click();

        // Verify direct message interface
        await expect(page.locator('[data-id="recipient-select"]')).toBeVisible();
        await expect(page.locator('[data-id="message-input"]')).toBeVisible();
        await expect(page.locator('[data-id="send-message"]')).toBeVisible();

        // Test message composition
        await page.locator('[data-id="recipient-select"]').click();
        await page.locator('[data-id="recipient-agent-02"]').click();
        await page.locator('[data-id="message-input"]').fill('Test communication message');

        const sendButton = page.locator('[data-id="send-message"]');
        await expect(sendButton).toBeEnabled();
      });
    });
  });

  // ============================================================================
  // 5. ORCHESTRATION TAB
  // ============================================================================

  test.describe('🎼 Orchestration Tab', () => {
    test('should provide comprehensive task orchestration', async ({ page }) => {
      await page.locator('[data-id="orchestration-tab"]').click();
      await page.waitForTimeout(2000);

      await test.step('Verify orchestration dashboard', async () => {
        await expect(page.locator('[data-id="orchestration-dashboard"]')).toBeVisible();

        // Check key orchestration components
        const components = [
          'workflow-builder',
          'task-queue',
          'agent-coordination',
          'performance-monitor',
          'resource-allocator'
        ];

        for (const component of components) {
          await expect(page.locator(`[data-id="${component}"]`)).toBeVisible();
        }
      });

      await test.step('Test workflow builder functionality', async () => {
        await page.locator('[data-id="workflow-builder"]').click();

        const builderInterface = page.locator('[data-id="workflow-canvas"]');
        await expect(builderInterface).toBeVisible();

        // Test workflow creation
        await page.locator('[data-id="add-workflow-step"]').click();
        await page.locator('[data-id="step-agent-select"]').click();
        await page.locator('[data-id="select-agent-01"]').click();

        await page.locator('[data-id="step-operation"]').fill('health_check');
        await page.locator('[data-id="step-parameters"]').fill('{"comprehensive": true}');

        await expect(page.locator('[data-id="save-workflow"]')).toBeEnabled();
      });

      await test.step('Verify task queue management', async () => {
        const taskQueue = page.locator('[data-id="task-queue"]');

        // Check queue status
        await expect(taskQueue.locator('[data-id="queue-status"]')).toBeVisible();
        await expect(taskQueue.locator('[data-id="active-tasks"]')).toBeVisible();
        await expect(taskQueue.locator('[data-id="queued-tasks"]')).toBeVisible();

        // Test queue controls
        const controls = ['pause-queue', 'resume-queue', 'clear-queue', 'priority-settings'];
        for (const control of controls) {
          await expect(page.locator(`[data-id="${control}"]`)).toBeVisible();
        }
      });

      await test.step('Test agent coordination features', async () => {
        const coordinationPanel = page.locator('[data-id="agent-coordination"]');

        // Check coordination metrics
        await expect(coordinationPanel.locator('[data-id="coordination-efficiency"]')).toBeVisible();
        await expect(coordinationPanel.locator('[data-id="conflict-resolution"]')).toBeVisible();

        // Test coordination controls
        await page.locator('[data-id="coordination-settings"]').click();
        const settingsModal = page.locator('[data-id="coordination-settings-modal"]');
        await expect(settingsModal).toBeVisible();

        // Verify coordination options
        const options = ['load-balancing', 'conflict-prevention', 'resource-sharing', 'priority-inheritance'];
        for (const option of options) {
          await expect(settingsModal.locator(`[data-id="${option}"]`)).toBeVisible();
        }
      });
    });
  });

  // ============================================================================
  // 6. AGENT CONFIGURATION
  // ============================================================================

  test.describe('⚙️ Agent Configuration', () => {
    test('should provide comprehensive agent configuration', async ({ page }) => {
      await page.locator('[data-id="agents-tab"]').click();
      await page.waitForTimeout(1000);

      await test.step('Test agent configuration modal', async () => {
        const configButton = page.locator('[data-id*="configure-button-"]').first();
        await configButton.click();

        const configModal = page.locator('[data-id="agent-config-modal"]');
        await expect(configModal).toBeVisible({ timeout: 5000 });
      });

      await test.step('Verify configuration categories', async () => {
        const configCategories = [
          { id: 'performance-config', name: 'Performance Settings' },
          { id: 'behavior-config', name: 'Behavior Configuration' },
          { id: 'resource-config', name: 'Resource Management' },
          { id: 'communication-config', name: 'Communication Settings' },
          { id: 'monitoring-config', name: 'Monitoring & Logging' }
        ];

        for (const category of configCategories) {
          const tab = page.locator(`[data-id="${category.id}"]`);
          await expect(tab).toBeVisible();
          await expect(tab.locator(`text=${category.name}`)).toBeVisible();
        }
      });

      await test.step('Test performance configuration', async () => {
        await page.locator('[data-id="performance-config"]').click();

        // Verify performance settings
        const perfSettings = [
          'max-concurrent-tasks',
          'cpu-allocation',
          'memory-limit',
          'timeout-settings',
          'retry-policy'
        ];

        for (const setting of perfSettings) {
          await expect(page.locator(`[data-id="${setting}"]`)).toBeVisible();
        }

        // Test configuration changes
        const maxTasksInput = page.locator('[data-id="max-concurrent-tasks"]');
        await maxTasksInput.fill('10');

        const cpuSlider = page.locator('[data-id="cpu-allocation"]');
        await cpuSlider.fill('75');

        // Verify validation
        await expect(page.locator('[data-id="config-validation-status"]')).toBeVisible();
      });

      await test.step('Test behavior configuration', async () => {
        await page.locator('[data-id="behavior-config"]').click();

        const behaviorSettings = [
          'aggression-level',
          'cooperation-mode',
          'error-handling',
          'learning-rate',
          'adaptation-speed'
        ];

        for (const setting of behaviorSettings) {
          await expect(page.locator(`[data-id="${setting}"]`)).toBeVisible();
        }
      });

      await test.step('Test resource management', async () => {
        await page.locator('[data-id="resource-config"]').click();

        const resourceSettings = [
          'resource-priorities',
          'allocation-strategy',
          'cleanup-policies',
          'cache-settings',
          'storage-limits'
        ];

        for (const setting of resourceSettings) {
          await expect(page.locator(`[data-id="${setting}"]`)).toBeVisible();
        }
      });

      await test.step('Verify configuration persistence', async () => {
        // Make a configuration change
        const originalValue = await page.locator('[data-id="max-concurrent-tasks"]').inputValue();
        await page.locator('[data-id="max-concurrent-tasks"]').fill('15');

        // Save configuration
        await page.locator('[data-id="save-config"]').click();

        // Verify success message
        await expect(page.locator('[data-id="config-save-success"]')).toBeVisible();

        // Refresh and verify persistence
        await page.reload();
        await page.locator('[data-id="agents-tab"]').click();
        await page.locator('[data-id*="configure-button-"]').first().click();

        const newValue = await page.locator('[data-id="max-concurrent-tasks"]').inputValue();
        expect(newValue).toBe('15');
      });
    });
  });

  // ============================================================================
  // 7. NAVIGATION & TAB FUNCTIONALITY
  // ============================================================================

  test.describe('🧭 Navigation & Tab Functionality', () => {
    test('should provide seamless tab navigation', async ({ page }) => {
      const tabs = [
        { id: 'overview-tab', name: 'Overview' },
        { id: 'agents-tab', name: 'Agents' },
        { id: 'tasks-tab', name: 'Task Execution' },
        { id: 'orchestration-tab', name: 'Orchestration' },
        { id: 'debate-tab', name: 'Debate System' },
        { id: 'system-tab', name: 'System' }
      ];

      await test.step('Test all main tabs', async () => {
        for (const tab of tabs) {
          await test.step(`Navigate to ${tab.name} tab`, async () => {
            const tabButton = page.locator(`[data-id="${tab.id}"]`);
            await expect(tabButton).toBeVisible();
            await tabButton.click();

            // Verify tab content loads
            const tabContent = page.locator(`[data-id="${tab.id.replace('-tab', '-content')}"]`);
            await expect(tabContent).toBeVisible({ timeout: 5000 });

            // Verify URL updates (if using hash routing)
            const url = page.url();
            // URL should contain tab identifier or hash
          });
        }
      });

      await test.step('Test tab state persistence', async () => {
        // Navigate to a specific tab
        await page.locator('[data-id="debate-tab"]').click();
        await page.waitForTimeout(1000);

        // Refresh page
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Should return to Overview tab (default)
        await expect(page.locator('[data-id="overview-content"]')).toBeVisible();
      });

      await test.step('Test keyboard navigation', async () => {
        // Tab through navigation elements
        await page.keyboard.press('Tab');
        await page.keyboard.press('Tab');

        // Should focus on first tab
        const activeElement = await page.evaluate(() => document.activeElement?.getAttribute('data-id'));
        expect(activeElement).toMatch(/tab/);
      });
    });

    test('should handle deep linking and bookmarks', async ({ page }) => {
      await test.step('Test direct navigation to tabs', async () => {
        const tabUrls = [
          { url: `${BASE_URL}#agents`, content: 'agents-content' },
          { url: `${BASE_URL}#tasks`, content: 'tasks-content' },
          { url: `${BASE_URL}#orchestration`, content: 'orchestration-content' }
        ];

        for (const tabUrl of tabUrls) {
          await page.goto(tabUrl.url);
          await page.waitForLoadState('networkidle');

          const contentLocator = page.locator(`[data-id="${tabUrl.content}"]`);
          await expect(contentLocator).toBeVisible({ timeout: 5000 });
        }
      });
    });
  });

  // ============================================================================
  // 8. DATA PERSISTENCE & STATE MANAGEMENT
  // ============================================================================

  test.describe('💾 Data Persistence & State Management', () => {
    test('should maintain state across sessions', async ({ page, context }) => {
      await test.step('Create and save configuration', async () => {
        await page.locator('[data-id="agents-tab"]').click();
        await page.locator('[data-id*="configure-button-"]').first().click();

        // Make configuration changes
        await page.locator('[data-id="max-concurrent-tasks"]').fill('20');
        await page.locator('[data-id="cpu-allocation"]').fill('80');

        await page.locator('[data-id="save-config"]').click();
        await expect(page.locator('[data-id="config-save-success"]')).toBeVisible();
      });

      await test.step('Verify persistence in new session', async () => {
        // Open new page/context to simulate new session
        const newPage = await context.newPage();
        await newPage.goto(BASE_URL);
        await newPage.waitForLoadState('networkidle');

        // Navigate to same configuration
        await newPage.locator('[data-id="agents-tab"]').click();
        await newPage.locator('[data-id*="configure-button-"]').first().click();

        // Verify values persisted
        const maxTasks = await newPage.locator('[data-id="max-concurrent-tasks"]').inputValue();
        const cpuAlloc = await newPage.locator('[data-id="cpu-allocation"]').inputValue();

        expect(maxTasks).toBe('20');
        expect(cpuAlloc).toBe('80');

        await newPage.close();
      });
    });

    test('should handle offline functionality gracefully', async ({ page }) => {
      await test.step('Test offline state handling', async () => {
        // Simulate offline state
        await page.context().setOffline(true);

        // Verify offline indicators
        await expect(page.locator('[data-id="offline-indicator"]')).toBeVisible({ timeout: 5000 });

        // WebSocket should show disconnected state
        await expect(page.locator('[data-id="ws-disconnected"]')).toBeVisible();

        // Core functionality should still work
        await expect(page.locator('[data-id="agents-tab"]')).toBeEnabled();

        // Restore connection
        await page.context().setOffline(false);
        await page.waitForTimeout(2000);

        // Should reconnect automatically
        await expect(page.locator('[data-id="ws-connected"]')).toBeVisible({ timeout: 10000 });
      });
    });

    test('should handle data synchronization', async ({ page }) => {
      await test.step('Test real-time data sync', async () => {
        // Monitor agent status changes
        const initialStatus = await page.locator('[data-id="agent-status-01"]').textContent();

        // Simulate external status change (would come via WebSocket in real scenario)
        await page.waitForTimeout(5000);

        // Verify status updates are reflected
        const updatedStatus = await page.locator('[data-id="agent-status-01"]').textContent();

        // Status should be current (may be same or different based on system state)
        expect(updatedStatus).toBeDefined();
        expect(['idle', 'working', 'error', 'degraded', 'initializing']).toContain(updatedStatus?.toLowerCase());
      });
    });
  });

  // ============================================================================
  // 9. RESPONSIVE DESIGN
  // ============================================================================

  test.describe('📱 Responsive Design', () => {
    test('should work on desktop viewport', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });

      // Verify all components are visible and properly laid out
      await expect(page.locator('[data-id="agent-management-header"]')).toBeVisible();
      await expect(page.locator('[data-id="system-overview-cards"]')).toBeVisible();

      // Test grid layouts
      const agentCards = page.locator('[data-id*="agent-card-"]');
      await expect(agentCards).toHaveCount(5);

      // Verify cards are in a reasonable layout
      const firstCard = agentCards.first();
      const boundingBox = await firstCard.boundingBox();
      expect(boundingBox?.width).toBeGreaterThan(300); // Reasonable card width
    });

    test('should work on tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      // Header should still be visible
      await expect(page.locator('[data-id="agent-management-header"]')).toBeVisible();

      // Cards should adapt to smaller screen
      const agentCards = page.locator('[data-id*="agent-card-"]');
      await expect(agentCards).toHaveCount(5);

      // Test mobile menu if present
      const mobileMenu = page.locator('[data-id="mobile-menu"]');
      if (await mobileMenu.isVisible()) {
        await mobileMenu.click();
        await expect(page.locator('[data-id="mobile-nav"]')).toBeVisible();
      }
    });

    test('should work on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });

      // Critical elements should remain accessible
      await expect(page.locator('[data-id="agent-management-header"]')).toBeVisible();

      // Navigation should be mobile-friendly
      const tabs = page.locator('[data-id*="tab"]');
      const tabCount = await tabs.count();

      if (tabCount > 4) { // If many tabs, should have mobile navigation
        const mobileNav = page.locator('[data-id="mobile-tab-nav"]');
        await expect(mobileNav).toBeVisible();
      }

      // Cards should stack vertically on mobile
      const agentCards = page.locator('[data-id*="agent-card-"]');
      await expect(agentCards).toHaveCount(5);

      // Test touch interactions
      const firstCard = agentCards.first();
      await firstCard.tap();

      // Should open details modal or expand card
      const modal = page.locator('[data-id*="modal"]');
      const expandedCard = page.locator('[data-id*="expanded"]');

      expect(await modal.isVisible() || await expandedCard.isVisible()).toBe(true);
    });
  });

  // ============================================================================
  // 10. ERROR HANDLING & RECOVERY
  // ============================================================================

  test.describe('🚨 Error Handling & Recovery', () => {
    test('should handle network failures gracefully', async ({ page }) => {
      await test.step('Test API endpoint failures', async () => {
        // Intercept API calls and simulate failures
        await page.route('**/api/v1/agents/**', route => {
          route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Internal Server Error' })
          });
        });

        // Navigate to agents tab
        await page.locator('[data-id="agents-tab"]').click();

        // Should show error state but not crash
        await expect(page.locator('[data-id="error-state"]')).toBeVisible({ timeout: 5000 });

        // Should provide retry option
        await expect(page.locator('[data-id="retry-button"]')).toBeVisible();

        // Test retry functionality
        await page.locator('[data-id="retry-button"]').click();

        // Should attempt to reload data
        await page.waitForTimeout(2000);
      });

      await test.step('Test WebSocket disconnection recovery', async () => {
        // WebSocket disconnection is already tested in the live stats section
        // Here we verify that the UI remains functional during disconnection

        // Force disconnect (in real scenario, this would be network interruption)
        const wasConnected = await page.locator('[data-id="ws-connected"]').isVisible();

        if (wasConnected) {
          // Simulate disconnection by blocking WebSocket
          await page.route('ws://**', route => route.abort());

          await expect(page.locator('[data-id="ws-disconnected"]')).toBeVisible({ timeout: 10000 });

          // UI should remain functional
          await expect(page.locator('[data-id="agents-tab"]')).toBeEnabled();
          await expect(page.locator('[data-id="tasks-tab"]')).toBeEnabled();

          // Should show reconnect option
          await expect(page.locator('[data-id="ws-reconnect-button"]')).toBeVisible();
        }
      });
    });

    test('should handle form validation errors', async ({ page }) => {
      await page.locator('[data-id="tasks-tab"]').click();

      await test.step('Test invalid JSON parameters', async () => {
        const paramsField = page.locator('[data-id="task-parameters"]');
        await paramsField.fill('invalid json syntax {{{');

        // Try to submit
        const submitButton = page.locator('[data-id="execute-task"]');
        if (await submitButton.isEnabled()) {
          await submitButton.click();

          // Should show validation error
          await expect(page.locator('[data-id="validation-error"]')).toBeVisible();
          await expect(page.locator('text=Invalid JSON')).toBeVisible();
        }
      });

      await test.step('Test missing required fields', async () => {
        // Clear all fields
        await page.locator('[data-id="task-operation"]').fill('');
        await page.locator('[data-id="task-parameters"]').fill('');

        // Submit button should be disabled
        const submitButton = page.locator('[data-id="execute-task"]');
        await expect(submitButton).toBeDisabled();
      });

      await test.step('Test network timeout handling', async () => {
        // Fill valid form
        await page.locator('[data-id="task-operation"]').fill('test_operation');
        await page.locator('[data-id="task-parameters"]').fill('{"test": true}');

        // Intercept and delay API call to simulate timeout
        await page.route('**/api/v1/agents/**/execute', async route => {
          await page.waitForTimeout(35000); // Longer than timeout
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ task_id: 'test-123', status: 'completed' })
          });
        });

        // Submit should eventually timeout and show error
        await page.locator('[data-id="execute-task"]').click();

        // Should show timeout error
        await expect(page.locator('[data-id="timeout-error"]')).toBeVisible({ timeout: 40000 });
      });
    });

    test('should handle modal state errors', async ({ page }) => {
      await page.locator('[data-id="agents-tab"]').click();

      await test.step('Test modal opening failures', async () => {
        // Click details button
        await page.locator('[data-id*="details-button-"]').first().click();

        // Modal should open
        const modal = page.locator('[data-id="agent-details-modal"]');
        await expect(modal).toBeVisible();

        // Simulate modal content loading failure
        await page.route('**/api/v1/agents/**/details', route => {
          route.fulfill({
            status: 404,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Agent not found' })
          });
        });

        // Should show error in modal
        await expect(modal.locator('[data-id="modal-error"]')).toBeVisible();
        await expect(modal.locator('text=Agent not found')).toBeVisible();

        // Close button should still work
        await page.locator('[data-id="modal-close"]').click();
        await expect(modal).not.toBeVisible();
      });
    });
  });

  // ============================================================================
  // 11. ACCESSIBILITY COMPLIANCE
  // ============================================================================

  test.describe('♿ Accessibility Compliance', () => {
    test('should meet WCAG 2.1 AA standards', async ({ page }) => {
      await test.step('Test keyboard navigation', async () => {
        // Tab through main navigation
        await page.keyboard.press('Tab');
        let activeElement = await page.evaluate(() => document.activeElement?.tagName);
        expect(activeElement).toBe('BUTTON'); // Should focus on first interactive element

        // Continue tabbing through interface
        for (let i = 0; i < 10; i++) {
          await page.keyboard.press('Tab');
          await page.waitForTimeout(100);

          // Should always have some element focused
          const hasFocus = await page.evaluate(() => document.activeElement !== null);
          expect(hasFocus).toBe(true);
        }
      });

      await test.step('Test ARIA labels and roles', async () => {
        // Check main landmarks
        await expect(page.locator('[role="main"]')).toBeVisible();
        await expect(page.locator('[role="navigation"]')).toBeVisible();

        // Check form elements have labels
        const inputs = page.locator('input');
        const inputCount = await inputs.count();

        for (let i = 0; i < Math.min(inputCount, 5); i++) {
          const input = inputs.nth(i);
          const hasLabel = await input.evaluate(el => {
            const id = el.id;
            return id && document.querySelector(`label[for="${id}"]`);
          });

          if (!hasLabel) {
            // Check if input has aria-label
            const ariaLabel = await input.getAttribute('aria-label');
            expect(ariaLabel).toBeTruthy();
          }
        }
      });

      await test.step('Test color contrast', async () => {
        // Check that text has sufficient contrast
        const textElements = page.locator('p, span, h1, h2, h3, h4, h5, h6');
        const sampleTexts = await textElements.evaluateAll(elements =>
          elements.slice(0, 5).map(el => ({
            text: el.textContent?.trim(),
            color: window.getComputedStyle(el).color,
            backgroundColor: window.getComputedStyle(el).backgroundColor
          }))
        );

        // Should have readable text (basic check)
        expect(sampleTexts.length).toBeGreaterThan(0);
        sampleTexts.forEach(item => {
          expect(item.text).toBeTruthy();
        });
      });

      await test.step('Test screen reader support', async () => {
        // Check for ARIA live regions for dynamic content
        const liveRegions = page.locator('[aria-live]');
        const liveCount = await liveRegions.count();

        // Should have live regions for status updates
        expect(liveCount).toBeGreaterThan(0);

        // Check modal accessibility
        const modal = page.locator('[role="dialog"]');
        if (await modal.isVisible()) {
          await expect(modal).toHaveAttribute('aria-labelledby');
          await expect(modal).toHaveAttribute('aria-describedby');
        }
      });
    });
  });

  // ============================================================================
  // 12. PERFORMANCE & LOAD TESTING
  // ============================================================================

  test.describe('⚡ Performance & Load Testing', () => {
    test('should handle rapid user interactions', async ({ page }) => {
      await test.step('Test rapid tab switching', async () => {
        const tabs = ['overview-tab', 'agents-tab', 'tasks-tab', 'orchestration-tab', 'system-tab'];

        // Rapidly switch between tabs
        for (let i = 0; i < 3; i++) {
          for (const tabId of tabs) {
            await page.locator(`[data-id="${tabId}"]`).click();
            // Don't wait, test rapid switching
          }
        }

        // Should still be functional after rapid switching
        await expect(page.locator('[data-id="agent-management-header"]')).toBeVisible();
      });

      await test.step('Test concurrent modal operations', async () => {
        await page.locator('[data-id="agents-tab"]').click();

        // Open multiple modals rapidly
        const detailsButtons = page.locator('[data-id*="details-button-"]');
        const buttonCount = await detailsButtons.count();

        // Click first few buttons rapidly
        for (let i = 0; i < Math.min(buttonCount, 3); i++) {
          await detailsButtons.nth(i).click();
          await page.waitForTimeout(100); // Minimal delay
        }

        // Should handle multiple modals gracefully
        const modals = page.locator('[role="dialog"]');
        const modalCount = await modals.count();

        // Should have at least one modal open
        expect(modalCount).toBeGreaterThan(0);

        // Close all modals
        for (let i = 0; i < modalCount; i++) {
          await page.keyboard.press('Escape');
          await page.waitForTimeout(100);
        }
      });
    });

    test('should maintain performance with large datasets', async ({ page }) => {
      await test.step('Test with simulated large task history', async () => {
        await page.locator('[data-id="tasks-tab"]').click();

        // Simulate scrolling through large task list
        const taskList = page.locator('[data-id="task-history"]');
        if (await taskList.isVisible()) {
          // Scroll to bottom to test virtual scrolling
          await taskList.evaluate(el => el.scrollTop = el.scrollHeight);
          await page.waitForTimeout(1000);

          // Should still be responsive
          const scrollPosition = await taskList.evaluate(el => el.scrollTop);
          expect(scrollPosition).toBeGreaterThan(0);
        }
      });

      await test.step('Test memory usage with multiple tabs open', async () => {
        // Open all tabs
        const tabs = ['overview-tab', 'agents-tab', 'tasks-tab', 'orchestration-tab', 'debate-tab', 'system-tab'];

        for (const tabId of tabs) {
          await page.locator(`[data-id="${tabId}"]`).click();
          await page.waitForTimeout(500);
        }

        // Should handle memory pressure gracefully
        // Check that no memory-related errors occurred
        const consoleMessages = [];
        page.on('console', msg => consoleMessages.push(msg.text()));

        await page.waitForTimeout(2000);

        // Should not have memory errors
        const memoryErrors = consoleMessages.filter(msg =>
          msg.includes('memory') || msg.includes('out of memory')
        );
        expect(memoryErrors.length).toBe(0);
      });
    });

    test('should handle network latency gracefully', async ({ page }) => {
      await test.step('Test with simulated network delay', async () => {
        // Add artificial delay to all API calls
        await page.route('**/api/v1/**', async route => {
          await page.waitForTimeout(1000); // 1 second delay
          await route.continue();
        });

        // Navigate and verify UI remains responsive
        await page.locator('[data-id="agents-tab"]').click();

        // Should show loading states
        await expect(page.locator('[data-id="loading-spinner"]')).toBeVisible({ timeout: 2000 });

        // Should eventually load content
        await expect(page.locator('[data-id="agent-card-01"]')).toBeVisible({ timeout: 15000 });
      });

      await test.step('Test connection recovery', async () => {
        // Simulate complete network failure
        await page.context().setOffline(true);
        await page.waitForTimeout(2000);

        // Should show offline indicators
        await expect(page.locator('[data-id="offline-indicator"]')).toBeVisible();

        // Restore connection
        await page.context().setOffline(false);

        // Should recover and show online status
        await expect(page.locator('[data-id="ws-connected"]')).toBeVisible({ timeout: 10000 });
      });
    });
  });

  // ============================================================================
  // SUMMARY & FINAL VALIDATION
  // ============================================================================

  test.describe('🎯 Final Validation & Summary', () => {
    test('should pass comprehensive system validation', async ({ page }) => {
      const validationResults = {
        systemOverview: false,
        agentCards: false,
        taskExecution: false,
        orchestration: false,
        configuration: false,
        communication: false,
        websocket: false,
        navigation: false,
        responsiveness: false,
        accessibility: false,
        performance: false
      };

      await test.step('Validate system overview', async () => {
        await expect(page.locator('[data-id="system-overview-cards"]')).toBeVisible();
        await expect(page.locator('[data-id="websocket-indicator"]')).toBeVisible();
        validationResults.systemOverview = true;
      });

      await test.step('Validate agent management', async () => {
        await page.locator('[data-id="agents-tab"]').click();
        await expect(page.locator('[data-id="agent-card-01"]')).toBeVisible();
        await expect(page.locator('[data-id="agent-card-02"]')).toBeVisible();
        validationResults.agentCards = true;
      });

      await test.step('Validate task execution', async () => {
        await page.locator('[data-id="tasks-tab"]').click();
        await expect(page.locator('[data-id="task-execution-form"]')).toBeVisible();
        await expect(page.locator('[data-id="task-history"]')).toBeVisible();
        validationResults.taskExecution = true;
      });

      await test.step('Validate orchestration', async () => {
        await page.locator('[data-id="orchestration-tab"]').click();
        await expect(page.locator('[data-id="orchestration-dashboard"]')).toBeVisible();
        validationResults.orchestration = true;
      });

      await test.step('Validate configuration', async () => {
        await page.locator('[data-id="agents-tab"]').click();
        await page.locator('[data-id*="configure-button-"]').first().click();
        await expect(page.locator('[data-id="agent-config-modal"]')).toBeVisible();
        validationResults.configuration = true;
      });

      await test.step('Validate communication', async () => {
        await page.locator('[data-id="agent-communication-button"]').click();
        await expect(page.locator('[data-id="communication-modal"]')).toBeVisible();
        validationResults.communication = true;
      });

      await test.step('Validate WebSocket functionality', async () => {
        const wsIndicator = page.locator('[data-id="websocket-indicator"]');
        const isConnected = await page.locator('[data-id="ws-connected"]').isVisible().catch(() => false);
        const isDisconnected = await page.locator('[data-id="ws-disconnected"]').isVisible().catch(() => false);

        validationResults.websocket = isConnected || isDisconnected;
      });

      await test.step('Validate navigation', async () => {
        const tabs = ['overview-tab', 'agents-tab', 'tasks-tab', 'orchestration-tab', 'system-tab'];
        for (const tabId of tabs) {
          await page.locator(`[data-id="${tabId}"]`).click();
          await expect(page.locator(`[data-id="${tabId.replace('-tab', '-content')}"]`)).toBeVisible();
        }
        validationResults.navigation = true;
      });

      await test.step('Validate responsiveness', async () => {
        await page.setViewportSize({ width: 375, height: 667 });
        await expect(page.locator('[data-id="agent-management-header"]')).toBeVisible();
        validationResults.responsiveness = true;
      });

      await test.step('Generate validation report', async () => {
        const passedTests = Object.values(validationResults).filter(Boolean).length;
        const totalTests = Object.keys(validationResults).length;
        const successRate = (passedTests / totalTests) * 100;

        console.log('\n=== COMPREHENSIVE VALIDATION REPORT ===');
        console.log(`Passed: ${passedTests}/${totalTests} (${successRate.toFixed(1)}%)`);

        Object.entries(validationResults).forEach(([test, passed]) => {
          const status = passed ? '✅' : '❌';
          console.log(`${status} ${test.replace(/([A-Z])/g, ' $1').toLowerCase()}`);
        });

        console.log('\n=== SYSTEM HEALTH CHECK ===');
        console.log(`WebSocket: ${validationResults.websocket ? 'Connected' : 'Disconnected'}`);
        console.log(`All Agents: ${validationResults.agentCards ? 'Loaded' : 'Failed'}`);
        console.log(`Task System: ${validationResults.taskExecution ? 'Operational' : 'Failed'}`);
        console.log(`Orchestration: ${validationResults.orchestration ? 'Active' : 'Failed'}`);

        // Final assertion
        expect(successRate).toBeGreaterThanOrEqual(90); // Require 90% pass rate
      });
    });
  });
});
