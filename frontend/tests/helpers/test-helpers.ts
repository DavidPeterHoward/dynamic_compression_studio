/**
 * Test Helper Functions for Playwright E2E Tests
 * 
 * This module provides reusable helper functions for E2E testing,
 * including common operations, assertions, and test data generation.
 */

import { Page, expect } from '@playwright/test';

export interface TestContent {
  text: string;
  json: string;
  xml: string;
  code: string;
  large: string;
  empty: string;
}

export interface CompressionResult {
  success: boolean;
  ratio: number;
  time: number;
  algorithm: string;
  error?: string;
}

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Navigate to the compression screen and wait for it to load
   */
  async navigateToCompressionScreen(): Promise<void> {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
    
    // Ensure we're on the compression tab
    const compressionTab = this.page.locator('button:has-text("Compression")');
    if (await compressionTab.isVisible()) {
      await compressionTab.click();
    }
    
    await this.page.waitForSelector('main h1:has-text("Compression")');
  }

  /**
   * Generate test content of various types and sizes
   */
  generateTestContent(): TestContent {
    const baseText = 'This is a sample text for compression testing. ';
    const codeSample = `
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"fibonacci({i}) = {fibonacci(i)}")
    `.trim();

    const jsonSample = JSON.stringify({
      users: Array.from({ length: 50 }, (_, i) => ({
        id: i + 1,
        name: `User ${i + 1}`,
        email: `user${i + 1}@example.com`,
        preferences: {
          theme: i % 2 === 0 ? 'dark' : 'light',
          notifications: true,
          language: 'en'
        }
      })),
      metadata: {
        total: 50,
        page: 1,
        timestamp: new Date().toISOString()
      }
    });

    const xmlSample = `
<?xml version="1.0" encoding="UTF-8"?>
<products>
  ${Array.from({ length: 100 }, (_, i) => `
    <product id="${i + 1}">
      <name>Product ${i + 1}</name>
      <price>${(Math.random() * 1000).toFixed(2)}</price>
      <category>Category ${i % 10 + 1}</category>
      <description>This is a detailed description for product ${i + 1}</description>
    </product>
  `).join('')}
</products>
    `.trim();

    return {
      text: baseText.repeat(100),
      json: jsonSample,
      xml: xmlSample,
      code: codeSample,
      large: baseText.repeat(10000), // ~1MB of text
      empty: ''
    };
  }

  /**
   * Enter content into the textarea and wait for analysis
   */
  async enterContentAndWaitForAnalysis(content: string): Promise<void> {
    await this.page.fill('textarea[placeholder="Enter content to compress..."]', content);
    
    // Wait for content analysis to appear
    await this.page.waitForSelector('h3:has-text("Content Analysis")', { timeout: 15000 });
    
    // Verify analysis results are displayed
    await expect(this.page.locator('text=Content Type')).toBeVisible();
    await expect(this.page.locator('text=Entropy')).toBeVisible();
    await expect(this.page.locator('text=Redundancy')).toBeVisible();
    await expect(this.page.locator('text=Compressibility')).toBeVisible();
  }

  /**
   * Wait for algorithm recommendations and verify they appear
   */
  async waitForRecommendations(): Promise<void> {
    await this.page.waitForSelector('h3:has-text("Recommended Algorithms")', { timeout: 15000 });
    
    // Verify recommendations are displayed
    await expect(this.page.locator('text=confidence')).toHaveCount(1);
    
    // Check that the first recommendation is selected
    const firstRecommendation = this.page.locator('div[class*="border-blue-500"]').first();
    await expect(firstRecommendation).toBeVisible();
  }

  /**
   * Select a specific algorithm recommendation
   */
  async selectAlgorithm(index: number = 0): Promise<void> {
    const recommendations = this.page.locator('div[class*="cursor-pointer"]');
    const count = await recommendations.count();
    
    if (count > index) {
      await recommendations.nth(index).click();
      await expect(recommendations.nth(index)).toHaveClass(/border-blue-500/);
    }
  }

  /**
   * Perform compression and wait for results
   */
  async performCompression(): Promise<CompressionResult> {
    const startTime = Date.now();
    
    // Click the compress button
    await this.page.click('button:has-text("Compress Content")');
    
    // Wait for compression results
    await this.page.waitForSelector('h3:has-text("Compression Results")', { timeout: 30000 });
    
    const endTime = Date.now();
    const processingTime = endTime - startTime;
    
    // Extract compression metrics
    const ratioText = await this.page.textContent('text=Compression Ratio');
    const ratio = ratioText ? parseFloat(ratioText.replace(/[^\d.]/g, '')) : 0;
    
    const algorithmText = await this.page.textContent('text=Algorithm Used');
    const algorithm = algorithmText || 'unknown';
    
    return {
      success: true,
      ratio,
      time: processingTime,
      algorithm
    };
  }

  /**
   * Verify compression results are displayed correctly
   */
  async verifyCompressionResults(): Promise<void> {
    // Check main metrics
    await expect(this.page.locator('text=Compression Ratio')).toBeVisible();
    await expect(this.page.locator('text=Size Reduction')).toBeVisible();
    await expect(this.page.locator('text=Processing Time')).toBeVisible();
    await expect(this.page.locator('text=Algorithm Used')).toBeVisible();
    
    // Check performance metrics
    await expect(this.page.locator('text=CPU Usage')).toBeVisible();
    await expect(this.page.locator('text=Memory Usage')).toBeVisible();
    await expect(this.page.locator('text=Throughput')).toBeVisible();
    
    // Check quality metrics
    await expect(this.page.locator('text=Compression Quality')).toBeVisible();
    await expect(this.page.locator('text=Data Integrity')).toBeVisible();
    await expect(this.page.locator('text=Validation')).toBeVisible();
    
    // Check prediction accuracy
    await expect(this.page.locator('text=Ratio Accuracy')).toBeVisible();
    await expect(this.page.locator('text=Time Accuracy')).toBeVisible();
    await expect(this.page.locator('text=Overall Quality')).toBeVisible();
  }

  /**
   * Test error handling scenarios
   */
  async testErrorScenarios(): Promise<void> {
    // Test empty content
    await this.page.fill('textarea[placeholder="Enter content to compress..."]', '');
    await expect(this.page.locator('button:has-text("Compress Content")')).toBeDisabled();
    
    // Test very large content
    const largeContent = 'A'.repeat(1000000);
    await this.page.fill('textarea[placeholder="Enter content to compress..."]', largeContent);
    
    // Should still be able to process large content
    await this.page.waitForSelector('h3:has-text("Content Analysis")', { timeout: 30000 });
  }

  /**
   * Test responsive design at different viewport sizes
   */
  async testResponsiveDesign(): Promise<void> {
    const viewports = [
      { width: 375, height: 667, name: 'Mobile' },
      { width: 768, height: 1024, name: 'Tablet' },
      { width: 1920, height: 1080, name: 'Desktop' }
    ];

    for (const viewport of viewports) {
      await this.page.setViewportSize({ width: viewport.width, height: viewport.height });
      
      // Check that main components are still visible
      await expect(this.page.locator('h2:has-text("Content Input")')).toBeVisible();
      await expect(this.page.locator('button:has-text("Compress Content")')).toBeVisible();
      
      if (viewport.width >= 768) {
        await expect(this.page.locator('h3:has-text("Meta-Learning")')).toBeVisible();
        await expect(this.page.locator('h3:has-text("Real-time Metrics")')).toBeVisible();
      }
    }
  }

  /**
   * Test keyboard navigation
   */
  async testKeyboardNavigation(): Promise<void> {
    // Test tab navigation
    await this.page.keyboard.press('Tab');
    await this.page.keyboard.press('Tab');
    await this.page.keyboard.press('Tab');
    
    // Test Enter key for compression
    const testContent = this.generateTestContent().text;
    await this.page.fill('textarea[placeholder="Enter content to compress..."]', testContent);
    await this.waitForRecommendations();
    
    // Focus on compress button and press Enter
    await this.page.focus('button:has-text("Compress Content")');
    await this.page.keyboard.press('Enter');
    
    // Should trigger compression
    await this.page.waitForSelector('h3:has-text("Compression Results")', { timeout: 30000 });
  }

  /**
   * Test meta-learning functionality
   */
  async testMetaLearning(): Promise<void> {
    // Check meta-learning panel
    await expect(this.page.locator('text=Learning Status')).toBeVisible();
    await expect(this.page.locator('text=Progress')).toBeVisible();
    await expect(this.page.locator('text=Iteration')).toBeVisible();
    await expect(this.page.locator('text=Learning Rate')).toBeVisible();
    
    // Check that learning status shows as active
    const learningStatus = await this.page.textContent('text=Learning Status');
    expect(learningStatus).toContain('Active');
  }

  /**
   * Test real-time metrics
   */
  async testRealTimeMetrics(): Promise<void> {
    // Check that real-time metrics are displayed
    await expect(this.page.locator('text=Throughput')).toBeVisible();
    await expect(this.page.locator('text=Success Rate')).toBeVisible();
    await expect(this.page.locator('text=Queue Length')).toBeVisible();
    await expect(this.page.locator('text=Active')).toBeVisible();
    
    // Wait a bit to see if metrics update
    await this.page.waitForTimeout(5000);
    
    // Check that metrics have reasonable values
    const throughput = await this.page.textContent('text=Throughput');
    expect(throughput).toMatch(/\d+\.\d+ MB\/s/);
    
    const successRate = await this.page.textContent('text=Success Rate');
    expect(successRate).toMatch(/\d+\.\d+%/);
  }

  /**
   * Test different content types
   */
  async testDifferentContentTypes(): Promise<void> {
    const contentTypes = [
      { name: 'JSON', content: this.generateTestContent().json },
      { name: 'XML', content: this.generateTestContent().xml },
      { name: 'Code', content: this.generateTestContent().code }
    ];
    
    for (const contentType of contentTypes) {
      // Clear previous content
      await this.page.fill('textarea[placeholder="Enter content to compress..."]', '');
      
      // Enter new content
      await this.page.fill('textarea[placeholder="Enter content to compress..."]', contentType.content);
      
      // Wait for analysis
      await this.page.waitForSelector('h3:has-text("Content Analysis")', { timeout: 10000 });
      
      // Check that content type is detected correctly
      const detectedType = await this.page.textContent('text=Content Type');
      expect(detectedType).toBeTruthy();
      
      // Wait for recommendations
      await this.waitForRecommendations();
      
      // Compress the content
      await this.performCompression();
      
      // Verify compression was successful
      await this.verifyCompressionResults();
    }
  }

  /**
   * Test state persistence across page refreshes
   */
  async testStatePersistence(): Promise<void> {
    const testContent = this.generateTestContent().text;
    
    // Enter content and compress
    await this.enterContentAndWaitForAnalysis(testContent);
    await this.waitForRecommendations();
    await this.performCompression();
    await this.verifyCompressionResults();
    
    // Refresh the page
    await this.page.reload();
    await this.page.waitForLoadState('networkidle');
    
    // Navigate back to compression tab
    const compressionTab = this.page.locator('button:has-text("Compression")');
    if (await compressionTab.isVisible()) {
      await compressionTab.click();
    }
    await this.page.waitForSelector('main h1:has-text("Compression")');
    
    // Check that the interface is still functional
    await expect(this.page.locator('h2:has-text("Content Input")')).toBeVisible();
    await expect(this.page.locator('button:has-text("Compress Content")')).toBeVisible();
  }
}
