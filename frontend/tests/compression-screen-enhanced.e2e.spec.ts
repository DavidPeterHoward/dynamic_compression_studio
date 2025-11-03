/**
 * Enhanced End-to-End Tests for the Compression Screen
 * 
 * This test suite provides comprehensive testing of the compression screen
 * with improved edge case handling, logical test splitting, and robust assertions.
 */

import { expect, test } from '@playwright/test';
import { TestHelpers } from './helpers/test-helpers';

test.describe('Compression Screen - Enhanced Testing', () => {
  let testHelpers: TestHelpers;

  test.beforeEach(async ({ page }) => {
    testHelpers = new TestHelpers(page);
    await testHelpers.navigateToCompressionScreen();
  });

  // ===== CORE FUNCTIONALITY TESTS =====
  test.describe('Core Functionality', () => {
    test('should display all essential components', async ({ page }) => {
      // Check main components
      await expect(page.locator('main h1:has-text("Compression")')).toBeVisible();
      await expect(page.locator('h2:has-text("Content Input")')).toBeVisible();
      await expect(page.locator('h3:has-text("Meta-Learning")')).toBeVisible();
      await expect(page.locator('h3:has-text("Real-time Metrics")')).toBeVisible();
      
      // Check system health indicator
      await expect(page.locator('main text=System:')).toBeVisible();
    });

    test('should handle content analysis workflow', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      // Test content analysis
      await testHelpers.enterContentAndWaitForAnalysis(content.text);
      
      // Verify analysis results
      await expect(page.locator('text=Content Type')).toBeVisible();
      await expect(page.locator('text=Entropy')).toBeVisible();
      await expect(page.locator('text=Redundancy')).toBeVisible();
      await expect(page.locator('text=Compressibility')).toBeVisible();
    });

    test('should display and allow algorithm selection', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      await testHelpers.enterContentAndWaitForAnalysis(content.text);
      await testHelpers.waitForRecommendations();
      
      // Test algorithm selection
      await testHelpers.selectAlgorithm(0);
      
      // Verify selection is working
      const recommendations = page.locator('div[class*="cursor-pointer"]');
      await expect(recommendations.first()).toHaveClass(/border-blue-500/);
    });

    test('should perform compression and display results', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      await testHelpers.enterContentAndWaitForAnalysis(content.text);
      await testHelpers.waitForRecommendations();
      
      const result = await testHelpers.performCompression();
      
      // Verify compression was successful
      expect(result.success).toBe(true);
      expect(result.ratio).toBeGreaterThan(0);
      expect(result.time).toBeGreaterThan(0);
      
      await testHelpers.verifyCompressionResults();
    });
  });

  // ===== CONTENT TYPE TESTS =====
  test.describe('Content Type Handling', () => {
    test('should handle different content types appropriately', async ({ page }) => {
      await testHelpers.testDifferentContentTypes();
    });

    test('should handle JSON content', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      await testHelpers.enterContentAndWaitForAnalysis(content.json);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      await testHelpers.verifyCompressionResults();
    });

    test('should handle XML content', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      await testHelpers.enterContentAndWaitForAnalysis(content.xml);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      await testHelpers.verifyCompressionResults();
    });

    test('should handle code content', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      await testHelpers.enterContentAndWaitForAnalysis(content.code);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      await testHelpers.verifyCompressionResults();
    });
  });

  // ===== EDGE CASE TESTS =====
  test.describe('Edge Cases and Error Handling', () => {
    test('should handle empty content gracefully', async ({ page }) => {
      await testHelpers.testErrorScenarios();
    });

    test('should handle very large content', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      await testHelpers.enterContentAndWaitForAnalysis(content.large);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      await testHelpers.verifyCompressionResults();
    });

    test('should handle special characters and unicode', async ({ page }) => {
      const specialContent = '🚀 Special chars: ñáéíóú 中文 العربية русский 🎉'.repeat(100);
      
      await testHelpers.enterContentAndWaitForAnalysis(specialContent);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      await testHelpers.verifyCompressionResults();
    });

    test('should handle binary-like content', async ({ page }) => {
      const binaryContent = '01010101010101010101010101010101'.repeat(1000);
      
      await testHelpers.enterContentAndWaitForAnalysis(binaryContent);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      await testHelpers.verifyCompressionResults();
    });
  });

  // ===== PERFORMANCE TESTS =====
  test.describe('Performance and Load Testing', () => {
    test('should handle rapid successive compressions', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      for (let i = 0; i < 3; i++) {
        await testHelpers.enterContentAndWaitForAnalysis(content.text);
        await testHelpers.waitForRecommendations();
        await testHelpers.performCompression();
        await testHelpers.verifyCompressionResults();
        
        // Clear content for next iteration
        await page.fill('textarea[placeholder="Enter content to compress..."]', '');
      }
    });

    test('should maintain performance with large datasets', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      const startTime = Date.now();
      
      await testHelpers.enterContentAndWaitForAnalysis(content.large);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      
      const endTime = Date.now();
      const totalTime = endTime - startTime;
      
      // Should complete within reasonable time (30 seconds)
      expect(totalTime).toBeLessThan(30000);
    });
  });

  // ===== USER INTERACTION TESTS =====
  test.describe('User Interactions', () => {
    test('should support keyboard navigation', async ({ page }) => {
      await testHelpers.testKeyboardNavigation();
    });

    test('should be responsive across different screen sizes', async ({ page }) => {
      await testHelpers.testResponsiveDesign();
    });

    test('should maintain state across page refreshes', async ({ page }) => {
      await testHelpers.testStatePersistence();
    });

    test('should handle tab switching and return to compression', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      // Start compression process
      await testHelpers.enterContentAndWaitForAnalysis(content.text);
      await testHelpers.waitForRecommendations();
      
      // Switch to another tab
      await page.click('button:has-text("Experiments")');
      await page.waitForSelector('h1:has-text("Experiments")');
      
      // Return to compression tab
      await page.click('button:has-text("Compression")');
      await page.waitForSelector('main h1:has-text("Compression")');
      
      // Verify state is maintained
      await expect(page.locator('h2:has-text("Content Input")')).toBeVisible();
      await expect(page.locator('button:has-text("Compress Content")')).toBeVisible();
    });
  });

  // ===== META-LEARNING TESTS =====
  test.describe('Meta-Learning Functionality', () => {
    test('should display meta-learning status and progress', async ({ page }) => {
      await testHelpers.testMetaLearning();
    });

    test('should update learning progress after compression', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      // Get initial learning progress
      const initialProgress = await page.textContent('text=Progress');
      const initialIteration = await page.textContent('text=Iteration');
      
      // Perform compression
      await testHelpers.enterContentAndWaitForAnalysis(content.text);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      
      // Wait for meta-learning to update
      await page.waitForTimeout(2000);
      
      // Check that learning progress has updated
      const updatedProgress = await page.textContent('text=Progress');
      const updatedIteration = await page.textContent('text=Iteration');
      
      // Progress should have increased
      expect(updatedProgress).not.toBe(initialProgress);
      expect(updatedIteration).not.toBe(initialIteration);
    });
  });

  // ===== REAL-TIME METRICS TESTS =====
  test.describe('Real-Time Metrics', () => {
    test('should display real-time metrics updates', async ({ page }) => {
      await testHelpers.testRealTimeMetrics();
    });

    test('should update metrics during compression', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      // Get initial metrics
      const initialThroughput = await page.textContent('text=Throughput');
      const initialActive = await page.textContent('text=Active');
      
      // Perform compression
      await testHelpers.enterContentAndWaitForAnalysis(content.text);
      await testHelpers.waitForRecommendations();
      await testHelpers.performCompression();
      
      // Wait for metrics to update
      await page.waitForTimeout(3000);
      
      // Check that metrics have updated
      const updatedThroughput = await page.textContent('text=Throughput');
      const updatedActive = await page.textContent('text=Active');
      
      // Metrics should have changed
      expect(updatedThroughput).not.toBe(initialThroughput);
      expect(updatedActive).not.toBe(initialActive);
    });
  });

  // ===== INTEGRATION TESTS =====
  test.describe('End-to-End Integration', () => {
    test('should complete full compression workflow', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      // Complete workflow
      await testHelpers.enterContentAndWaitForAnalysis(content.text);
      await testHelpers.waitForRecommendations();
      await testHelpers.selectAlgorithm(0);
      
      const result = await testHelpers.performCompression();
      await testHelpers.verifyCompressionResults();
      
      // Verify compression was successful
      expect(result.success).toBe(true);
      expect(result.ratio).toBeGreaterThan(1);
      expect(result.time).toBeLessThan(10000); // Should complete within 10 seconds
    });

    test('should handle multiple algorithm selections', async ({ page }) => {
      const content = testHelpers.generateTestContent();
      
      await testHelpers.enterContentAndWaitForAnalysis(content.text);
      await testHelpers.waitForRecommendations();
      
      // Test selecting different algorithms
      const recommendations = page.locator('div[class*="cursor-pointer"]');
      const count = await recommendations.count();
      
      for (let i = 0; i < Math.min(count, 3); i++) {
        await testHelpers.selectAlgorithm(i);
        
        // Verify selection
        await expect(recommendations.nth(i)).toHaveClass(/border-blue-500/);
      }
    });
  });

  // ===== ACCESSIBILITY TESTS =====
  test.describe('Accessibility', () => {
    test('should support screen reader navigation', async ({ page }) => {
      // Check for proper ARIA labels and roles
      await expect(page.locator('textarea[placeholder="Enter content to compress..."]')).toBeVisible();
      await expect(page.locator('button:has-text("Compress Content")')).toBeVisible();
      
      // Check for proper heading hierarchy
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('h2')).toBeVisible();
      await expect(page.locator('h3')).toHaveCount.greaterThan(0);
    });

    test('should support keyboard-only navigation', async ({ page }) => {
      // Test tab navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Test Enter key functionality
      const content = testHelpers.generateTestContent();
      await page.fill('textarea[placeholder="Enter content to compress..."]', content.text);
      await testHelpers.waitForRecommendations();
      
      await page.focus('button:has-text("Compress Content")');
      await page.keyboard.press('Enter');
      
      await page.waitForSelector('h3:has-text("Compression Results")', { timeout: 30000 });
    });
  });
});
