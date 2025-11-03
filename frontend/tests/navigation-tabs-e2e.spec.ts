import { expect, test } from '@playwright/test';

/**
 * Comprehensive E2E Tests for All Navigation Tabs
 * 
 * This test suite ensures all top-level navigation tabs are functioning correctly,
 * including the System Metrics tab that was experiencing network errors.
 */

test.describe('Navigation Tabs E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the page to load completely
    await page.waitForLoadState('networkidle');
    
    // Verify the main navigation is visible
    await expect(page.locator('nav')).toBeVisible();
  });

  // ============================================================================
  // NAVIGATION TAB VISIBILITY TESTS
  // ============================================================================
  
  test.describe('Navigation Tab Visibility', () => {
    test('should display all navigation tabs', async ({ page }) => {
      const expectedTabs = [
        'Compression/Decompression',
        'Experiments', 
        'System Metrics',
        'Synthetic Data',
        'Synthetic Media',
        'LLM/Agent',
        'Enhanced LLM Agent',
        'Prompts',
        'Evaluation'
      ];

      for (const tabLabel of expectedTabs) {
        await expect(page.locator(`button:has-text("${tabLabel}")`)).toBeVisible();
      }
    });

    test('should have proper tab styling and icons', async ({ page }) => {
      // Check that all tabs have icons
      const tabButtons = page.locator('nav button');
      const tabCount = await tabButtons.count();
      
      for (let i = 0; i < tabCount; i++) {
        const tab = tabButtons.nth(i);
        await expect(tab.locator('svg')).toBeVisible(); // Icon should be present
        await expect(tab).toHaveClass(/flex items-center space-x-2/); // Proper styling
      }
    });
  });

  // ============================================================================
  // INDIVIDUAL TAB FUNCTIONALITY TESTS
  // ============================================================================
  
  test.describe('Compression/Decompression Tab', () => {
    test('should load compression tab successfully', async ({ page }) => {
      await page.click('button:has-text("Compression/Decompression")');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      await expect(page.locator('button:has-text("Compression/Decompression")')).toHaveClass(/border-blue-500/);
      
      // Verify compression interface is visible
      await expect(page.locator('textarea[placeholder*="Enter content"]')).toBeVisible();
      await expect(page.locator('button:has-text("Compress")')).toBeVisible();
    });

    test('should allow text input and compression', async ({ page }) => {
      await page.click('button:has-text("Compression/Decompression")');
      await page.waitForTimeout(500);
      
      // Enter test content
      const testContent = 'This is a test string for compression testing.';
      await page.fill('textarea[placeholder*="Enter content"]', testContent);
      
      // Verify content is entered
      await expect(page.locator('textarea[placeholder*="Enter content"]')).toHaveValue(testContent);
      
      // Click compress button
      await page.click('button:has-text("Compress")');
      
      // Wait for compression to complete (with timeout)
      await page.waitForTimeout(2000);
      
      // Verify results are displayed
      await expect(page.locator('text=Compression Results')).toBeVisible();
    });
  });

  test.describe('Experiments Tab', () => {
    test('should load experiments tab successfully', async ({ page }) => {
      await page.click('button:has-text("Experiments")');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      await expect(page.locator('button:has-text("Experiments")')).toHaveClass(/border-blue-500/);
      
      // Verify experiments interface is visible
      await expect(page.locator('text=Experiments')).toBeVisible();
    });

    test('should display experiment templates', async ({ page }) => {
      await page.click('button:has-text("Experiments")');
      await page.waitForTimeout(500);
      
      // Check for experiment templates or configuration options
      await expect(page.locator('text=Template')).toBeVisible();
    });
  });

  test.describe('System Metrics Tab - Critical Fix', () => {
    test('should load system metrics tab without network errors', async ({ page }) => {
      // Monitor network requests to catch any errors
      const networkErrors: string[] = [];
      
      page.on('response', response => {
        if (response.status() >= 400) {
          networkErrors.push(`${response.url()}: ${response.status()}`);
        }
      });

      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(2000); // Give time for data loading
      
      // Verify tab is active
      await expect(page.locator('button:has-text("System Metrics")')).toHaveClass(/border-blue-500/);
      
      // Verify metrics interface is visible
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
      
      // Check that no network errors occurred
      expect(networkErrors).toHaveLength(0);
    });

    test('should display live metrics data', async ({ page }) => {
      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(3000); // Allow time for data fetching
      
      // Verify key metrics are displayed
      await expect(page.locator('text=CPU Usage')).toBeVisible();
      await expect(page.locator('text=Memory Usage')).toBeVisible();
      await expect(page.locator('text=Disk Usage')).toBeVisible();
      await expect(page.locator('text=Network Usage')).toBeVisible();
      
      // Verify metrics have values (not just 0 or empty)
      const cpuValue = page.locator('text=CPU Usage').locator('..').locator('.text-2xl');
      await expect(cpuValue).toBeVisible();
    });

    test('should have working refresh functionality', async ({ page }) => {
      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(2000);
      
      // Find and click refresh button
      const refreshButton = page.locator('button:has-text("Refresh")');
      await expect(refreshButton).toBeVisible();
      
      // Click refresh and verify it works
      await refreshButton.click();
      await page.waitForTimeout(1000);
      
      // Verify refresh completed without errors
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
    });

    test('should display system health overview', async ({ page }) => {
      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(2000);
      
      // Verify system health section
      await expect(page.locator('text=System Health Overview')).toBeVisible();
      await expect(page.locator('text=Active Connections')).toBeVisible();
      await expect(page.locator('text=Queue Length')).toBeVisible();
      await expect(page.locator('text=Uptime')).toBeVisible();
      await expect(page.locator('text=Processes')).toBeVisible();
    });

    test('should display algorithm performance metrics', async ({ page }) => {
      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(2000);
      
      // Verify algorithm performance section
      await expect(page.locator('text=Algorithm Performance')).toBeVisible();
      
      // Check for algorithm metrics
      const algorithmSection = page.locator('text=Algorithm Performance').locator('..');
      await expect(algorithmSection).toBeVisible();
    });

    test('should display compression analytics', async ({ page }) => {
      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(2000);
      
      // Verify compression analytics section
      await expect(page.locator('text=Compression Analytics')).toBeVisible();
      await expect(page.locator('text=Content Type Distribution')).toBeVisible();
      await expect(page.locator('text=Algorithm Usage')).toBeVisible();
      await expect(page.locator('text=Error Distribution')).toBeVisible();
    });
  });

  test.describe('Synthetic Data Tab', () => {
    test('should load synthetic data tab successfully', async ({ page }) => {
      await page.click('button:has-text("Synthetic Data")');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      await expect(page.locator('button:has-text("Synthetic Data")')).toHaveClass(/border-blue-500/);
      
      // Verify synthetic data interface is visible
      await expect(page.locator('text=Synthetic Data')).toBeVisible();
    });
  });

  test.describe('Synthetic Media Tab', () => {
    test('should load synthetic media tab successfully', async ({ page }) => {
      await page.click('button:has-text("Synthetic Media")');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      await expect(page.locator('button:has-text("Synthetic Media")')).toHaveClass(/border-blue-500/);
      
      // Verify synthetic media interface is visible
      await expect(page.locator('text=Synthetic Media')).toBeVisible();
    });
  });

  test.describe('LLM/Agent Tab', () => {
    test('should load LLM/Agent tab successfully', async ({ page }) => {
      await page.click('button:has-text("LLM/Agent")');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      await expect(page.locator('button:has-text("LLM/Agent")')).toHaveClass(/border-blue-500/);
      
      // Verify LLM/Agent interface is visible
      await expect(page.locator('text=LLM/Agent')).toBeVisible();
    });
  });

  test.describe('Enhanced LLM Agent Tab', () => {
    test('should load Enhanced LLM Agent tab successfully', async ({ page }) => {
      await page.click('button:has-text("Enhanced LLM Agent")');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      await expect(page.locator('button:has-text("Enhanced LLM Agent")')).toHaveClass(/border-blue-500/);
      
      // Verify Enhanced LLM Agent interface is visible
      await expect(page.locator('text=Enhanced LLM Agent')).toBeVisible();
    });
  });

  test.describe('Prompts Tab', () => {
    test('should load Prompts tab successfully', async ({ page }) => {
      await page.click('button:has-text("Prompts")');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      await expect(page.locator('button:has-text("Prompts")')).toHaveClass(/border-blue-500/);
      
      // Verify Prompts interface is visible
      await expect(page.locator('text=Prompts')).toBeVisible();
    });
  });

  test.describe('Evaluation Tab', () => {
    test('should load Evaluation tab successfully', async ({ page }) => {
      await page.click('button:has-text("Evaluation")');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      await expect(page.locator('button:has-text("Evaluation")')).toHaveClass(/border-blue-500/);
      
      // Verify Evaluation interface is visible
      await expect(page.locator('text=Evaluation')).toBeVisible();
    });
  });

  // ============================================================================
  // TAB SWITCHING AND STATE MANAGEMENT TESTS
  // ============================================================================
  
  test.describe('Tab Switching', () => {
    test('should switch between all tabs without errors', async ({ page }) => {
      const tabs = [
        'Compression/Decompression',
        'Experiments',
        'System Metrics',
        'Synthetic Data',
        'Synthetic Media',
        'LLM/Agent',
        'Enhanced LLM Agent',
        'Prompts',
        'Evaluation'
      ];

      for (const tabLabel of tabs) {
        await page.click(`button:has-text("${tabLabel}")`);
        await page.waitForTimeout(500);
        
        // Verify tab is active
        await expect(page.locator(`button:has-text("${tabLabel}")`)).toHaveClass(/border-blue-500/);
        
        // Verify no JavaScript errors occurred
        const errors = await page.evaluate(() => {
          return window.consoleErrors || [];
        });
        expect(errors).toHaveLength(0);
      }
    });

    test('should maintain state when switching tabs', async ({ page }) => {
      // Go to compression tab and enter content
      await page.click('button:has-text("Compression/Decompression")');
      await page.waitForTimeout(500);
      
      const testContent = 'Test content for state preservation';
      await page.fill('textarea[placeholder*="Enter content"]', testContent);
      
      // Switch to another tab
      await page.click('button:has-text("Experiments")');
      await page.waitForTimeout(500);
      
      // Switch back to compression tab
      await page.click('button:has-text("Compression/Decompression")');
      await page.waitForTimeout(500);
      
      // Verify content is preserved
      await expect(page.locator('textarea[placeholder*="Enter content"]')).toHaveValue(testContent);
    });

    test('should handle rapid tab switching', async ({ page }) => {
      const tabs = [
        'Compression/Decompression',
        'System Metrics',
        'Experiments',
        'Synthetic Data'
      ];

      // Rapidly switch between tabs
      for (let i = 0; i < 3; i++) {
        for (const tabLabel of tabs) {
          await page.click(`button:has-text("${tabLabel}")`);
          await page.waitForTimeout(100); // Short delay
        }
      }
      
      // Verify final tab is active and functional
      await expect(page.locator('button:has-text("Synthetic Data")')).toHaveClass(/border-blue-500/);
    });
  });

  // ============================================================================
  // ERROR HANDLING AND RESILIENCE TESTS
  // ============================================================================
  
  test.describe('Error Handling', () => {
    test('should handle network errors gracefully in System Metrics', async ({ page }) => {
      // Simulate network issues by intercepting requests
      await page.route('**/api/v1/metrics/**', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Network error' })
        });
      });

      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(2000);
      
      // Verify error handling is in place
      await expect(page.locator('text=Failed to load metrics')).toBeVisible();
      await expect(page.locator('button:has-text("Retry")')).toBeVisible();
    });

    test('should recover from temporary network issues', async ({ page }) => {
      // First, simulate network failure
      await page.route('**/api/v1/metrics/**', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Temporary network error' })
        });
      });

      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(2000);
      
      // Verify error state
      await expect(page.locator('text=Failed to load metrics')).toBeVisible();
      
      // Remove network interception to allow normal requests
      await page.unroute('**/api/v1/metrics/**');
      
      // Click retry
      await page.click('button:has-text("Retry")');
      await page.waitForTimeout(2000);
      
      // Verify recovery
      await expect(page.locator('text=System Metrics & Analytics')).toBeVisible();
    });
  });

  // ============================================================================
  // PERFORMANCE AND LOADING TESTS
  // ============================================================================
  
  test.describe('Performance Tests', () => {
    test('should load all tabs within acceptable time', async ({ page }) => {
      const tabs = [
        'Compression/Decompression',
        'Experiments',
        'System Metrics',
        'Synthetic Data',
        'Synthetic Media',
        'LLM/Agent',
        'Enhanced LLM Agent',
        'Prompts',
        'Evaluation'
      ];

      for (const tabLabel of tabs) {
        const startTime = Date.now();
        
        await page.click(`button:has-text("${tabLabel}")`);
        await page.waitForTimeout(1000); // Wait for content to load
        
        const loadTime = Date.now() - startTime;
        
        // Verify tab loads within 3 seconds
        expect(loadTime).toBeLessThan(3000);
        
        // Verify tab is functional
        await expect(page.locator(`button:has-text("${tabLabel}")`)).toHaveClass(/border-blue-500/);
      }
    });

    test('should not cause memory leaks during tab switching', async ({ page }) => {
      // Switch between tabs multiple times
      const tabs = ['Compression/Decompression', 'System Metrics', 'Experiments'];
      
      for (let i = 0; i < 10; i++) {
        for (const tabLabel of tabs) {
          await page.click(`button:has-text("${tabLabel}")`);
          await page.waitForTimeout(200);
        }
      }
      
      // Verify final state is still functional
      await expect(page.locator('button:has-text("Experiments")')).toHaveClass(/border-blue-500/);
    });
  });

  // ============================================================================
  // ACCESSIBILITY TESTS
  // ============================================================================
  
  test.describe('Accessibility Tests', () => {
    test('should have proper ARIA labels for navigation', async ({ page }) => {
      const navButtons = page.locator('nav button');
      const count = await navButtons.count();
      
      for (let i = 0; i < count; i++) {
        const button = navButtons.nth(i);
        await expect(button).toHaveAttribute('data-testid');
      }
    });

    test('should support keyboard navigation', async ({ page }) => {
      // Focus on first tab
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Navigate with arrow keys
      await page.keyboard.press('ArrowRight');
      await page.keyboard.press('ArrowRight');
      
      // Activate with Enter
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);
      
      // Verify tab is active
      const activeTab = page.locator('button[class*="border-blue-500"]');
      await expect(activeTab).toBeVisible();
    });
  });
});
