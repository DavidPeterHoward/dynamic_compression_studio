import { test, expect } from '@playwright/test';

test.describe('Metrics Critical Path E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:8449');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
  });

  test('should load system metrics page without network errors', async ({ page }) => {
    // Click on the System Metrics tab
    await page.click('[data-testid="metrics-nav-button"]');
    
    // Wait for the metrics page to load
    await page.waitForSelector('h2:has-text("System Metrics & Analytics")', { timeout: 10000 });
    
    // Check that no network errors occurred
    const networkErrors = [];
    page.on('response', response => {
      if (response.status() >= 400) {
        networkErrors.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        });
      }
    });
    
    // Wait for metrics to load (should not have network errors)
    await page.waitForTimeout(5000);
    
    // Verify no critical network errors
    const criticalErrors = networkErrors.filter(error => 
      error.url.includes('metrics') || error.url.includes('health')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('should display real-time metrics data', async ({ page }) => {
    // Navigate to metrics page
    await page.click('[data-testid="metrics-nav-button"]');
    await page.waitForSelector('h2:has-text("System Metrics & Analytics")');
    
    // Check for system health overview
    await expect(page.locator('text=System Health Overview')).toBeVisible();
    
    // Check for metric cards
    await expect(page.locator('text=CPU Usage')).toBeVisible();
    await expect(page.locator('text=Memory Usage')).toBeVisible();
    await expect(page.locator('text=Disk Usage')).toBeVisible();
    await expect(page.locator('text=Network Usage')).toBeVisible();
    
    // Check for compression metrics
    await expect(page.locator('text=Compression Efficiency')).toBeVisible();
    await expect(page.locator('text=Throughput')).toBeVisible();
    await expect(page.locator('text=Success Rate')).toBeVisible();
    await expect(page.locator('text=Response Time')).toBeVisible();
  });

  test('should have working auto-refresh functionality', async ({ page }) => {
    // Navigate to metrics page
    await page.click('[data-testid="metrics-nav-button"]');
    await page.waitForSelector('h2:has-text("System Metrics & Analytics")');
    
    // Check that auto-refresh is enabled by default
    const autoRefreshButton = page.locator('button:has-text("Auto-refresh")').first();
    await expect(autoRefreshButton).toBeVisible();
    
    // Test refresh button
    const refreshButton = page.locator('button:has-text("Refresh")');
    await expect(refreshButton).toBeVisible();
    
    // Click refresh and verify it works
    await refreshButton.click();
    await page.waitForTimeout(2000);
    
    // Verify metrics are still displayed after refresh
    await expect(page.locator('text=System Health Overview')).toBeVisible();
  });

  test('should display algorithm performance data', async ({ page }) => {
    // Navigate to metrics page
    await page.click('[data-testid="metrics-nav-button"]');
    await page.waitForSelector('h2:has-text("System Metrics & Analytics")');
    
    // Check for algorithm performance section
    await expect(page.locator('text=Algorithm Performance')).toBeVisible();
    
    // Check for system resources section
    await expect(page.locator('text=System Resources')).toBeVisible();
    
    // Check for compression analytics
    await expect(page.locator('text=Compression Analytics')).toBeVisible();
  });

  test('should handle time range selection', async ({ page }) => {
    // Navigate to metrics page
    await page.click('[data-testid="metrics-nav-button"]');
    await page.waitForSelector('h2:has-text("System Metrics & Analytics")');
    
    // Check for time range buttons
    const timeRangeButtons = ['1h', '6h', '24h', '7d', '30d'];
    
    for (const range of timeRangeButtons) {
      const button = page.locator(`button:has-text("${range}")`);
      await expect(button).toBeVisible();
    }
    
    // Test clicking different time ranges
    await page.click('button:has-text("6h")');
    await page.waitForTimeout(1000);
    
    await page.click('button:has-text("24h")');
    await page.waitForTimeout(1000);
    
    // Verify metrics are still displayed
    await expect(page.locator('text=System Health Overview')).toBeVisible();
  });

  test('should display detailed system information', async ({ page }) => {
    // Navigate to metrics page
    await page.click('[data-testid="metrics-nav-button"]');
    await page.waitForSelector('h2:has-text("System Metrics & Analytics")');
    
    // Check for system health indicators
    await expect(page.locator('text=Active Connections')).toBeVisible();
    await expect(page.locator('text=Queue Length')).toBeVisible();
    await expect(page.locator('text=Uptime')).toBeVisible();
    await expect(page.locator('text=Processes')).toBeVisible();
    
    // Check for detailed metrics
    await expect(page.locator('text=CPU Temperature')).toBeVisible();
    await expect(page.locator('text=Power Consumption')).toBeVisible();
    await expect(page.locator('text=Network Latency')).toBeVisible();
  });

  test('should show content type and algorithm usage distribution', async ({ page }) => {
    // Navigate to metrics page
    await page.click('[data-testid="metrics-nav-button"]');
    await page.waitForSelector('h2:has-text("System Metrics & Analytics")');
    
    // Check for distribution charts
    await expect(page.locator('text=Content Type Distribution')).toBeVisible();
    await expect(page.locator('text=Algorithm Usage')).toBeVisible();
    await expect(page.locator('text=Error Distribution')).toBeVisible();
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Navigate to metrics page
    await page.click('[data-testid="metrics-nav-button"]');
    await page.waitForSelector('h2:has-text("System Metrics & Analytics")');
    
    // Check for error handling - should not show error messages for normal operation
    const errorMessages = page.locator('text=Failed to load metrics');
    await expect(errorMessages).toHaveCount(0);
    
    // Check for loading states
    const loadingSpinner = page.locator('.animate-spin');
    if (await loadingSpinner.count() > 0) {
      // If loading spinner is present, wait for it to disappear
      await expect(loadingSpinner).not.toBeVisible({ timeout: 10000 });
    }
  });

  test('should verify API endpoints are accessible', async ({ page }) => {
    // Test that backend API endpoints are accessible
    const apiEndpoints = [
      'http://localhost:8443/api/v1/metrics/dashboard',
      'http://localhost:8443/api/v1/metrics/performance',
      'http://localhost:8443/api/v1/metrics/algorithms',
      'http://localhost:8443/api/health/detailed'
    ];
    
    for (const endpoint of apiEndpoints) {
      const response = await page.request.get(endpoint);
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data).toBeDefined();
    }
  });

  test('should verify metrics data structure', async ({ page }) => {
    // Test the dashboard metrics endpoint
    const response = await page.request.get('http://localhost:8443/api/v1/metrics/dashboard');
    const data = await response.json();
    
    // Verify expected structure
    expect(data).toHaveProperty('overview');
    expect(data).toHaveProperty('performance');
    expect(data).toHaveProperty('top_algorithms');
    expect(data).toHaveProperty('recent_activity');
    
    // Verify overview structure
    expect(data.overview).toHaveProperty('total_compressions_today');
    expect(data.overview).toHaveProperty('average_compression_ratio');
    expect(data.overview).toHaveProperty('success_rate');
    
    // Verify performance structure
    expect(data.performance).toHaveProperty('cpu_usage');
    expect(data.performance).toHaveProperty('memory_usage');
    expect(data.performance).toHaveProperty('disk_usage');
  });

  test('should test metrics page navigation and functionality', async ({ page }) => {
    // Start from home page
    await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
    
    // Navigate to metrics
    await page.click('[data-testid="metrics-nav-button"]');
    
    // Verify we're on the metrics page
    await expect(page.locator('h2:has-text("System Metrics & Analytics")')).toBeVisible();
    
    // Test refresh functionality
    const refreshButton = page.locator('button:has-text("Refresh")');
    await refreshButton.click();
    
    // Wait for refresh to complete
    await page.waitForTimeout(3000);
    
    // Verify metrics are still displayed
    await expect(page.locator('text=System Health Overview')).toBeVisible();
    
    // Test auto-refresh toggle
    const autoRefreshToggle = page.locator('button:has-text("Auto-refresh")').first();
    await autoRefreshToggle.click();
    
    // Verify toggle worked (button state should change)
    await page.waitForTimeout(1000);
  });
});

