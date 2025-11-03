import { test, expect } from '@playwright/test';

test.describe('Simple Metrics API Test', () => {
  test('should verify API endpoints are working', async ({ page }) => {
    // Test that backend API endpoints are accessible
    const apiEndpoints = [
      'http://localhost:8443/api/v1/metrics/dashboard',
      'http://localhost:8443/api/v1/metrics/performance',
      'http://localhost:8443/api/v1/metrics/algorithms',
      'http://localhost:8443/api/v1/health/detailed'
    ];
    
    for (const endpoint of apiEndpoints) {
      const response = await page.request.get(endpoint);
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data).toBeDefined();
    }
  });

  test('should verify frontend is accessible', async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:8449');
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle');
    
    // Check that the main page loads
    await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
    
    // Check that the metrics navigation button exists
    await expect(page.locator('[data-testid="metrics-nav-button"]')).toBeVisible();
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

  test('should verify health endpoint works', async ({ page }) => {
    const response = await page.request.get('http://localhost:8443/api/v1/health/detailed');
    const data = await response.json();
    
    expect(response.status()).toBe(200);
    expect(data).toHaveProperty('status');
    expect(data).toHaveProperty('timestamp');
    expect(data).toHaveProperty('performance_metrics');
  });
});

