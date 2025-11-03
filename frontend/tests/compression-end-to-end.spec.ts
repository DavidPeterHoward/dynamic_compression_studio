/**
 * End-to-End Compression Test Suite
 * 
 * This test suite verifies the complete compression workflow from input to output,
 * including content analysis, algorithm selection, compression execution, and result display.
 */

import { expect, test } from '@playwright/test';

test.describe('Compression End-to-End Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for the main application to load
    await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
    
    // Navigate to Compression tab
    await page.click('button:has-text("Compression")');
    await expect(page.locator('main h1:has-text("Compression")')).toBeVisible();
  });

  test('should complete full compression workflow with output display and copy functionality', async ({ page }) => {
    // Step 1: Enter content
    const testContent = 'This is a sample text for compression testing. It contains repeated patterns and should compress well. This is a sample text for compression testing. It contains repeated patterns and should compress well.';
    
    const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
    await contentInput.fill(testContent);
    await expect(contentInput).toHaveValue(testContent);
    
    // Step 2: Wait for content analysis
    await page.waitForTimeout(2000); // Wait for auto-analysis
    
    // Step 3: Verify compression interface is ready
    await expect(page.locator('textarea[placeholder="Enter content to compress..."]')).toBeVisible();
    await expect(page.locator('button:has-text("Optimize & Compress")')).toBeVisible();
    
    // Step 4: Select an algorithm (gzip)
    await page.click('text=gzip');
    
    // Step 5: Execute compression
    const compressButton = page.locator('button:has-text("Optimize & Compress")');
    await compressButton.click();
    
    // Step 6: Verify compression is in progress
    await expect(page.locator('button:has-text("Compressing...")')).toBeVisible();
    
    // Step 7: Wait for compression to complete
    await page.waitForTimeout(5000);
    
    // Step 8: Verify results tab is active
    await expect(page.locator('button:has-text("Results & Metrics")')).toBeVisible();
    
    // Step 9: Click on results tab to view results
    await page.click('button:has-text("Results & Metrics")');
    
    // Step 10: Verify compressed content is displayed
    await expect(page.locator('text=Compressed Content')).toBeVisible();
    await expect(page.locator('textarea[readonly]')).toBeVisible();
    
    // Step 11: Verify compression metrics are displayed
    await expect(page.locator('text=Compression Ratio')).toBeVisible();
    await expect(page.locator('text=Size Reduction')).toBeVisible();
    await expect(page.locator('text=Processing Time')).toBeVisible();
    await expect(page.locator('text=Algorithm Used')).toBeVisible();
    
    // Step 12: Test copy functionality
    const copyButton = page.locator('button:has-text("Copy")');
    await expect(copyButton).toBeVisible();
    await copyButton.click();
    
    // Step 13: Verify copy notification (if implemented)
    // Note: This might show a toast notification or change button text
    
    // Step 14: Test download functionality
    const downloadButton = page.locator('button:has-text("Download")');
    await expect(downloadButton).toBeVisible();
    
    // Step 15: Verify detailed metrics are displayed
    await expect(page.locator('text=Performance Metrics')).toBeVisible();
    await expect(page.locator('text=Quality Metrics')).toBeVisible();
    await expect(page.locator('text=Prediction Accuracy')).toBeVisible();
    await expect(page.locator('text=Size Comparison')).toBeVisible();
    
    // Step 16: Verify compressed content is not empty
    const compressedContent = page.locator('textarea[readonly]');
    const compressedText = await compressedContent.inputValue();
    expect(compressedText.length).toBeGreaterThan(0);
    expect(compressedText).not.toBe(testContent); // Should be different from original
    
    // Step 17: Verify compression ratio is displayed and reasonable
    const compressionRatio = page.locator('text=/\\d+\\.\\d+x/').first();
    await expect(compressionRatio).toBeVisible();
    
    // Step 18: Verify size reduction percentage
    const sizeReduction = page.locator('text=/\\d+\\.\\d+%/').first();
    await expect(sizeReduction).toBeVisible();
  });

  test('should handle different content types and algorithms', async ({ page }) => {
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
        content: 'A'.repeat(1000), // Repeated character pattern
        name: 'Repeated Pattern'
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
      
      // Select gzip algorithm
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

  test('should test multiple compression algorithms', async ({ page }) => {
    const testContent = 'Sample content for algorithm testing with repeated patterns for better compression results.';
    
    const algorithms = ['gzip', 'brotli', 'lz4', 'zstd'];
    
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
    const autoOptimizationToggle = page.getByText('Auto-Optimization').locator('..').locator('..').locator('button:not(:has-text("Optimize"))').first();
    await autoOptimizationToggle.click();
    
    // Select an algorithm
    await page.click('text=gzip');
    
    // Start optimization
    await page.click('button:has-text("Optimize & Compress")');
    
    // Wait for optimization to complete
    await page.waitForTimeout(10000); // Longer timeout for optimization
    
    // Verify results
    await expect(page.locator('text=Compressed Content')).toBeVisible();
    
    // Verify optimization iterations are displayed
    await expect(page.locator('text=Optimization Iterations')).toBeVisible();
    
    // Verify multiple algorithms were tested
    const iterations = page.locator('[class*="border-slate-600"]');
    const iterationCount = await iterations.count();
    expect(iterationCount).toBeGreaterThan(1);
  });

  test('should display real-time metrics during compression', async ({ page }) => {
    // Check that real-time metrics are displayed
    await expect(page.locator('h3:has-text("Real-time Metrics")')).toBeVisible();
    await expect(page.locator('text=Throughput').first()).toBeVisible();
    await expect(page.locator('text=Success Rate')).toBeVisible();
    await expect(page.locator('text=Queue Length')).toBeVisible();
    await expect(page.locator('text=Active').first()).toBeVisible();
    
    // Enter content and start compression
    const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
    await contentInput.fill('Metrics test content');
    
    await page.click('text=gzip');
    await page.click('button:has-text("Optimize & Compress")');
    
    // Wait for compression
    await page.waitForTimeout(5000);
    
    // Verify metrics are still updating
    await expect(page.locator('text=Throughput').first()).toBeVisible();
    await expect(page.locator('text=Success Rate')).toBeVisible();
  });

  test('should handle error cases gracefully', async ({ page }) => {
    // Test with empty content
    await page.click('button:has-text("Optimize & Compress")');
    
    // Button should be disabled or show error
    const compressButton = page.locator('button:has-text("Compress Content")');
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

  test('should maintain state when switching tabs', async ({ page }) => {
    // Enter content
    const testContent = 'State preservation test content.';
    const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
    await contentInput.fill(testContent);
    
    // Switch to another tab
    await page.click('button:has-text("System Metrics")');
    await page.waitForTimeout(1000);
    
    // Switch back to Compression tab
    await page.click('button:has-text("Compression")');
    
    // Verify content is still there
    await expect(contentInput).toHaveValue(testContent);
  });

  test('should provide accessible copy and download functionality', async ({ page }) => {
    // Complete compression workflow
    const testContent = 'Accessibility test content for copy and download functionality.';
    const contentInput = page.locator('textarea[placeholder="Enter content to compress..."]');
    await contentInput.fill(testContent);
    
    await page.click('text=gzip');
    await page.click('button:has-text("Optimize & Compress")');
    await page.waitForTimeout(5000);
    
    // Verify copy button has proper accessibility
    const copyButton = page.locator('button:has-text("Copy")');
    await expect(copyButton).toHaveAttribute('aria-label');
    
    // Verify download button has proper accessibility
    const downloadButton = page.locator('button:has-text("Download")');
    await expect(downloadButton).toHaveAttribute('aria-label');
    
    // Test keyboard navigation
    await copyButton.focus();
    await expect(copyButton).toBeFocused();
    
    await page.keyboard.press('Tab');
    await expect(downloadButton).toBeFocused();
  });
});
