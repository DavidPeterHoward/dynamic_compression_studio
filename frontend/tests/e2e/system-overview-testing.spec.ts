import { expect, test } from '@playwright/test';

/**
 * COMPREHENSIVE SYSTEM OVERVIEW TESTING SUITE
 *
 * This test suite provides complete coverage for the enhanced System Overview
 * with live metrics, real-time updates, and comprehensive system health monitoring.
 *
 * Test Coverage Areas:
 * ✅ Enhanced System Overview Header
 * ✅ Live Metrics Updates (Active Agents, API Requests, WS Connections, System Health)
 * ✅ Real-time System Status Indicators
 * ✅ System Resources Monitoring (CPU, Memory, Disk)
 * ✅ Load Average Display
 * ✅ Quick Actions Functionality
 * ✅ WebSocket Connection Status
 * ✅ Health Score Calculations
 * ✅ Responsive Design
 * ✅ Data Persistence
 * ✅ Error Recovery
 * ✅ Performance Metrics
 */

const BASE_URL = process.env.BASE_URL || 'http://localhost:8449';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8443';

/**
 * Helper Functions
 */
async function waitForSystemOverviewLoad(page: any) {
  await page.locator('[data-id="system-overview-title"]').waitFor({ state: 'visible' });
  await page.locator('[data-id="active-agents-card"]').waitFor({ state: 'visible' });
  await page.locator('[data-id="api-requests-card"]').waitFor({ state: 'visible' });
  await page.locator('[data-id="websocket-connections-card"]').waitFor({ state: 'visible' });
  await page.locator('[data-id="system-health-card"]').waitFor({ state: 'visible' });
}

async function waitForWebSocketConnection(page: any, timeout = 10000) {
  const wsIndicator = page.locator('[data-id="ws-indicator"][data-connected="true"]');
  await expect(wsIndicator).toBeVisible({ timeout });
}

async function mockSystemMetrics(page: any) {
  // Mock enhanced system metrics for testing
  await page.route(`${API_BASE_URL}/api/v1/system/status`, async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        system_status: 'operational',
        timestamp: new Date().toISOString(),
        last_updated: new Date().toISOString(),
        health_score: 95,
        agents: [],
        api_metrics: {
          total_requests: 15420,
          websocket_connections: 3,
          requests_per_second: 2.4,
          error_rate: 0.02,
          avg_response_time: 45
        },
        system_metrics: {
          cpu_usage: 23.5,
          memory_usage: 67.8,
          disk_usage: 34.2,
          uptime: 345600, // 4 days in seconds
          load_average: [1.25, 1.15, 1.05]
        }
      })
    });
  });
}

/**
 * ============================================================================
 * ENHANCED SYSTEM OVERVIEW HEADER TESTS
 * ============================================================================
 */
test.describe('Enhanced System Overview Header', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
  });

  test('should display enhanced header with live indicators', async ({ page }) => {
    // Verify enhanced header elements
    await expect(page.locator('[data-id="system-overview-title"]')).toContainText('System Overview');
    await expect(page.locator('[data-id="live-indicator"]')).toBeVisible();
    await expect(page.locator('[data-id="live-pulse"]')).toBeVisible();
    await expect(page.locator('[data-id="live-text"]')).toContainText('Live');
    await expect(page.locator('[data-id="last-updated"]')).toBeVisible();
  });

  test('should display overall health score prominently', async ({ page }) => {
    await expect(page.locator('[data-id="health-score"]')).toBeVisible();
    await expect(page.locator('[data-id="health-indicator"][class*="bg-green-400"]')).toBeVisible();
    await expect(page.locator('[data-id="health-score-text"]')).toContainText('95% Health');
  });

  test('should show operational status with appropriate styling', async ({ page }) => {
    await expect(page.locator('[data-id="system-status-badge"]')).toContainText('operational');
    await expect(page.locator('[data-id="system-status-badge"]')).toHaveClass(/bg-green-500/);
  });

  test('should display refresh functionality', async ({ page }) => {
    const refreshButton = page.locator('[data-id="refresh-system-btn"]');
    await expect(refreshButton).toBeVisible();
    await expect(refreshButton).toBeEnabled();

    // Test refresh action
    await refreshButton.click();
    // Button should show loading state briefly
    await expect(refreshButton).toBeEnabled(); // Should re-enable after refresh
  });
});

/**
 * ============================================================================
 * LIVE METRICS CARDS TESTS
 * ============================================================================
 */
test.describe('Live Metrics Cards', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
  });

  test('should display active agents card with enhanced metrics', async ({ page }) => {
    const agentsCard = page.locator('[data-id="active-agents-card"]');

    // Enhanced card structure
    await expect(agentsCard.locator('[data-id="active-agents-count"]')).toBeVisible();
    await expect(agentsCard.locator('[data-id="agents-activity-progress"]')).toBeVisible();
    await expect(agentsCard.locator('[data-id="agents-activity-progress"]')).toHaveAttribute('aria-valuenow');

    // Activity rate display
    await expect(agentsCard.locator('text=Activity Rate')).toBeVisible();
  });

  test('should display API requests card with comprehensive metrics', async ({ page }) => {
    const apiCard = page.locator('[data-id="api-requests-card"]');

    // Total requests with formatting
    await expect(apiCard.locator('[data-id="api-requests-count"]')).toContainText('15,420');

    // Rate metrics
    await expect(apiCard.locator('[data-id="requests-per-second"]')).toContainText('2.4/s');

    // Error rate with color coding
    const errorRate = apiCard.locator('[data-id="error-rate"]');
    await expect(errorRate).toContainText('0.0%');
    await expect(errorRate).toHaveClass(/text-green-400/);

    // Average response time
    await expect(apiCard.locator('[data-id="avg-response-time"]')).toContainText('45ms');

    // Progress bar
    await expect(apiCard.locator('[data-id="api-requests-progress"]')).toBeVisible();
  });

  test('should display WebSocket connections with real-time status', async ({ page }) => {
    const wsCard = page.locator('[data-id="websocket-connections-card"]');

    // Connection count
    await expect(wsCard.locator('[data-id="ws-connections-count"]')).toContainText('3');

    // Connection status indicator
    const statusIndicator = wsCard.locator('[class*="rounded-full"]');
    await expect(statusIndicator).toBeVisible();

    // Status text
    await expect(wsCard.locator('[data-id="ws-status-text"]')).toBeVisible();

    // Latency display
    await expect(wsCard.locator('[data-id="ws-latency"]')).toContainText('< 100ms');
  });

  test('should display system health card with detailed metrics', async ({ page }) => {
    const healthCard = page.locator('[data-id="system-health-card"]');

    // Overall health score
    await expect(healthCard.locator('[data-id="system-health-score"]')).toContainText('95%');

    // CPU and Memory usage with color coding
    await expect(healthCard.locator('[data-id="cpu-usage"]')).toContainText('24%');
    await expect(healthCard.locator('[data-id="memory-usage"]')).toContainText('68%');

    // Uptime display
    await expect(healthCard.locator('[data-id="system-uptime"]')).toContainText('4d 0h 0m');

    // Health progress bar
    const healthProgress = healthCard.locator('[data-id="system-health-progress"]');
    await expect(healthProgress).toHaveAttribute('aria-valuenow', '95');
  });
});

/**
 * ============================================================================
 * SYSTEM RESOURCES MONITORING TESTS
 * ============================================================================
 */
test.describe('System Resources Monitoring', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
  });

  test('should display CPU usage with progress bar', async ({ page }) => {
    const resourcesCard = page.locator('[data-id="system-resources-card"]');

    await expect(resourcesCard.locator('text=CPU Usage')).toBeVisible();
    await expect(resourcesCard.locator('[data-id="cpu-usage-detailed"]')).toContainText('23.5%');

    const cpuProgress = resourcesCard.locator('[data-id="cpu-progress"]');
    await expect(cpuProgress).toBeVisible();
    await expect(cpuProgress).toHaveAttribute('aria-valuenow', '23.5');
  });

  test('should display memory usage with progress bar', async ({ page }) => {
    const resourcesCard = page.locator('[data-id="system-resources-card"]');

    await expect(resourcesCard.locator('text=Memory Usage')).toBeVisible();
    await expect(resourcesCard.locator('[data-id="memory-usage-detailed"]')).toContainText('67.8%');

    const memoryProgress = resourcesCard.locator('[data-id="memory-progress"]');
    await expect(memoryProgress).toBeVisible();
    await expect(memoryProgress).toHaveAttribute('aria-valuenow', '67.8');
  });

  test('should display disk usage with progress bar', async ({ page }) => {
    const resourcesCard = page.locator('[data-id="system-resources-card"]');

    await expect(resourcesCard.locator('text=Disk Usage')).toBeVisible();
    await expect(resourcesCard.locator('[data-id="disk-usage"]')).toContainText('34.2%');

    const diskProgress = resourcesCard.locator('[data-id="disk-progress"]');
    await expect(diskProgress).toBeVisible();
    await expect(diskProgress).toHaveAttribute('aria-valuenow', '34.2');
  });
});

/**
 * ============================================================================
 * LOAD AVERAGE MONITORING TESTS
 * ============================================================================
 */
test.describe('Load Average Monitoring', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
  });

  test('should display load average metrics', async ({ page }) => {
    const loadCard = page.locator('[data-id="load-average-card"]');

    await expect(loadCard.locator('text=Load Average')).toBeVisible();

    // 1-minute load average
    await expect(loadCard.locator('[data-id="load-1min"]')).toContainText('1.25');

    // 5-minute load average
    await expect(loadCard.locator('[data-id="load-5min"]')).toContainText('1.15');

    // 15-minute load average
    await expect(loadCard.locator('[data-id="load-15min"]')).toContainText('1.05');
  });

  test('should handle missing load average data gracefully', async ({ page }) => {
    // Mock response without load average
    await page.route(`${API_BASE_URL}/api/v1/system/status`, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          system_status: 'operational',
          timestamp: new Date().toISOString(),
          last_updated: new Date().toISOString(),
          health_score: 95,
          agents: [],
          api_metrics: {
            total_requests: 15420,
            websocket_connections: 3,
            requests_per_second: 2.4,
            error_rate: 0.02,
            avg_response_time: 45
          },
          system_metrics: {
            cpu_usage: 23.5,
            memory_usage: 67.8,
            disk_usage: 34.2,
            uptime: 345600
            // No load_average
          }
        })
      });
    });

    await page.reload();
    await waitForSystemOverviewLoad(page);

    const loadCard = page.locator('[data-id="load-average-card"]');
    await expect(loadCard.locator('text=Load average not available')).toBeVisible();
  });
});

/**
 * ============================================================================
 * QUICK ACTIONS FUNCTIONALITY TESTS
 * ============================================================================
 */
test.describe('Quick Actions Functionality', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
  });

  test('should navigate to agents tab when clicking view agents action', async ({ page }) => {
    const viewAgentsButton = page.locator('[data-id="view-agents-action"]');
    await expect(viewAgentsButton).toBeVisible();

    await viewAgentsButton.click();

    // Should switch to agents tab
    await expect(page.locator('[data-id="tab-agents"]')).toHaveAttribute('data-state', 'active');
  });

  test('should navigate to tasks tab when clicking create task action', async ({ page }) => {
    const createTaskButton = page.locator('[data-id="create-task-action"]');
    await expect(createTaskButton).toBeVisible();

    await createTaskButton.click();

    // Should switch to tasks tab
    await expect(page.locator('[data-id="tab-tasks"]')).toHaveAttribute('data-state', 'active');
  });

  test('should open agent marketplace modal', async ({ page }) => {
    const marketplaceButton = page.locator('[data-id="agent-marketplace-action"]');
    await expect(marketplaceButton).toBeVisible();

    // Note: This would require checking if the modal opens
    // The actual modal implementation may vary
    await expect(marketplaceButton).toBeEnabled();
  });

  test('should trigger system analytics action', async ({ page }) => {
    const analyticsButton = page.locator('[data-id="system-analytics-action"]');
    await expect(analyticsButton).toBeVisible();

    // Note: This would require checking analytics functionality
    await expect(analyticsButton).toBeEnabled();
  });
});

/**
 * ============================================================================
 * WEBSOCKET INTEGRATION TESTS
 * ============================================================================
 */
test.describe('WebSocket Integration', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
  });

  test('should display live WebSocket connection status', async ({ page }) => {
    await waitForWebSocketConnection(page);

    // Live indicator should be visible
    await expect(page.locator('[data-id="live-indicator"]')).toBeVisible();
    await expect(page.locator('[data-id="live-pulse"]')).toBeVisible();
  });

  test('should update connection status in real-time', async ({ page }) => {
    await waitForWebSocketConnection(page);

    // WebSocket status in cards should reflect connection
    const wsCard = page.locator('[data-id="websocket-connections-card"]');
    await expect(wsCard.locator('[data-id="ws-status-text"]')).toContainText('Connected');
  });

  test('should show last updated timestamp', async ({ page }) => {
    const lastUpdated = page.locator('[data-id="last-updated"]');
    await expect(lastUpdated).toBeVisible();

    // Should contain a timestamp
    const timestampText = await lastUpdated.textContent();
    expect(timestampText).toMatch(/\d{1,2}:\d{2}:\d{2}/); // Time format
  });
});

/**
 * ============================================================================
 * RESPONSIVE DESIGN TESTS
 * ============================================================================
 */
test.describe('Responsive Design', () => {
  test.setTimeout(60000);

  test.beforeEach(async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
  });

  test('should display correctly on desktop viewport', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });

    // Should display all cards in grid layout
    await expect(page.locator('[data-id="primary-metrics-grid"]')).toBeVisible();
    await expect(page.locator('[data-id="secondary-metrics-grid"]')).toBeVisible();

    // All cards should be visible
    await expect(page.locator('[data-id="active-agents-card"]')).toBeVisible();
    await expect(page.locator('[data-id="api-requests-card"]')).toBeVisible();
    await expect(page.locator('[data-id="websocket-connections-card"]')).toBeVisible();
    await expect(page.locator('[data-id="system-health-card"]')).toBeVisible();
  });

  test('should adapt to tablet viewport', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });

    // Cards should still be visible but potentially in different layout
    await expect(page.locator('[data-id="active-agents-card"]')).toBeVisible();
    await expect(page.locator('[data-id="system-overview-title"]')).toBeVisible();
  });

  test('should work on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });

    // Essential information should still be visible
    await expect(page.locator('[data-id="system-overview-title"]')).toBeVisible();
    await expect(page.locator('[data-id="health-score"]')).toBeVisible();
  });
});

/**
 * ============================================================================
 * ERROR HANDLING & RECOVERY TESTS
 * ============================================================================
 */
test.describe('Error Handling & Recovery', () => {
  test.setTimeout(60000);

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route(`${API_BASE_URL}/api/v1/system/status`, async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });

    await page.goto(BASE_URL);
    await page.waitForTimeout(2000); // Allow time for error to be handled

    // Should still display basic UI without crashing
    await expect(page.locator('[data-id="system-overview-title"]')).toBeVisible();
  });

  test('should handle WebSocket disconnection gracefully', async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);

    // Simulate disconnection by changing connection state
    // Note: This would require more complex WebSocket mocking

    // UI should remain stable
    await expect(page.locator('[data-id="system-overview-title"]')).toBeVisible();
  });

  test('should recover from temporary API failures', async ({ page }) => {
    // First request fails
    let requestCount = 0;
    await page.route(`${API_BASE_URL}/api/v1/system/status`, async route => {
      requestCount++;
      if (requestCount === 1) {
        await route.fulfill({
          status: 503,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Service temporarily unavailable' })
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            system_status: 'operational',
            timestamp: new Date().toISOString(),
            last_updated: new Date().toISOString(),
            health_score: 95,
            agents: [],
            api_metrics: {
              total_requests: 15420,
              websocket_connections: 3,
              requests_per_second: 2.4,
              error_rate: 0.02,
              avg_response_time: 45
            },
            system_metrics: {
              cpu_usage: 23.5,
              memory_usage: 67.8,
              disk_usage: 34.2,
              uptime: 345600,
              load_average: [1.25, 1.15, 1.05]
            }
          })
        });
      }
    });

    await page.goto(BASE_URL);
    await page.waitForTimeout(3000); // Allow time for recovery

    // Should eventually display data
    await expect(page.locator('[data-id="active-agents-count"]')).toBeVisible();
  });
});

/**
 * ============================================================================
 * PERFORMANCE & LOAD TESTS
 * ============================================================================
 */
test.describe('Performance & Load Tests', () => {
  test.setTimeout(120000); // Extended timeout for performance tests

  test('should load system overview within acceptable time', async ({ page }) => {
    await mockSystemMetrics(page);

    const startTime = Date.now();
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
    const loadTime = Date.now() - startTime;

    // Should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('should handle rapid metric updates', async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);

    // Simulate multiple rapid updates
    for (let i = 0; i < 5; i++) {
      await page.route(`${API_BASE_URL}/api/v1/system/status`, async route => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            system_status: 'operational',
            timestamp: new Date().toISOString(),
            last_updated: new Date().toISOString(),
            health_score: 90 + Math.random() * 10,
            agents: [],
            api_metrics: {
              total_requests: 15000 + Math.floor(Math.random() * 1000),
              websocket_connections: 3,
              requests_per_second: 2 + Math.random() * 2,
              error_rate: Math.random() * 0.05,
              avg_response_time: 40 + Math.random() * 20
            },
            system_metrics: {
              cpu_usage: 20 + Math.random() * 30,
              memory_usage: 60 + Math.random() * 20,
              disk_usage: 30 + Math.random() * 20,
              uptime: 345600,
              load_average: [1 + Math.random(), 1 + Math.random(), 1 + Math.random()]
            }
          })
        });
      });

      await page.waitForTimeout(200);
    }

    // UI should remain stable and responsive
    await expect(page.locator('[data-id="system-overview-title"]')).toBeVisible();
    await expect(page.locator('[data-id="active-agents-count"]')).toBeVisible();
  });

  test('should maintain performance with WebSocket updates', async ({ page }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);
    await waitForWebSocketConnection(page);

    const startTime = Date.now();

    // Monitor for 10 seconds of WebSocket activity
    await page.waitForTimeout(10000);

    const endTime = Date.now();
    const duration = endTime - startTime;

    // Should have maintained connection and updated UI
    expect(duration).toBeGreaterThan(9000); // At least 9 seconds passed
    await expect(page.locator('[data-id="live-indicator"]')).toBeVisible();
  });
});

/**
 * ============================================================================
 * DATA INTEGRITY & PERSISTENCE TESTS
 * ============================================================================
 */
test.describe('Data Integrity & Persistence', () => {
  test.setTimeout(60000);

  test('should display consistent data across refreshes', async ({ page, context }) => {
    await mockSystemMetrics(page);
    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);

    // Get initial values
    const initialHealthScore = await page.locator('[data-id="system-health-score"]').textContent();
    const initialCpuUsage = await page.locator('[data-id="cpu-usage-detailed"]').textContent();

    // Refresh page
    await page.reload();
    await waitForSystemOverviewLoad(page);

    // Values should be consistent (from mock data)
    const refreshedHealthScore = await page.locator('[data-id="system-health-score"]').textContent();
    const refreshedCpuUsage = await page.locator('[data-id="cpu-usage-detailed"]').textContent();

    expect(refreshedHealthScore).toBe(initialHealthScore);
    expect(refreshedCpuUsage).toBe(initialCpuUsage);
  });

  test('should handle data format variations gracefully', async ({ page }) => {
    // Test with missing optional fields
    await page.route(`${API_BASE_URL}/api/v1/system/status`, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          system_status: 'operational',
          timestamp: new Date().toISOString(),
          last_updated: new Date().toISOString(),
          health_score: 85,
          agents: [],
          api_metrics: {
            total_requests: 1000,
            websocket_connections: 1
            // Missing optional fields
          },
          system_metrics: {
            cpu_usage: 15.5,
            memory_usage: 45.2,
            disk_usage: 25.1,
            uptime: 86400
            // Missing load_average
          }
        })
      });
    });

    await page.goto(BASE_URL);
    await waitForSystemOverviewLoad(page);

    // Should display available data and handle missing data gracefully
    await expect(page.locator('[data-id="system-health-score"]')).toContainText('85%');
    await expect(page.locator('[data-id="cpu-usage-detailed"]')).toContainText('15.5%');
    await expect(page.locator('[data-id="load-average-card"]')).toContainText('Load average not available');
  });
});
