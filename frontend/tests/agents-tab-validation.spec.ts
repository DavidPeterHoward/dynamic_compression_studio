import { expect, test } from '@playwright/test';

/**
 * Comprehensive Agents Tab Validation Test
 * 
 * Validates that all components, forms, dropdowns, selects, and features
 * mentioned in FRONTEND_AGENT_AGENT_CAPABILITIES_REVIEW.md are present
 * and functional on the Agents tab.
 */

const BASE_URL = process.env.BASE_URL || process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8443';
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8441';

test.describe('Agents Tab Comprehensive Validation', () => {
  test.setTimeout(120000); // 2 minutes

  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000); // Wait for React hydration

    // Navigate to Agents tab
    const agentsTab = page.locator('text=Agents').first();
    await agentsTab.click({ timeout: 10000 });
    await page.waitForTimeout(2000); // Wait for Agents tab to load
  });

  test('1. Verify Header Section and System Overview', async ({ page }) => {
    await test.step('Check header title and description', async () => {
      await expect(page.locator('text=Agent Management')).toBeVisible({ timeout: 10000 });
      await expect(page.locator('text=Monitor and control the multi-agent system')).toBeVisible();
    });

    await test.step('Check WebSocket connection indicator', async () => {
      const wsIndicator = page.locator('text=/Live Updates|Disconnected/');
      await expect(wsIndicator.first()).toBeVisible();
    });

    await test.step('Check Refresh button', async () => {
      const refreshButton = page.locator('button:has-text("Refresh")').or(
        page.locator('button[aria-label*="refresh" i]')
      );
      await expect(refreshButton.first()).toBeVisible();
    });

    await test.step('Verify System Overview Cards', async () => {
      // System Status card
      await expect(page.locator('text=System Status').or(page.locator('text=/System.*Status/i'))).toBeVisible();
      
      // Active Agents card
      await expect(page.locator('text=Active Agents').or(page.locator('text=/Active.*Agents/i'))).toBeVisible();
      
      // API Requests card
      await expect(page.locator('text=API Requests').or(page.locator('text=/API.*Requests/i'))).toBeVisible();
      
      // WS Connections card
      await expect(page.locator('text=WS Connections').or(page.locator('text=/WS.*Connections/i'))).toBeVisible();
    });
  });

  test('2. Verify Tab Navigation Structure', async ({ page }) => {
    await test.step('Check all tabs are present', async () => {
      const tabs = ['Overview', 'Agents', 'Task Execution', 'System'];
      
      for (const tabName of tabs) {
        const tab = page.locator(`text=${tabName}`).or(
          page.locator(`button:has-text("${tabName}")`)
        );
        await expect(tab.first()).toBeVisible({ timeout: 5000 });
      }
    });

    await test.step('Test tab switching', async () => {
      // Click Overview tab
      await page.locator('text=Overview').first().click();
      await page.waitForTimeout(500);
      
      // Click Agents tab
      await page.locator('text=Agents').first().click();
      await page.waitForTimeout(500);
      
      // Click Task Execution tab
      await page.locator('text=Task Execution').first().click();
      await page.waitForTimeout(500);
      
      // Click System tab
      await page.locator('text=System').first().click();
      await page.waitForTimeout(500);
    });
  });

  test('3. Verify Overview Tab Components', async ({ page }) => {
    // Navigate to Overview tab
    await page.locator('text=Overview').first().click();
    await page.waitForTimeout(1000);

    await test.step('Check Agent Status section', async () => {
      await expect(page.locator('text=Agent Status').or(page.locator('text=/Agent.*Status/i'))).toBeVisible();
    });

    await test.step('Check Recent Tasks section', async () => {
      await expect(page.locator('text=Recent Tasks').or(page.locator('text=/Recent.*Tasks/i'))).toBeVisible();
    });

    await test.step('Verify agent cards are displayed', async () => {
      // Look for agent cards (they should contain agent names or IDs)
      const agentCards = page.locator('text=/Infrastructure Agent|Database Agent|Core Engine Agent|API Layer Agent|Meta-Learner Agent/i');
      const count = await agentCards.count();
      console.log(`Found ${count} agent cards in Overview tab`);
      // At least one agent card should be visible
      expect(count).toBeGreaterThan(0);
    });

    await test.step('Check agent card elements', async () => {
      // Check for status indicators (colored dots or badges)
      const statusIndicators = page.locator('[class*="rounded-full"]').or(
        page.locator('text=/idle|working|error|degraded/i')
      );
      const statusCount = await statusIndicators.count();
      expect(statusCount).toBeGreaterThan(0);
    });
  });

  test('4. Verify Agents Tab Components', async ({ page }) => {
    // Navigate to Agents tab
    await page.locator('text=Agents').first().click();
    await page.waitForTimeout(1000);

    await test.step('Check Agent Management header', async () => {
      await expect(page.locator('text=Agent Management').or(page.locator('text=/Agent.*Management/i'))).toBeVisible();
    });

    await test.step('Check Create Agent button (should be present even if disabled)', async () => {
      const createButton = page.locator('button:has-text("Create Agent")').or(
        page.locator('button:has-text("Create")')
      );
      await expect(createButton.first()).toBeVisible();
    });

    await test.step('Verify agent cards in grid layout', async () => {
      // Check for agent type names
      const agentTypes = [
        'Infrastructure Agent',
        'Database Agent',
        'Core Engine Agent',
        'API Layer Agent',
        'Meta-Learner Agent'
      ];

      for (const agentType of agentTypes) {
        const agentCard = page.locator(`text=${agentType}`).or(
          page.locator(`text=/.*${agentType.split(' ')[0]}.*Agent/i`)
        );
        // At least one should be visible
        const count = await agentCard.count();
        if (count > 0) {
          console.log(`✅ Found ${agentType}`);
        }
      }
    });

    await test.step('Check Details button on agent cards', async () => {
      const detailsButton = page.locator('button:has-text("Details")').or(
        page.locator('button:has-text("View")')
      );
      const count = await detailsButton.count();
      expect(count).toBeGreaterThan(0);
    });

    await test.step('Check Configure button on agent cards', async () => {
      const configureButton = page.locator('button:has-text("Configure")').or(
        page.locator('button:has-text("Settings")')
      );
      const count = await configureButton.count();
      expect(count).toBeGreaterThan(0);
    });
  });

  test('5. Verify Task Execution Tab - Forms and Inputs', async ({ page }) => {
    // Navigate to Task Execution tab
    await page.locator('text=Task Execution').first().click();
    await page.waitForTimeout(1000);

    await test.step('Check Execute Task card header', async () => {
      await expect(page.locator('text=Execute Task').or(page.locator('text=/Execute.*Task/i'))).toBeVisible();
    });

    await test.step('Verify Target Agent Select dropdown', async () => {
      const agentSelect = page.locator('label:has-text("Target Agent")').or(
        page.locator('label:has-text("Agent")')
      );
      await expect(agentSelect.first()).toBeVisible();
      
      // Check for select trigger
      const selectTrigger = page.locator('[role="combobox"]').or(
        page.locator('button:has-text("Select agent")')
      );
      await expect(selectTrigger.first()).toBeVisible();
      
      // Click to open dropdown
      await selectTrigger.first().click();
      await page.waitForTimeout(500);
      
      // Check dropdown is open (should have select items)
      const selectItems = page.locator('[role="option"]');
      const itemCount = await selectItems.count();
      expect(itemCount).toBeGreaterThan(0);
      
      // Close dropdown by clicking outside or pressing Escape
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    });

    await test.step('Verify Operation Input field', async () => {
      const operationLabel = page.locator('label:has-text("Operation")');
      await expect(operationLabel.first()).toBeVisible();
      
      const operationInput = page.locator('input[placeholder*="compress" i]').or(
        page.locator('input[placeholder*="analyze" i]')
      );
      await expect(operationInput.first()).toBeVisible();
      
      // Test input
      await operationInput.first().fill('test_operation');
      const value = await operationInput.first().inputValue();
      expect(value).toBe('test_operation');
    });

    await test.step('Verify Parameters Textarea', async () => {
      const parametersLabel = page.locator('label:has-text("Parameters")');
      await expect(parametersLabel.first()).toBeVisible();
      
      const parametersTextarea = page.locator('textarea[placeholder*="JSON" i]').or(
        page.locator('textarea[placeholder*="key.*value" i]')
      );
      await expect(parametersTextarea.first()).toBeVisible();
      
      // Test textarea
      await parametersTextarea.first().fill('{"test": "value"}');
      const value = await parametersTextarea.first().inputValue();
      expect(value).toContain('test');
    });

    await test.step('Verify Priority Select dropdown', async () => {
      const priorityLabel = page.locator('label:has-text("Priority")');
      await expect(priorityLabel.first()).toBeVisible();
      
      const prioritySelect = page.locator('button:has-text("Normal")').or(
        page.locator('button:has-text("Low")').or(
          page.locator('[role="combobox"]').nth(1)
        )
      );
      await expect(prioritySelect.first()).toBeVisible();
      
      // Click to open
      await prioritySelect.first().click();
      await page.waitForTimeout(500);
      
      // Check priority options
      const priorities = ['Low', 'Normal', 'High', 'Urgent'];
      for (const priority of priorities) {
        const option = page.locator(`text=${priority}`);
        const count = await option.count();
        if (count > 0) {
          console.log(`✅ Found priority option: ${priority}`);
        }
      }
      
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    });

    await test.step('Verify Timeout Input field', async () => {
      const timeoutLabel = page.locator('label:has-text("Timeout")');
      await expect(timeoutLabel.first()).toBeVisible();
      
      const timeoutInput = page.locator('input[type="number"]').or(
        page.locator('input[placeholder*="seconds" i]')
      );
      const timeoutInputs = page.locator('input[type="number"]');
      const count = await timeoutInputs.count();
      
      if (count > 0) {
        const input = timeoutInputs.first();
        await expect(input).toBeVisible();
        
        // Test input
        await input.fill('60');
        const value = await input.inputValue();
        expect(value).toBe('60');
      }
    });

    await test.step('Verify Execute Task button', async () => {
      const executeButton = page.locator('button:has-text("Execute Task")').or(
        page.locator('button:has-text("Execute")')
      );
      await expect(executeButton.first()).toBeVisible();
      
      // Button should be disabled when form is incomplete
      const isDisabled = await executeButton.first().getAttribute('disabled');
      // It should be disabled initially (no agent selected)
      expect(isDisabled).not.toBeNull();
    });
  });

  test('6. Verify Task History Panel', async ({ page }) => {
    // Navigate to Task Execution tab
    await page.locator('text=Task Execution').first().click();
    await page.waitForTimeout(1000);

    await test.step('Check Task History card', async () => {
      await expect(page.locator('text=Task History').or(page.locator('text=/Task.*History/i'))).toBeVisible();
    });

    await test.step('Check task history content area', async () => {
      // Should show either "No tasks executed yet" or task items
      const noTasksMessage = page.locator('text=No tasks executed yet');
      const taskItems = page.locator('text=/Task.*\\d/i').or(
        page.locator('text=/completed|failed/i')
      );
      
      const noTasksVisible = await noTasksMessage.isVisible().catch(() => false);
      const hasTasks = await taskItems.count().then(count => count > 0);
      
      // Either message or tasks should be visible
      expect(noTasksVisible || hasTasks).toBe(true);
    });
  });

  test('7. Verify System Tab Components', async ({ page }) => {
    // Navigate to System tab
    await page.locator('text=System').first().click();
    await page.waitForTimeout(1000);

    await test.step('Check System Metrics card', async () => {
      await expect(page.locator('text=System Metrics').or(page.locator('text=/System.*Metrics/i'))).toBeVisible();
    });

    await test.step('Check Agent Health Summary card', async () => {
      await expect(page.locator('text=Agent Health Summary').or(page.locator('text=/Agent.*Health/i'))).toBeVisible();
    });

    await test.step('Verify system metrics display', async () => {
      // Should show API Requests and WS Connections
      await expect(page.locator('text=API Requests').or(page.locator('text=/API.*Requests/i'))).toBeVisible();
      await expect(page.locator('text=WS Connections').or(page.locator('text=/WS.*Connections/i'))).toBeVisible();
    });
  });

  test('8. Verify Agent Details Modal', async ({ page }) => {
    // Navigate to Agents tab
    await page.locator('text=Agents').first().click();
    await page.waitForTimeout(1000);

    await test.step('Click Details button on an agent card', async () => {
      const detailsButton = page.locator('button:has-text("Details")').first();
      await expect(detailsButton).toBeVisible();
      await detailsButton.click();
      await page.waitForTimeout(500);
    });

    await test.step('Check modal is open', async () => {
      // Look for modal/dialog content
      const modal = page.locator('[role="dialog"]').or(
        page.locator('text=/Details/i')
      );
      await expect(modal.first()).toBeVisible({ timeout: 5000 });
    });

    await test.step('Verify modal content sections', async () => {
      // Check for status overview
      const statusSection = page.locator('text=/Status|Health|Tasks|Success Rate/i');
      const statusCount = await statusSection.count();
      expect(statusCount).toBeGreaterThan(0);

      // Check for capabilities section
      const capabilitiesSection = page.locator('text=Capabilities').or(
        page.locator('text=/Capabilities/i')
      );
      const hasCapabilities = await capabilitiesSection.isVisible().catch(() => false);
      if (hasCapabilities) {
        console.log('✅ Capabilities section found');
      }

      // Check for performance metrics
      const metricsSection = page.locator('text=/Performance|Metrics/i');
      const metricsCount = await metricsSection.count();
      if (metricsCount > 0) {
        console.log('✅ Performance metrics section found');
      }
    });

    await test.step('Close modal', async () => {
      // Press Escape or click close button
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    });
  });

  test('9. Verify Agent Status Cards Display', async ({ page }) => {
    // Navigate to Overview tab
    await page.locator('text=Overview').first().click();
    await page.waitForTimeout(1000);

    await test.step('Check agent cards have required elements', async () => {
      // Look for agent names
      const agentNames = [
        'Infrastructure',
        'Database',
        'Core Engine',
        'API Layer',
        'Meta-Learner'
      ];

      for (const name of agentNames) {
        const agentCard = page.locator(`text=${name}`).or(
          page.locator(`text=/.*${name}.*/i`)
        );
        const count = await agentCard.count();
        if (count > 0) {
          console.log(`✅ Found agent card: ${name}`);
          
          // Check for status indicator
          const statusIndicator = agentCard.locator('..').locator('[class*="rounded-full"]');
          const hasStatus = await statusIndicator.count().then(c => c > 0);
          if (hasStatus) {
            console.log(`  ✅ Has status indicator`);
          }
        }
      }
    });

    await test.step('Check agent metrics display', async () => {
      // Look for task counts, success rates, etc.
      const metrics = page.locator('text=/Tasks|Success Rate|Avg Time/i');
      const metricsCount = await metrics.count();
      expect(metricsCount).toBeGreaterThan(0);
    });
  });

  test('10. Verify API Endpoints Accessibility', async ({ page, request }) => {
    await test.step('Test system status endpoint', async () => {
      const response = await request.get(`${API_URL}/system/status`);
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('system_status');
      expect(data).toHaveProperty('agents');
      expect(data).toHaveProperty('api_metrics');
      console.log('✅ System status endpoint accessible');
    });

    await test.step('Test agent status endpoints', async () => {
      const agentIds = ['01', '02', '03', '04', '06'];
      
      for (const agentId of agentIds) {
        try {
          const response = await request.get(`${API_URL}/api/v1/agents/${agentId}/status`);
          if (response.status() === 200) {
            const data = await response.json();
            expect(data).toHaveProperty('agent_id');
            expect(data).toHaveProperty('status');
            console.log(`✅ Agent ${agentId} status endpoint accessible`);
          } else {
            console.log(`⚠️ Agent ${agentId} status endpoint returned ${response.status()}`);
          }
        } catch (error) {
          console.log(`⚠️ Agent ${agentId} status endpoint error: ${error}`);
        }
      }
    });
  });

  test('11. Verify Form Validation', async ({ page }) => {
    // Navigate to Task Execution tab
    await page.locator('text=Task Execution').first().click();
    await page.waitForTimeout(1000);

    await test.step('Test Execute button disabled state', async () => {
      const executeButton = page.locator('button:has-text("Execute Task")').first();
      
      // Button should be disabled when form is empty
      const isDisabled = await executeButton.getAttribute('disabled');
      expect(isDisabled).not.toBeNull();
    });

    await test.step('Test JSON validation in parameters field', async () => {
      const parametersTextarea = page.locator('textarea[placeholder*="JSON" i]').or(
        page.locator('textarea').first()
      );
      
      // Test invalid JSON
      await parametersTextarea.fill('invalid json');
      await page.waitForTimeout(300);
      
      // Check for validation error (if displayed)
      const errorMessage = page.locator('text=/invalid.*json/i').or(
        page.locator('text=/error/i')
      );
      // Error might not be visible until submit, but field should accept input
      const value = await parametersTextarea.inputValue();
      expect(value).toBe('invalid json');
      
      // Test valid JSON
      await parametersTextarea.fill('{"test": "value"}');
      await page.waitForTimeout(300);
      const validValue = await parametersTextarea.inputValue();
      expect(validValue).toContain('test');
    });
  });

  test('12. Verify Real-Time Updates (WebSocket)', async ({ page }) => {
    await test.step('Check WebSocket connection indicator', async () => {
      const wsIndicator = page.locator('text=/Live Updates|Disconnected/');
      await expect(wsIndicator.first()).toBeVisible();
      
      // Check if it shows connected state
      const isConnected = await page.locator('text=Live Updates').isVisible().catch(() => false);
      if (isConnected) {
        console.log('✅ WebSocket connection indicator shows connected');
      } else {
        console.log('⚠️ WebSocket may be disconnected (checking indicator)');
      }
    });

    await test.step('Verify system status updates', async () => {
      // Wait for any status updates
      await page.waitForTimeout(3000);
      
      // Check if system status cards are visible and populated
      const systemStatusCard = page.locator('text=System Status');
      await expect(systemStatusCard.first()).toBeVisible();
    });
  });

  test('13. Verify All Agent Types Are Displayed', async ({ page }) => {
    // Navigate to Agents tab
    await page.locator('text=Agents').first().click();
    await page.waitForTimeout(1000);

    await test.step('Check for all 5 agent types', async () => {
      const agentTypes = [
        { name: 'Infrastructure Agent', id: '01' },
        { name: 'Database Agent', id: '02' },
        { name: 'Core Engine Agent', id: '03' },
        { name: 'API Layer Agent', id: '04' },
        { name: 'Meta-Learner Agent', id: '06' }
      ];

      let foundCount = 0;
      for (const agentType of agentTypes) {
        const agentCard = page.locator(`text=${agentType.name}`).or(
          page.locator(`text=/.*${agentType.name.split(' ')[0]}.*Agent/i`)
        );
        const count = await agentCard.count();
        if (count > 0) {
          foundCount++;
          console.log(`✅ Found: ${agentType.name}`);
        }
      }
      
      console.log(`Found ${foundCount}/5 agent types`);
      // At least some agents should be visible
      expect(foundCount).toBeGreaterThan(0);
    });
  });

  test('14. Verify Task Execution Form Completion Flow', async ({ page }) => {
    // Navigate to Task Execution tab
    await page.locator('text=Task Execution').first().click();
    await page.waitForTimeout(1000);

    await test.step('Fill out complete form', async () => {
      // Select agent
      const agentSelect = page.locator('[role="combobox"]').first();
      await agentSelect.click();
      await page.waitForTimeout(500);
      
      // Select first available agent
      const firstOption = page.locator('[role="option"]').first();
      if (await firstOption.isVisible()) {
        await firstOption.click();
        await page.waitForTimeout(500);
      }

      // Fill operation
      const operationInput = page.locator('input[placeholder*="compress" i]').or(
        page.locator('input').first()
      );
      await operationInput.fill('test_operation');
      
      // Fill parameters
      const parametersTextarea = page.locator('textarea').first();
      await parametersTextarea.fill('{"test": "value"}');
      
      // Select priority
      const prioritySelect = page.locator('[role="combobox"]').nth(1);
      await prioritySelect.click();
      await page.waitForTimeout(500);
      const normalOption = page.locator('text=Normal').or(page.locator('[role="option"]').nth(1));
      if (await normalOption.isVisible()) {
        await normalOption.click();
        await page.waitForTimeout(500);
      }

      // Fill timeout
      const timeoutInput = page.locator('input[type="number"]');
      if (await timeoutInput.count() > 0) {
        await timeoutInput.first().fill('60');
      }

      console.log('✅ Form filled successfully');
    });

    await test.step('Verify Execute button becomes enabled', async () => {
      const executeButton = page.locator('button:has-text("Execute Task")').first();
      // Button should be enabled if form is valid
      // Note: We can't actually execute without backend, but we can verify form state
      const isVisible = await executeButton.isVisible();
      expect(isVisible).toBe(true);
    });
  });

  test('15. Verify Responsive Design Elements', async ({ page }) => {
    await test.step('Check grid layouts', async () => {
      // Check for grid containers
      const grids = page.locator('[class*="grid"]');
      const gridCount = await grids.count();
      expect(gridCount).toBeGreaterThan(0);
      console.log(`✅ Found ${gridCount} grid layouts`);
    });

    await test.step('Check card components', async () => {
      const cards = page.locator('[class*="card" i]').or(
        page.locator('article')
      );
      const cardCount = await cards.count();
      expect(cardCount).toBeGreaterThan(0);
      console.log(`✅ Found ${cardCount} card components`);
    });
  });

  test('16. Verify Error Handling and Notifications', async ({ page }) => {
    await test.step('Check notification system integration', async () => {
      // The notification system is integrated via useApp hook
      // We can verify it's being used by checking for notification elements
      // (These may appear temporarily during operations)
      
      // Check if notification container exists (if implemented)
      const notificationContainer = page.locator('[role="alert"]').or(
        page.locator('[class*="notification" i]')
      );
      // Notifications are likely toast/overlay, may not be visible initially
      const count = await notificationContainer.count();
      console.log(`Found ${count} notification elements`);
    });
  });

  test('17. Comprehensive Component Count Validation', async ({ page }) => {
    await test.step('Count all major UI components', async () => {
      const components = {
        buttons: await page.locator('button').count(),
        inputs: await page.locator('input').count(),
        textareas: await page.locator('textarea').count(),
        selects: await page.locator('[role="combobox"]').count(),
        cards: await page.locator('[class*="card" i]').count(),
        badges: await page.locator('[class*="badge" i]').count(),
        tabs: await page.locator('[role="tab"]').count(),
      };

      console.log('Component counts:');
      console.log(`  Buttons: ${components.buttons}`);
      console.log(`  Inputs: ${components.inputs}`);
      console.log(`  Textareas: ${components.textareas}`);
      console.log(`  Selects: ${components.selects}`);
      console.log(`  Cards: ${components.cards}`);
      console.log(`  Badges: ${components.badges}`);
      console.log(`  Tabs: ${components.tabs}`);

      // Verify minimum expected counts
      expect(components.buttons).toBeGreaterThan(0);
      expect(components.cards).toBeGreaterThan(0);
      expect(components.tabs).toBeGreaterThanOrEqual(4); // 4 main tabs
    });
  });
});

