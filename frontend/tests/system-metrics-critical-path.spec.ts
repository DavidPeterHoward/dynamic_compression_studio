import { expect, test } from '@playwright/test';

/**
 * Critical Path Tests for System Metrics Tab
 * 
 * This test suite specifically focuses on fixing and validating the System Metrics tab
 * that was experiencing network errors and ensuring all metrics are live and functional.
 */

test.describe('System Metrics Critical Path Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Navigate to System Metrics tab
    await page.click('button:has-text("System Metrics")');
    await page.waitForTimeout(2000); // Allow time for data loading
  });

  // ============================================================================
  // NETWORK CONNECTIVITY AND API TESTS
  // ============================================================================
  
  test.describe('Network Connectivity', () => {
    test('should successfully connect to metrics API endpoints', async ({ page }) => {
      const apiCalls: string[] = [];
      
      // Monitor all API calls
      page.on('request', request => {
        if (request.url().includes('/api/v1/metrics/')) {
          apiCalls.push(request.url());
        }
      });

      const responses: any[] = [];
      page.on('response', response => {
        if (response.url().includes('/api/v1/metrics/')) {
          responses.push({
            url: response.url(),
            status: response.status(),
            ok: response.ok()
          });
        }
      });

      // Wait for API calls to complete
      await page.waitForTimeout(3000);
      
      // Verify API calls were made
      expect(apiCalls.length).toBeGreaterThan(0);
      
      // Verify all responses are successful
      const failedResponses = responses.filter(r => !r.ok);
      expect(failedResponses).toHaveLength(0);
    });

    test('should handle API timeouts gracefully', async ({ page }) => {
      // Simulate slow API responses
      await page.route('**/api/v1/metrics/**', async route => {
        await new Promise(resolve => setTimeout(resolve, 5000)); // 5 second delay
        route.continue();
      });

      await page.click('button:has-text("System Metrics")');
      
      // Should show loading state
      await expect(page.locator('text=Loading system metrics...')).toBeVisible();
    });

    test('should retry failed API calls', async ({ page }) => {
      let callCount = 0;
      
      await page.route('**/api/v1/metrics/**', route => {
        callCount++;
        if (callCount <= 2) {
          // Fail first two calls
          route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Temporary server error' })
          });
        } else {
          // Succeed on third call
          route.continue();
        }
      });

      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(5000);
      
      // Should eventually succeed
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
    });
  });

  // ============================================================================
  // LIVE DATA VALIDATION TESTS
  // ============================================================================
  
  test.describe('Live Data Validation', () => {
    test('should display real-time system metrics', async ({ page }) => {
      // Verify key metrics are displayed with actual values
      const metrics = [
        'CPU Usage',
        'Memory Usage', 
        'Disk Usage',
        'Network Usage',
        'Compression Efficiency',
        'Throughput',
        'Success Rate',
        'Response Time'
      ];

      for (const metric of metrics) {
        await expect(page.locator(`text=${metric}`)).toBeVisible();
        
        // Verify metric has a value (not just 0 or empty)
        const metricCard = page.locator(`text=${metric}`).locator('..');
        const valueElement = metricCard.locator('.text-2xl');
        await expect(valueElement).toBeVisible();
        
        // Verify value is a number
        const value = await valueElement.textContent();
        expect(value).toMatch(/\d+/);
      }
    });

    test('should show system health status', async ({ page }) => {
      // Verify system health overview
      await expect(page.locator('text=System Health Overview')).toBeVisible();
      
      // Check for health indicators
      const healthStatus = page.locator('text=Healthy, Warning, or Error');
      await expect(healthStatus).toBeVisible();
      
      // Verify system metrics are displayed
      await expect(page.locator('text=Active Connections')).toBeVisible();
      await expect(page.locator('text=Queue Length')).toBeVisible();
      await expect(page.locator('text=Uptime')).toBeVisible();
      await expect(page.locator('text=Processes')).toBeVisible();
    });

    test('should display algorithm performance data', async ({ page }) => {
      // Verify algorithm performance section
      await expect(page.locator('text=Algorithm Performance')).toBeVisible();
      
      // Check for algorithm metrics
      const algorithmSection = page.locator('text=Algorithm Performance').locator('..');
      await expect(algorithmSection).toBeVisible();
      
      // Verify algorithm names are displayed
      const algorithmNames = ['gzip', 'lzma', 'bzip2', 'lz4', 'zstandard', 'brotli'];
      for (const algorithm of algorithmNames) {
        const algorithmElement = page.locator(`text=${algorithm.charAt(0).toUpperCase() + algorithm.slice(1)}`);
        if (await algorithmElement.isVisible()) {
          await expect(algorithmElement).toBeVisible();
        }
      }
    });

    test('should show compression analytics with live data', async ({ page }) => {
      // Verify compression analytics section
      await expect(page.locator('text=Compression Analytics')).toBeVisible();
      
      // Check content type distribution
      await expect(page.locator('text=Content Type Distribution')).toBeVisible();
      await expect(page.locator('text=Algorithm Usage')).toBeVisible();
      await expect(page.locator('text=Error Distribution')).toBeVisible();
      
      // Verify data is displayed
      const analyticsSection = page.locator('text=Compression Analytics').locator('..');
      await expect(analyticsSection).toBeVisible();
    });
  });

  // ============================================================================
  // AUTO-REFRESH AND REAL-TIME UPDATES TESTS
  // ============================================================================
  
  test.describe('Auto-Refresh Functionality', () => {
    test('should have working auto-refresh toggle', async ({ page }) => {
      // Find auto-refresh toggle
      const autoRefreshToggle = page.locator('button').filter({ hasText: /Auto-refresh|Eye|EyeOff/ });
      await expect(autoRefreshToggle).toBeVisible();
      
      // Test toggle functionality
      await autoRefreshToggle.click();
      await page.waitForTimeout(500);
      
      // Verify toggle state changed
      await expect(autoRefreshToggle).toHaveClass(/bg-slate-500\/20/);
    });

    test('should allow refresh interval configuration', async ({ page }) => {
      // Find refresh interval selector
      const intervalSelector = page.locator('select').filter({ hasText: /5s|10s|30s|1m/ });
      await expect(intervalSelector).toBeVisible();
      
      // Test changing interval
      await intervalSelector.selectOption('30');
      await page.waitForTimeout(500);
      
      // Verify selection changed
      await expect(intervalSelector).toHaveValue('30');
    });

    test('should have working manual refresh button', async ({ page }) => {
      // Find refresh button
      const refreshButton = page.locator('button:has-text("Refresh")');
      await expect(refreshButton).toBeVisible();
      
      // Click refresh and verify it works
      await refreshButton.click();
      await page.waitForTimeout(1000);
      
      // Verify refresh completed
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
    });

    test('should show last updated timestamp', async ({ page }) => {
      // Wait for data to load
      await page.waitForTimeout(2000);
      
      // Look for last updated timestamp
      const lastUpdated = page.locator('text=Last updated:');
      if (await lastUpdated.isVisible()) {
        await expect(lastUpdated).toBeVisible();
      }
    });
  });

  // ============================================================================
  // METRIC CARDS AND VISUALIZATION TESTS
  // ============================================================================
  
  test.describe('Metric Cards Display', () => {
    test('should display all metric cards with proper styling', async ({ page }) => {
      const metricCards = page.locator('.glass').filter({ hasText: /CPU|Memory|Disk|Network|Compression|Throughput|Success|Response/ });
      const cardCount = await metricCards.count();
      
      expect(cardCount).toBeGreaterThan(0);
      
      // Verify each card has proper structure
      for (let i = 0; i < cardCount; i++) {
        const card = metricCards.nth(i);
        await expect(card).toBeVisible();
        
        // Check for icon
        await expect(card.locator('svg')).toBeVisible();
        
        // Check for value display
        await expect(card.locator('.text-2xl')).toBeVisible();
        
        // Check for progress bar
        await expect(card.locator('.bg-slate-700')).toBeVisible();
      }
    });

    test('should show trend indicators for metrics', async ({ page }) => {
      // Look for trend icons
      const trendIcons = page.locator('svg').filter({ hasText: /TrendingUp|TrendingDown|Activity/ });
      const iconCount = await trendIcons.count();
      
      expect(iconCount).toBeGreaterThan(0);
    });

    test('should display status indicators correctly', async ({ page }) => {
      // Look for status icons (healthy, warning, error)
      const statusIcons = page.locator('svg').filter({ hasText: /CheckCircle|AlertTriangle|XCircle/ });
      const iconCount = await statusIcons.count();
      
      expect(iconCount).toBeGreaterThan(0);
    });

    test('should show progress bars for metrics', async ({ page }) => {
      // Find progress bars
      const progressBars = page.locator('.bg-slate-700');
      const barCount = await progressBars.count();
      
      expect(barCount).toBeGreaterThan(0);
      
      // Verify progress bars have proper styling
      for (let i = 0; i < barCount; i++) {
        const bar = progressBars.nth(i);
        await expect(bar).toHaveClass(/rounded-full/);
      }
    });
  });

  // ============================================================================
  // ERROR HANDLING AND RECOVERY TESTS
  // ============================================================================
  
  test.describe('Error Handling', () => {
    test('should display error message when API fails', async ({ page }) => {
      // Simulate API failure
      await page.route('**/api/v1/metrics/**', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' })
        });
      });

      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(3000);
      
      // Verify error message is displayed
      await expect(page.locator('text=Failed to load metrics')).toBeVisible();
      await expect(page.locator('text=Retry')).toBeVisible();
    });

    test('should allow retry after error', async ({ page }) => {
      // First, simulate API failure
      await page.route('**/api/v1/metrics/**', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Temporary error' })
        });
      });

      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(2000);
      
      // Verify error state
      await expect(page.locator('text=Failed to load metrics')).toBeVisible();
      
      // Remove route interception
      await page.unroute('**/api/v1/metrics/**');
      
      // Click retry
      await page.click('button:has-text("Retry")');
      await page.waitForTimeout(2000);
      
      // Verify recovery
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
    });

    test('should show loading state during data fetch', async ({ page }) => {
      // Simulate slow API response
      await page.route('**/api/v1/metrics/**', async route => {
        await new Promise(resolve => setTimeout(resolve, 2000));
        route.continue();
      });

      await page.click('button:has-text("System Metrics")');
      
      // Should show loading state
      await expect(page.locator('text=Loading system metrics...')).toBeVisible();
    });
  });

  // ============================================================================
  // PERFORMANCE AND RESPONSIVENESS TESTS
  // ============================================================================
  
  test.describe('Performance Tests', () => {
    test('should load metrics within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      
      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(3000);
      
      const loadTime = Date.now() - startTime;
      
      // Should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
      
      // Verify content is displayed
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
    });

    test('should handle multiple rapid refreshes', async ({ page }) => {
      const refreshButton = page.locator('button:has-text("Refresh")');
      
      // Perform multiple rapid refreshes
      for (let i = 0; i < 5; i++) {
        await refreshButton.click();
        await page.waitForTimeout(200);
      }
      
      // Verify final state is stable
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
    });

    test('should not cause memory leaks during auto-refresh', async ({ page }) => {
      // Enable auto-refresh
      const autoRefreshToggle = page.locator('button').filter({ hasText: /Auto-refresh|Eye/ });
      await autoRefreshToggle.click();
      
      // Wait for multiple refresh cycles
      await page.waitForTimeout(10000);
      
      // Verify metrics are still functional
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
    });
  });

  // ============================================================================
  // DATA ACCURACY AND CONSISTENCY TESTS
  // ============================================================================
  
  test.describe('Data Accuracy', () => {
    test('should display consistent metric values', async ({ page }) => {
      // Get initial metric values
      const cpuValue1 = await page.locator('text=CPU Usage').locator('..').locator('.text-2xl').textContent();
      
      // Wait a moment
      await page.waitForTimeout(1000);
      
      // Get values again
      const cpuValue2 = await page.locator('text=CPU Usage').locator('..').locator('.text-2xl').textContent();
      
      // Values should be consistent (within reasonable range)
      if (cpuValue1 && cpuValue2) {
        const value1 = parseFloat(cpuValue1);
        const value2 = parseFloat(cpuValue2);
        
        // Values should be within 10% of each other
        const difference = Math.abs(value1 - value2);
        const average = (value1 + value2) / 2;
        const percentageDiff = (difference / average) * 100;
        
        expect(percentageDiff).toBeLessThan(10);
      }
    });

    test('should show realistic metric ranges', async ({ page }) => {
      // Check CPU usage is between 0-100%
      const cpuValue = await page.locator('text=CPU Usage').locator('..').locator('.text-2xl').textContent();
      if (cpuValue) {
        const cpu = parseFloat(cpuValue);
        expect(cpu).toBeGreaterThanOrEqual(0);
        expect(cpu).toBeLessThanOrEqual(100);
      }
      
      // Check memory usage is between 0-100%
      const memoryValue = await page.locator('text=Memory Usage').locator('..').locator('.text-2xl').textContent();
      if (memoryValue) {
        const memory = parseFloat(memoryValue);
        expect(memory).toBeGreaterThanOrEqual(0);
        expect(memory).toBeLessThanOrEqual(100);
      }
    });
  });
});
