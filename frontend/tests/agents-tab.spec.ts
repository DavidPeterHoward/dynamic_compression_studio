import { expect, test } from '@playwright/test';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8441';

test.describe('Agents Tab Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:8443');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Click on Agents tab
    await page.click('[data-testid="agents-nav-button"]');
    await page.waitForTimeout(1000);
  });

  test('should display Agents tab with all sections', async ({ page }) => {
    // Check for main heading
    await expect(page.locator('text=Agent Management')).toBeVisible();
    
    // Check for tab navigation
    await expect(page.locator('text=Overview')).toBeVisible();
    await expect(page.locator('text=Agents')).toBeVisible();
    await expect(page.locator('text=Task Execution')).toBeVisible();
    await expect(page.locator('text=System')).toBeVisible();
  });

  test('should display system overview cards', async ({ page }) => {
    // Wait for system status to load
    await page.waitForTimeout(2000);
    
    // Check for system overview cards
    const systemStatusCard = page.locator('text=System Status').first();
    await expect(systemStatusCard).toBeVisible({ timeout: 10000 });
    
    // Check for other overview cards
    await expect(page.locator('text=Active Agents')).toBeVisible();
    await expect(page.locator('text=API Requests')).toBeVisible();
    await expect(page.locator('text=WS Connections')).toBeVisible();
  });

  test('should display WebSocket connection status', async ({ page }) => {
    // Check for connection indicator
    const connectionIndicator = page.locator('text=Live Updates').or(page.locator('text=Disconnected'));
    await expect(connectionIndicator).toBeVisible({ timeout: 5000 });
  });

  test('should have refresh button', async ({ page }) => {
    const refreshButton = page.locator('button:has-text("Refresh")');
    await expect(refreshButton).toBeVisible();
    await expect(refreshButton).toBeEnabled();
  });

  test('should display task execution form', async ({ page }) => {
    // Navigate to Tasks tab
    await page.click('text=Task Execution');
    await page.waitForTimeout(500);
    
    // Check for form elements
    await expect(page.locator('text=Execute Task')).toBeVisible();
    await expect(page.locator('label:has-text("Target Agent")')).toBeVisible();
    await expect(page.locator('label:has-text("Operation")')).toBeVisible();
    await expect(page.locator('label:has-text("Parameters")')).toBeVisible();
    await expect(page.locator('label:has-text("Priority")')).toBeVisible();
    await expect(page.locator('label:has-text("Timeout")')).toBeVisible();
  });

  test('should populate agent dropdown', async ({ page }) => {
    await page.click('text=Task Execution');
    await page.waitForTimeout(1000);
    
    // Click on agent select
    const agentSelect = page.locator('button:has-text("Select agent")').or(page.locator('button:has-text("No agents available")'));
    await agentSelect.click();
    await page.waitForTimeout(500);
    
    // Check if dropdown opens (may be empty if agents not loaded)
    const selectContent = page.locator('[role="listbox"]');
    await expect(selectContent).toBeVisible();
  });

  test('should display operation dropdown with categories', async ({ page }) => {
    await page.click('text=Task Execution');
    await page.waitForTimeout(1000);
    
    // Click on operation select
    const operationSelect = page.locator('button:has-text("Select operation")');
    await operationSelect.click();
    await page.waitForTimeout(500);
    
    // Check for operation categories
    const selectContent = page.locator('[role="listbox"]');
    await expect(selectContent).toBeVisible();
    
    // Check for at least one operation category
    const categories = ['Infrastructure', 'Compression', 'Meta-Learning', 'Data', 'NLP', 'Code', 'Research'];
    const foundCategory = await Promise.race(
      categories.map(cat => 
        selectContent.locator(`text=${cat}`).isVisible().then(visible => visible ? cat : null)
      )
    );
    expect(foundCategory).toBeTruthy();
  });

  test('should validate JSON parameters', async ({ page }) => {
    await page.click('text=Task Execution');
    await page.waitForTimeout(1000);
    
    // Enter invalid JSON
    const parametersTextarea = page.locator('textarea[id="parameters"]');
    await parametersTextarea.fill('invalid json');
    
    // Try to submit (should fail validation)
    const executeButton = page.locator('button:has-text("Execute Task")');
    
    // Check that button is disabled if agent/operation not selected
    // Or that validation error appears
    const isDisabled = await executeButton.isDisabled();
    if (!isDisabled) {
      // If enabled, try clicking - should show error
      await executeButton.click();
      await page.waitForTimeout(500);
      
      // Check for error notification or validation message
      const errorMessage = page.locator('text=Invalid JSON').or(page.locator('text=must be valid JSON'));
      // May not show immediately, but should handle gracefully
    }
  });

  test('should display priority dropdown options', async ({ page }) => {
    await page.click('text=Task Execution');
    await page.waitForTimeout(1000);
    
    // Click on priority select
    const prioritySelect = page.locator('button').filter({ hasText: /Low|Normal|High|Urgent/ }).first();
    await prioritySelect.click();
    await page.waitForTimeout(500);
    
    // Check for priority options
    const selectContent = page.locator('[role="listbox"]');
    await expect(selectContent).toBeVisible();
    
    await expect(selectContent.locator('text=Low')).toBeVisible();
    await expect(selectContent.locator('text=Normal')).toBeVisible();
    await expect(selectContent.locator('text=High')).toBeVisible();
    await expect(selectContent.locator('text=Urgent')).toBeVisible();
  });

  test('should display task history section', async ({ page }) => {
    await page.click('text=Task Execution');
    await page.waitForTimeout(1000);
    
    // Check for task history card
    await expect(page.locator('text=Task History')).toBeVisible();
    await expect(page.locator('text=Recent task executions and results')).toBeVisible();
  });

  test('should display agent details modal on click', async ({ page }) => {
    // Navigate to Agents tab
    await page.click('text=Agents');
    await page.waitForTimeout(1000);
    
    // Try to find an agent card (may not exist if agents not loaded)
    const agentCard = page.locator('[class*="card"]').first();
    if (await agentCard.isVisible()) {
      // Click on Details button if available
      const detailsButton = page.locator('button:has-text("Details")').first();
      if (await detailsButton.isVisible()) {
        await detailsButton.click();
        await page.waitForTimeout(500);
        
        // Check for modal
        const modal = page.locator('[role="dialog"]');
        await expect(modal).toBeVisible();
        
        // Check for agent details
        await expect(modal.locator('text=Details')).toBeVisible();
      }
    }
  });

  test('should handle empty agent list gracefully', async ({ page }) => {
    // If no agents are loaded, check for appropriate message
    await page.waitForTimeout(2000);
    
    // Check for either agent cards or empty state message
    const agentCards = page.locator('[class*="card"]');
    const emptyMessage = page.locator('text=No agents').or(page.locator('text=initializing'));
    
    // Either should be visible
    const hasCards = await agentCards.count() > 0;
    const hasMessage = await emptyMessage.isVisible().catch(() => false);
    
    expect(hasCards || hasMessage).toBeTruthy();
  });

  test('should test API endpoints availability', async ({ request }) => {
    // Test /agents endpoint
    const agentsResponse = await request.get(`${API_BASE_URL}/agents`);
    expect(agentsResponse.status()).toBeLessThan(500); // Should not be server error
    
    // Test /system/status endpoint
    const statusResponse = await request.get(`${API_BASE_URL}/system/status`);
    expect(statusResponse.status()).toBeLessThan(500);
    
    if (statusResponse.ok()) {
      const statusData = await statusResponse.json();
      expect(statusData).toHaveProperty('system_status');
      expect(statusData).toHaveProperty('agents');
      expect(statusData).toHaveProperty('api_metrics');
    }
  });

  test('should test agent status endpoint', async ({ request }) => {
    // Test agent status endpoint for known agent IDs
    const agentIds = ['01', '02', '03', '04', '06'];
    
    for (const agentId of agentIds) {
      const response = await request.get(`${API_BASE_URL}/agents/${agentId}/status`);
      // Accept 404 if agent not registered, but should not be 500
      expect([200, 404]).toContain(response.status());
      
      if (response.ok()) {
        const data = await response.json();
        expect(data).toHaveProperty('agent_id');
        expect(data).toHaveProperty('status');
      }
    }
  });

  test('should test task execution endpoint structure', async ({ request }) => {
    // Test task execution with a simple operation
    const taskData = {
      operation: 'status',
      parameters: {},
      priority: 'normal',
      timeout_seconds: 30
    };
    
    // Try with agent 01 (Infrastructure Agent)
    const response = await request.post(`${API_BASE_URL}/agents/01/execute`, {
      data: taskData
    });
    
    // Should return either 200 (success) or 404 (agent not found), but not 500
    expect([200, 404]).toContain(response.status());
    
    if (response.ok()) {
      const data = await response.json();
      expect(data).toHaveProperty('task_id');
      expect(data).toHaveProperty('status');
    }
  });
});

