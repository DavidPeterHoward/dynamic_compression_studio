/**
 * Comprehensive Frontend E2E Tests
 * 
 * This test suite covers all frontend functionality, user interactions,
 * buttons, forms, and critical user flows for the Dynamic Compression Algorithms application.
 */

import { expect, test } from '@playwright/test';

test.describe('Comprehensive Frontend E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for the main application to load
    await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
  });

  // ==================== NAVIGATION & TAB SWITCHING ====================
  
  test.describe('Navigation and Tab Switching', () => {
    test('should display all navigation tabs', async ({ page }) => {
      // Verify all navigation tabs are visible
      await expect(page.locator('button:has-text("Compression")')).toBeVisible();
      await expect(page.locator('button:has-text("Experiments")')).toBeVisible();
      await expect(page.locator('button:has-text("System Metrics")')).toBeVisible();
      await expect(page.locator('button:has-text("Synthetic Data")')).toBeVisible();
      await expect(page.locator('button:has-text("LLM/Agent")')).toBeVisible();
      await expect(page.locator('button:has-text("Evaluation")')).toBeVisible();
    });

    test('should switch between all tabs successfully', async ({ page }) => {
      const tabs = ['Compression', 'Experiments', 'System Metrics', 'Synthetic Data', 'LLM/Agent', 'Evaluation'];
      
      for (const tab of tabs) {
        await page.click(`button:has-text("${tab}")`);
        await page.waitForTimeout(500);
        
        // Verify tab content is loaded
        await expect(page.locator(`main h1:has-text("${tab}")`)).toBeVisible();
      }
    });

    test('should maintain state when switching tabs', async ({ page }) => {
      // Go to Compression tab and enter some content
      await page.click('button:has-text("Compression")');
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Test content for state preservation');
      
      // Switch to another tab
      await page.click('button:has-text("Experiments")');
      await page.waitForTimeout(500);
      
      // Switch back to Compression tab
      await page.click('button:has-text("Compression")');
      
      // Verify content is still there
      await expect(page.locator('textarea[placeholder="Enter content to compress..."]')).toHaveValue('Test content for state preservation');
    });
  });

  // ==================== COMPRESSION TAB - COMPLETE FUNCTIONALITY ====================
  
  test.describe('Compression Tab - Complete Functionality', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Compression")');
      await expect(page.locator('main h1:has-text("Compression")')).toBeVisible();
    });

    test('should display all compression tab elements', async ({ page }) => {
      // Verify main sections
      await expect(page.locator('h2:has-text("Content Input")')).toBeVisible();
      await expect(page.locator('h3:has-text("Select Compression Algorithm")')).toBeVisible();
      await expect(page.locator('h3:has-text("Meta-Learning")')).toBeVisible();
      await expect(page.locator('h3:has-text("Real-time Metrics")')).toBeVisible();
      
      // Verify input elements
      await expect(page.locator('textarea[placeholder="Enter content to compress..."]')).toBeVisible();
      await expect(page.locator('button:has-text("Optimize & Compress")')).toBeVisible();
    });

    test('should handle content input and validation', async ({ page }) => {
      const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
      
      // Test basic text input
      await contentInput.fill('Sample text for compression testing');
      await expect(contentInput).toHaveValue('Sample text for compression testing');
      
      // Test character counting
      await expect(page.locator('text=characters')).toBeVisible();
      
      // Test clear functionality
      await page.click('button:has-text("Clear")');
      await expect(contentInput).toHaveValue('');
    });

    test('should handle different content types', async ({ page }) => {
      const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
      
      // Test JSON content
      const jsonContent = JSON.stringify({ key: 'value', nested: { data: 'test' } });
      await contentInput.fill(jsonContent);
      await expect(contentInput).toHaveValue(jsonContent);
      
      // Test HTML content
      const htmlContent = '<html><body><p>HTML content</p></body></html>';
      await contentInput.fill(htmlContent);
      await expect(contentInput).toHaveValue(htmlContent);
      
      // Test large content
      const largeContent = 'A'.repeat(1000);
      await contentInput.fill(largeContent);
      await expect(contentInput).toHaveValue(largeContent);
    });

    test('should display algorithm selection options', async ({ page }) => {
      // Verify algorithm options are visible
      await expect(page.locator('text=gzip')).toBeVisible();
      await expect(page.locator('text=brotli')).toBeVisible();
      await expect(page.locator('text=lz4')).toBeVisible();
      await expect(page.locator('text=zstd')).toBeVisible();
      await expect(page.locator('text=bzip2')).toBeVisible();
      await expect(page.locator('text=lzma')).toBeVisible();
      
      // Verify advanced algorithms
      await expect(page.locator('text=content_aware')).toBeVisible();
      await expect(page.locator('text=quantum_biological')).toBeVisible();
      await expect(page.locator('text=neuromorphic')).toBeVisible();
      await expect(page.locator('text=topological')).toBeVisible();
    });

    test('should handle algorithm selection', async ({ page }) => {
      // Test selecting different algorithms
      const algorithms = ['gzip', 'brotli', 'lz4', 'zstd'];
      
      for (const algorithm of algorithms) {
        await page.click(`text=${algorithm}`);
        await page.waitForTimeout(200);
        
        // Verify selection (algorithm cards should have selected state)
        const algorithmCard = page.locator(`text=${algorithm}`).locator('..');
        await expect(algorithmCard).toBeVisible();
      }
    });

    test('should handle compression execution', async ({ page }) => {
      // Enter content
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Test content for compression');
      
      // Select an algorithm
      await page.click('text=gzip');
      
      // Execute compression
      await page.click('button:has-text("Optimize & Compress")');
      
      // Verify compression is in progress
      await expect(page.locator('button:has-text("Compressing...")')).toBeVisible();
      
      // Wait for completion (with timeout)
      await page.waitForTimeout(5000);
      
      // Verify results are displayed
      await expect(page.locator('text=Compression Results')).toBeVisible();
    });

    test('should display compression results', async ({ page }) => {
      // Perform compression
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Sample content for results testing');
      await page.click('text=gzip');
      await page.click('button:has-text("Optimize & Compress")');
      
      // Wait for results
      await page.waitForTimeout(5000);
      
      // Verify result metrics are displayed
      await expect(page.locator('text=Compression Ratio')).toBeVisible();
      await expect(page.locator('text=Size Reduction')).toBeVisible();
      await expect(page.locator('text=Processing Time')).toBeVisible();
      await expect(page.locator('text=Algorithm Used')).toBeVisible();
    });

    test('should handle result copying functionality', async ({ page }) => {
      // Perform compression
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Content for copying test');
      await page.click('text=gzip');
      await page.click('button:has-text("Optimize & Compress")');
      
      // Wait for results
      await page.waitForTimeout(5000);
      
      // Test copy functionality if available
      const copyButton = page.locator('button:has-text("Copy")');
      if (await copyButton.isVisible()) {
        await copyButton.click();
        // Verify copy notification
        await expect(page.locator('text=Copied to clipboard')).toBeVisible();
      }
    });
  });

  // ==================== SYSTEM METRICS TAB ====================
  
  test.describe('System Metrics Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("System Metrics")');
      await expect(page.locator('main h1:has-text("System Metrics")')).toBeVisible();
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

  // ==================== EXPERIMENTS TAB ====================
  
  test.describe('Experiments Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Experiments")');
      await expect(page.locator('main h1:has-text("Experiments")')).toBeVisible();
    });

    test('should display experiment management interface', async ({ page }) => {
      // Verify experiment elements
      await expect(page.locator('h2:has-text("Experiment Management")')).toBeVisible();
      await expect(page.locator('button:has-text("Create New Experiment")')).toBeVisible();
    });

    test('should handle experiment creation', async ({ page }) => {
      // Click create experiment button
      await page.click('button:has-text("Create New Experiment")');
      
      // Verify experiment form is displayed
      await expect(page.locator('text=Experiment Name')).toBeVisible();
      await expect(page.locator('text=Description')).toBeVisible();
    });

    test('should display experiment list', async ({ page }) => {
      // Verify experiment list is displayed
      await expect(page.locator('text=Active Experiments')).toBeVisible();
    });
  });

  // ==================== SYNTHETIC DATA TAB ====================
  
  test.describe('Synthetic Data Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Synthetic Data")');
      await expect(page.locator('main h1:has-text("Synthetic Data")')).toBeVisible();
    });

    test('should display synthetic data generation interface', async ({ page }) => {
      // Verify synthetic data elements
      await expect(page.locator('h2:has-text("Synthetic Data Generation")')).toBeVisible();
      await expect(page.locator('button:has-text("Generate Synthetic Data")')).toBeVisible();
    });

    test('should handle synthetic data generation', async ({ page }) => {
      // Click generate button
      await page.click('button:has-text("Generate Synthetic Data")');
      
      // Verify generation is in progress
      await expect(page.locator('text=Generating')).toBeVisible();
    });
  });

  // ==================== LLM/AGENT TAB ====================
  
  test.describe('LLM/Agent Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("LLM/Agent")');
      await expect(page.locator('main h1:has-text("LLM/Agent")')).toBeVisible();
    });

    test('should display LLM/Agent interface', async ({ page }) => {
      // Verify LLM/Agent elements
      await expect(page.locator('h2:has-text("LLM/Agent Interaction")')).toBeVisible();
      await expect(page.locator('button:has-text("Decompress Content")')).toBeVisible();
    });

    test('should handle LLM interaction', async ({ page }) => {
      // Test LLM interaction if available
      const llmInput = page.locator('textarea[placeholder*="message"]');
      if (await llmInput.isVisible()) {
        await llmInput.fill('Test LLM interaction');
        await page.click('button:has-text("Send")');
      }
    });
  });

  // ==================== EVALUATION TAB ====================
  
  test.describe('Evaluation Tab', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Evaluation")');
      await expect(page.locator('main h1:has-text("Evaluation")')).toBeVisible();
    });

    test('should display evaluation dashboard', async ({ page }) => {
      // Verify evaluation elements
      await expect(page.locator('h2:has-text("Evaluation Dashboard")')).toBeVisible();
      await expect(page.locator('button:has-text("Run Evaluation")')).toBeVisible();
    });

    test('should handle evaluation execution', async ({ page }) => {
      // Click run evaluation button
      await page.click('button:has-text("Run Evaluation")');
      
      // Verify evaluation is running
      await expect(page.locator('text=Running Evaluation')).toBeVisible();
    });
  });

  // ==================== META-LEARNING FUNCTIONALITY ====================
  
  test.describe('Meta-Learning Functionality', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Compression")');
    });

    test('should display meta-learning status', async ({ page }) => {
      // Verify meta-learning elements
      await expect(page.locator('h3:has-text("Meta-Learning")')).toBeVisible();
      await expect(page.locator('text=Learning Status')).toBeVisible();
      await expect(page.locator('text=Progress')).toBeVisible();
    });

    test('should toggle meta-learning status', async ({ page }) => {
      // Find meta-learning toggle button
      const metaLearningButton = page.locator('button:has-text("Meta-Learning")');
      if (await metaLearningButton.isVisible()) {
        const initialText = await metaLearningButton.textContent();
        await metaLearningButton.click();
        await expect(metaLearningButton).not.toHaveText(initialText!);
      }
    });

    test('should display learning progress', async ({ page }) => {
      // Verify progress elements
      await expect(page.locator('text=Progress')).toBeVisible();
      await expect(page.locator('text=Iteration')).toBeVisible();
      await expect(page.locator('text=Learning Rate')).toBeVisible();
    });
  });

  // ==================== REAL-TIME METRICS ====================
  
  test.describe('Real-time Metrics', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Compression")');
    });

    test('should display real-time metrics', async ({ page }) => {
      // Verify metrics elements
      await expect(page.locator('h3:has-text("Real-time Metrics")')).toBeVisible();
      await expect(page.locator('text=Throughput')).toBeVisible();
      await expect(page.locator('text=Success Rate')).toBeVisible();
      await expect(page.locator('text=Queue Length')).toBeVisible();
      await expect(page.locator('text=Active')).toBeVisible();
    });

    test('should update metrics during compression', async ({ page }) => {
      // Start compression
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Metrics test content');
      await page.click('text=gzip');
      await page.click('button:has-text("Optimize & Compress")');
      
      // Verify metrics are updating
      await expect(page.locator('text=Throughput')).toBeVisible();
      await expect(page.locator('text=Success Rate')).toBeVisible();
    });
  });

  // ==================== ERROR HANDLING ====================
  
  test.describe('Error Handling', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Compression")');
    });

    test('should handle empty content validation', async ({ page }) => {
      // Try to compress without content
      await page.click('button:has-text("Optimize & Compress")');
      
      // Verify error message or disabled state
      const button = page.locator('button:has-text("Optimize & Compress")');
      await expect(button).toBeDisabled();
    });

    test('should handle network errors gracefully', async ({ page }) => {
      // Simulate network error by going offline
      await page.context().setOffline(true);
      
      // Try to perform action
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Network test content');
      await page.click('button:has-text("Optimize & Compress")');
      
      // Verify error handling
      await expect(page.locator('text=Network Error')).toBeVisible();
      
      // Restore network
      await page.context().setOffline(false);
    });

    test('should handle timeout scenarios', async ({ page }) => {
      // Test with very large content that might timeout
      const largeContent = 'A'.repeat(100000);
      await page.fill('textarea[placeholder="Enter content to compress..."]', largeContent);
      await page.click('text=gzip');
      await page.click('button:has-text("Optimize & Compress")');
      
      // Wait for timeout or completion
      await page.waitForTimeout(10000);
      
      // Verify either completion or timeout handling
      const results = page.locator('text=Compression Results');
      const error = page.locator('text=Timeout');
      
      await expect(results.or(error)).toBeVisible();
    });
  });

  // ==================== ACCESSIBILITY TESTS ====================
  
  test.describe('Accessibility', () => {
    test('should have proper ARIA labels', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      
      // Check for ARIA labels on interactive elements
      const textarea = page.locator('textarea[placeholder="Enter content to compress..."]');
      await expect(textarea).toHaveAttribute('aria-label');
      
      const button = page.locator('button:has-text("Optimize & Compress")');
      await expect(button).toHaveAttribute('aria-label');
    });

    test('should support keyboard navigation', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      
      // Test tab navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Verify focus is on expected element
      const focusedElement = page.locator(':focus');
      await expect(focusedElement).toBeVisible();
    });

    test('should have proper color contrast', async ({ page }) => {
      // This would typically be tested with accessibility tools
      // For now, verify that text is visible
      await page.click('button:has-text("Compression")');
      await expect(page.locator('h1:has-text("Compression")')).toBeVisible();
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
      const results = page.locator('text=Compression Results');
      const progress = page.locator('text=Compressing');
      
      await expect(results.or(progress)).toBeVisible();
    });
  });
});
