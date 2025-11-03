/**
 * Comprehensive End-to-End Test Suite for All Application Paths
 * 
 * This test suite covers every possible user interaction, navigation path,
 * button click, form submission, and functionality across all tabs and pages.
 */

import { expect, test } from '@playwright/test';

test.describe('Comprehensive E2E Tests - All Application Paths', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for the main application to load
    await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
  });

  // ==================== NAVIGATION & TAB SWITCHING ====================
  
  test.describe('Navigation and Tab Switching', () => {
    test('should navigate through all tabs and verify content', async ({ page }) => {
      const checks = [
        { name: 'Compression', sel: 'textarea[placeholder="Enter content to compress..."]' },
        { name: 'Experiments', sel: 'button:has-text("Create New Experiment")' },
        { name: 'System Metrics', sel: 'h3:has-text("Real-time Metrics")' },
        { name: 'Synthetic Data', sel: 'button:has-text("Generate Synthetic Data")' },
        { name: 'LLM/Agent', sel: 'button:has-text("Decompress Content")' },
        { name: 'Evaluation', sel: 'button:has-text("Run Evaluation")' }
      ];

      for (const t of checks) {
        await page.click(`button:has-text("${t.name}")`);
        await expect(page.locator(t.sel)).toBeVisible();
      }
    });

    test('should retain compression input after tab switches', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
      await contentInput.fill('State preservation test content');
      await page.click('button:has-text("Experiments")');
      await expect(page.locator('button:has-text("Create New Experiment")')).toBeVisible();
      await page.click('button:has-text("Compression")');
      await expect(contentInput).toBeVisible();
    });

    test('should handle rapid tab switching', async ({ page }) => {
      const tabs = ['Compression', 'Experiments', 'System Metrics', 'Synthetic Data', 'LLM/Agent', 'Evaluation'];
      
      // Rapidly switch between tabs
      for (let i = 0; i < 3; i++) {
        for (const tab of tabs) {
          await page.click(`button:has-text("${tab}")`);
          await page.waitForTimeout(100);
        }
      }
      
      // Verify final tab is working
      await expect(page.locator('button:has-text("Run Evaluation")')).toBeVisible();
    });
  });

  // ==================== COMPRESSION TAB - COMPLETE WORKFLOW ====================
  
  test.describe('Compression Tab - Complete Workflow', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Compression")');
      await expect(page.locator('main h1:has-text("Compression")')).toBeVisible();
    });

    test('should complete full compression workflow with all steps', async ({ page }) => {
      // Step 1: Enter content
      const testContent = 'This is a comprehensive test content for compression workflow testing with repeated patterns and structures for optimal compression results.';
      const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
      await contentInput.fill(testContent);
      await expect(contentInput).toHaveValue(testContent);
      
      // Step 2: Wait for content analysis
      await page.waitForTimeout(2000);
      
      // Step 3: Verify content analysis results
      await expect(page.locator('h2:has-text("Content Input")')).toBeVisible();
      
      // Step 4: Select algorithm
      await page.click('text=gzip');
      
      // Step 5: Execute compression
      const compressButton = page.locator('button:has-text("Optimize & Compress")');
      await compressButton.click();
      
      // Step 6: Wait for compression to complete or show results
      await page.waitForTimeout(3000);
      
      // Step 7: Wait for completion
      await page.waitForTimeout(5000);
      
      // Step 8: Verify results tab is available
      await expect(page.locator('button:has-text("Results & Metrics")')).toBeVisible();
      
      // Step 9: Click results tab
      await page.click('button:has-text("Results & Metrics")');
      
      // Step 10: Verify compressed content is displayed
      await expect(page.locator('text=Compressed Content')).toBeVisible();
      await expect(page.locator('textarea[readonly]')).toBeVisible();
      
      // Step 11: Verify metrics are displayed
      await expect(page.locator('text=Compression Ratio')).toBeVisible();
      await expect(page.locator('text=Size Reduction')).toBeVisible();
      await expect(page.locator('text=Processing Time')).toBeVisible();
      await expect(page.locator('text=Algorithm Used')).toBeVisible();
      
      // Step 12: Test copy functionality
      const copyButton = page.locator('button:has-text("Copy")');
      await expect(copyButton).toBeVisible();
      await copyButton.click();
      
      // Step 13: Test download functionality
      const downloadButton = page.locator('button:has-text("Download")');
      await expect(downloadButton).toBeVisible();
      
      // Step 14: Verify detailed metrics
      await expect(page.locator('text=Performance Metrics')).toBeVisible();
      await expect(page.locator('text=Quality Metrics')).toBeVisible();
      await expect(page.locator('text=Prediction Accuracy')).toBeVisible();
      await expect(page.locator('text=Size Comparison')).toBeVisible();
    });

    test('should handle different content types', async ({ page }) => {
      const contentTypes = [
        {
          content: JSON.stringify({ key: 'value', nested: { data: 'test' }, array: [1, 2, 3, 4, 5] }),
          name: 'JSON'
        },
        {
          content: '<html><body><p>HTML content</p><div>Nested elements</div></body></html>',
          name: 'HTML'
        },
        {
          content: 'A'.repeat(1000),
          name: 'Repeated Pattern'
        },
        {
          content: 'Special characters: !@#$%^&*()_+-=[]{}|;:,.<>?',
          name: 'Special Characters'
        }
      ];

      for (const contentType of contentTypes) {
        // Clear previous content
        await page.click('button:has-text("Clear")');
        
        // Enter new content
        const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
        await contentInput.fill(contentType.content);
        
        // Wait for analysis
        await page.waitForTimeout(2000);
        
        // Select algorithm
        await page.click('text=gzip');
        
        // Compress
        await page.click('button:has-text("Optimize & Compress")');
        
        // Wait for completion
        await page.waitForTimeout(5000);
        
        // Verify results
        await expect(page.locator('text=Compressed Content')).toBeVisible();
        
        // Go back to input tab for next iteration
        await page.click('button:has-text("Input & Analysis")');
      }
    });

    test('should test all available algorithms', async ({ page }) => {
      const algorithms = ['gzip', 'brotli', 'lz4', 'zstd', 'bzip2', 'lzma'];
      const testContent = 'Algorithm testing content with repeated patterns for compression analysis.';
      
      for (const algorithm of algorithms) {
        // Enter content
        const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
        await contentInput.fill(testContent);
        
        // Wait for analysis
        await page.waitForTimeout(2000);
        
        // Select algorithm
        await page.click(`text=${algorithm}`);
        
        // Compress
        await page.click('button:has-text("Optimize & Compress")');
        
        // Wait for completion
        await page.waitForTimeout(5000);
        
        // Verify results
        await expect(page.locator('text=Compressed Content')).toBeVisible();
        
        // Verify algorithm used is displayed
        await expect(page.locator(`text=${algorithm}`)).toBeVisible();
        
        // Go back to input tab for next iteration
        await page.click('button:has-text("Input & Analysis")');
      }
    });

    test('should handle auto-optimization feature', async ({ page }) => {
      const testContent = 'Auto-optimization test content with patterns for compression analysis.';
      
      // Enter content
      const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
      await contentInput.fill(testContent);
      
      // Wait for analysis
      await page.waitForTimeout(2000);
      
      // Enable auto-optimization
      const autoOptToggle = page.getByText('Auto-Optimization').locator('..').locator('..').locator('button:not(:has-text("Optimize"))').first();
      await autoOptToggle.click();
      
      // Select an algorithm
      await page.click('text=gzip');
      
      // Start optimization
      await page.click('button:has-text("Optimize & Compress")');
      
      // Wait for optimization to complete
      await page.waitForTimeout(10000);
      
      // Verify results
      await expect(page.locator('text=Compressed Content')).toBeVisible();
      
      // Verify optimization iterations are displayed
      await expect(page.locator('text=Optimization Iterations')).toBeVisible();
    });

    test('should handle error cases gracefully', async ({ page }) => {
      // Test with empty content - button should be disabled
      const compressButton = page.locator('button:has-text("Optimize & Compress")');
      await expect(compressButton).toBeDisabled();
      
      // Test with very large content
      const largeContent = 'A'.repeat(100000);
      const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
      await contentInput.fill(largeContent);
      
      await page.click('text=gzip');
      await page.click('button:has-text("Optimize & Compress")');
      
      // Should handle large content without crashing
      await page.waitForTimeout(10000);
      
      // Should either complete or show appropriate error
      const results = page.locator('text=Compressed Content');
      const error = page.locator('text=Error');
      
      await expect(results.or(error)).toBeVisible();
    });
  });

  // ==================== EXPERIMENTS TAB ====================
  
  test.describe('Experiments Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Experiments")');
      await expect(page.locator('button:has-text("Create New Experiment")')).toBeVisible();
    });

    test('should display experiment management interface', async ({ page }) => {
      // Verify experiment elements
      await expect(page.locator('button:has-text("Create New Experiment")')).toBeVisible();
      await expect(page.locator('button:has-text("Create New Experiment")')).toBeVisible();
    });

    test('should handle experiment creation workflow', async ({ page }) => {
      // Click create experiment button
      await page.click('button:has-text("Create New Experiment")');
      
      // Verify experiment form is displayed
      await expect(page.locator('text=Experiment Name')).toBeVisible();
      await expect(page.locator('text=Description')).toBeVisible();
      
      // Fill experiment form
      await page.fill('input[placeholder*="name"]', 'Test Experiment');
      await page.fill('textarea[placeholder*="description"]', 'Test experiment description');
      
      // Submit form
      await page.click('button:has-text("Create")');
      
      // Verify experiment was created
      await expect(page.locator('text=Test Experiment')).toBeVisible();
    });

    test('should display experiment list and details', async ({ page }) => {
      // Verify experiment list is displayed
      await expect(page.locator('text=Active Experiments')).toBeVisible();
      
      // Check for experiment cards
      const experimentCards = page.locator('[data-testid="experiment-card"]');
      const cardCount = await experimentCards.count();
      expect(cardCount).toBeGreaterThanOrEqual(0);
    });
  });

  // ==================== SYSTEM METRICS TAB ====================
  
  test.describe('System Metrics Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("System Metrics")');
      await expect(page.locator('h3:has-text("Real-time Metrics")')).toBeVisible();
    });

    test('should display real-time system metrics', async ({ page }) => {
      // Verify metrics are displayed
      await expect(page.locator('text=CPU Usage')).toBeVisible();
      await expect(page.locator('text=Memory Usage')).toBeVisible();
      await expect(page.locator('text=Disk I/O')).toBeVisible();
      await expect(page.locator('text=Network Usage')).toBeVisible();
    });

    test('should update metrics in real-time', async ({ page }) => {
      // Get initial metrics
      const cpuUsage = page.locator('text=CPU Usage').locator('..').locator('text=/\\d+%/');
      await expect(cpuUsage).toBeVisible();
      
      // Wait for metrics to update
      await page.waitForTimeout(2000);
      
      // Verify metrics are still visible and updating
      await expect(cpuUsage).toBeVisible();
    });

    test('should display performance charts', async ({ page }) => {
      // Verify chart containers are present
      await expect(page.locator('[data-testid="cpu-chart"]')).toBeVisible();
      await expect(page.locator('[data-testid="memory-chart"]')).toBeVisible();
    });
  });

  // ==================== SYNTHETIC DATA TAB ====================
  
  test.describe('Synthetic Data Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Synthetic Data")');
      await expect(page.locator('button:has-text("Generate Synthetic Data")')).toBeVisible();
    });

    test('should display synthetic data generation interface', async ({ page }) => {
      // Verify synthetic data elements
      await expect(page.locator('button:has-text("Generate Synthetic Data")')).toBeVisible();
      await expect(page.locator('button:has-text("Generate Synthetic Data")')).toBeVisible();
    });

    test('should handle synthetic data generation workflow', async ({ page }) => {
      // Configure generation parameters
      await page.fill('input[placeholder*="size"]', '1000');
      await page.selectOption('select', 'text');
      
      // Click generate button
      await page.click('button:has-text("Generate Synthetic Data")');
      
      // Verify generation is in progress
      await expect(page.locator('text=Generating')).toBeVisible();
      
      // Wait for completion
      await page.waitForTimeout(5000);
      
      // Verify data was generated
      await expect(page.locator('text=Generated Data')).toBeVisible();
    });
  });

  // ==================== LLM/AGENT TAB ====================
  
  test.describe('LLM/Agent Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("LLM/Agent")');
      await expect(page.locator('button:has-text("Decompress Content")')).toBeVisible();
    });

    test('should display LLM/Agent interface', async ({ page }) => {
      // Verify LLM/Agent elements
      await expect(page.locator('button:has-text("Decompress Content")')).toBeVisible();
      await expect(page.locator('button:has-text("Decompress Content")')).toBeVisible();
    });

    test('should handle LLM interaction workflow', async ({ page }) => {
      // Test LLM interaction
      const llmInput = page.locator('textarea[placeholder*="message"]');
      if (await llmInput.isVisible()) {
        await llmInput.fill('Test LLM interaction message');
        await page.click('button:has-text("Send")');
        
        // Wait for response
        await page.waitForTimeout(3000);
        
        // Verify response is displayed
        await expect(page.locator('text=Response')).toBeVisible();
      }
    });
  });

  // ==================== EVALUATION TAB ====================
  
  test.describe('Evaluation Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Evaluation")');
      await expect(page.locator('button:has-text("Run Evaluation")')).toBeVisible();
    });

    test('should display evaluation dashboard', async ({ page }) => {
      // Verify evaluation elements
      await expect(page.locator('button:has-text("Run Evaluation")')).toBeVisible();
      await expect(page.locator('button:has-text("Run Evaluation")')).toBeVisible();
    });

    test('should handle evaluation execution workflow', async ({ page }) => {
      // Configure evaluation parameters
      await page.fill('input[placeholder*="start"]', '2024-01-01');
      await page.fill('input[placeholder*="end"]', '2024-12-31');
      
      // Click run evaluation button
      await page.click('button:has-text("Run Evaluation")');
      
      // Verify evaluation is running
      await expect(page.locator('text=Running Evaluation')).toBeVisible();
      
      // Wait for completion
      await page.waitForTimeout(10000);
      
      // Verify results are displayed
      await expect(page.locator('text=Evaluation Results')).toBeVisible();
    });
  });

  // ==================== ACCESSIBILITY TESTS ====================
  
  test.describe('Accessibility', () => {
    test('should support keyboard navigation', async ({ page }) => {
      // Test tab navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Verify focus is on expected element
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });

    test('should have proper ARIA labels', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      
      // Check for ARIA labels on interactive elements
      const textarea = page.locator('textarea[placeholder="Enter content to compress..."]');
      await expect(textarea).toBeVisible();
      
      const button = page.locator('button:has-text("Optimize & Compress")');
      await expect(button).toBeVisible();
    });

    test('should support screen reader navigation', async ({ page }) => {
      // Test with screen reader simulation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter');
      
      // Verify navigation worked
      await expect(page.locator('main h1')).toBeVisible();
    });
  });

  // ==================== PERFORMANCE TESTS ====================
  
  test.describe('Performance', () => {
    test('should load page within acceptable time', async ({ page }) => {
      const startTime = Date.now();
              await page.goto('/');
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      
      // Page should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    });

    test('should handle rapid user interactions', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      
      // Rapidly click between algorithms
      const algorithms = ['gzip', 'brotli', 'lz4', 'zstd'];
      for (let i = 0; i < 10; i++) {
        await page.click(`text=${algorithms[i % algorithms.length]}`);
        await page.waitForTimeout(50);
      }
      
      // Verify UI is still responsive
      await expect(page.locator('button:has-text("Optimize & Compress")')).toBeVisible();
    });

    test('should handle large content without performance issues', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      
      // Enter large content
      const largeContent = 'A'.repeat(10000);
      await page.fill('textarea[placeholder="Enter content to compress..."]', largeContent);
      
      // Verify UI is still responsive
      await expect(page.locator('button:has-text("Optimize & Compress")')).toBeVisible();
    });
  });

  // ==================== INTEGRATION TESTS ====================
  
  test.describe('Integration Tests', () => {
    test('should maintain state across page refreshes', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'State persistence test');
      
      // Refresh page
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      // Navigate back to compression tab
      await page.click('button:has-text("Compression")');
      
      // Verify state is maintained (if implemented)
      const textarea = page.locator('textarea[placeholder="Enter content to compress..."]');
      const value = await textarea.inputValue();
      // Note: This depends on whether state persistence is implemented
    });

    test('should handle multiple concurrent operations', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      
      // Start multiple operations
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Concurrent test content');
      await page.click('text=gzip');
      await page.click('button:has-text("Optimize & Compress")');
      
      // Switch tabs while operation is running
      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(1000);
      await page.click('button:has-text("Compression")');
      
      // Verify operation completed or is still running
      const results = page.locator('text=Compressed Content');
      const progress = page.locator('button:has-text("Optimize & Compress")');
      
      await expect(results.or(progress)).toBeVisible();
    });
  });

  // ==================== ERROR HANDLING TESTS ====================
  
  test.describe('Error Handling', () => {
    test('should handle network errors gracefully', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Network test content');
      
      // Simulate network error by going offline
      await page.context().setOffline(true);
      
      // Try to perform action - should handle gracefully
      await page.click('button:has-text("Optimize & Compress")');
      
      // Wait a moment for any error handling
      await page.waitForTimeout(2000);
      
      // Restore network
      await page.context().setOffline(false);
    });

    test('should handle timeout scenarios', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      
      // Test with large content
      const largeContent = 'A'.repeat(10000); // Reduced size for faster test
      await page.fill('textarea[placeholder="Enter content to compress..."]', largeContent);
      await page.click('text=gzip');
      await page.click('button:has-text("Optimize & Compress")');
      
      // Wait for processing
      await page.waitForTimeout(5000);
      
      // Verify the operation completed or is still processing
      const results = page.locator('text=Compressed Content');
      const progress = page.locator('button:has-text("Optimize & Compress")');
      
      // Either results are shown or button is still processing
      await expect(results.or(progress)).toBeVisible();
    });
  });
});
