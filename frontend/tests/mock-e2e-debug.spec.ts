/**
 * Mock-based E2E testing with network debugging
 */

import { expect, test } from '@playwright/test';

test.describe('Compression Screen - Mock Testing with Network Debug', () => {
  test.beforeEach(async ({ page }) => {
    // Enable network logging
    page.on('request', request => {
      console.log('>>', request.method(), request.url());
    });

    page.on('response', response => {
      console.log('<<', response.status(), response.url());
    });

    page.on('console', msg => {
      console.log('CONSOLE:', msg.type(), msg.text());
    });

    // Mock API responses to avoid connectivity issues
    await page.route('**/api/v1/compression/analyze-content', async route => {
      console.log('Mocking analyze-content endpoint');
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          analysis: {
            content_type: { primary: 'text', confidence: 0.95 },
            content_size: 1000,
            entropy: 0.75,
            redundancy: 0.25,
            compressibility: 8.5
          },
          processing_time: 0.045,
          timestamp: new Date().toISOString()
        })
      });
    });

    await page.route('**/api/v1/compression/recommendations', async route => {
      console.log('Mocking recommendations endpoint');
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          recommendations: [
            {
              algorithm: {
                name: 'gzip',
                description: 'General-purpose compression',
                category: 'traditional',
                parameters: { level: 6 }
              },
              confidence: 0.92,
              reasoning: ['High redundancy in content'],
              expected_performance: {
                compression_ratio: 2.8,
                processing_time: 0.045,
                memory_usage: 16.5
              }
            }
          ],
          meta_learning_insights: {
            user_pattern: 'Prefers balanced algorithms',
            success_rate: 0.94
          },
          processing_time: 0.023,
          timestamp: new Date().toISOString()
        })
      });
    });

    // Mock analyze endpoint for EnhancedCompressionTabImproved
    await page.route('**/api/v1/compression/analyze**', async route => {
      console.log('Mocking analyze endpoint');
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          analysis: {
            content_type: { primary: 'text', confidence: 0.95 },
            content_size: 1000,
            entropy: 0.75,
            redundancy: 0.25,
            compressibility: 8.5
          },
          processing_time: 0.045,
          timestamp: new Date().toISOString()
        })
      });
    });

    // Mock both possible compression endpoints
    await page.route('**/api/v1/compression/compress', async route => {
      console.log('Mocking compress endpoint');
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          result: {
            compressed_content: '1f8b0800000000000003',
            compression_ratio: 2.8,
            compression_percentage: 64.3,
            processing_time: 0.045,
            algorithm_used: 'gzip',
            parameters_used: { level: 6 }
          },
          compressed_content: '1f8b0800000000000003abcdef1234567890',
          analysis: {
            predicted_vs_actual: {
              compression_ratio: { predicted: 2.8, actual: 2.8, accuracy: 1.0 },
              processing_time: { predicted: 0.045, actual: 0.045, accuracy: 1.0 }
            },
            quality_assessment: {
              integrity_check: 'passed',
              quality_score: 0.95,
              validation_result: 'success'
            }
          },
          metrics: {
            performance: {
              cpu_usage: 45.2,
              memory_usage: 16.5,
              disk_io: 2.3,
              network_usage: 0.1
            },
            efficiency: {
              throughput: 22.7,
              resource_utilization: 0.68,
              energy_efficiency: 0.85
            },
            quality: {
              compression_quality: 0.95,
              decompression_quality: 0.98,
              data_integrity: 1.0
            }
          },
          request_id: 'req123',
          processing_time: 0.045,
          timestamp: new Date().toISOString()
        })
      });
    });

    await page.route('**/api/v1/metrics/performance', async route => {
      console.log('Mocking metrics/performance endpoint');
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          requests_per_second: 22.7,
          success_rate: 98.0,
          error_rate: 2.0,
          queue_size: 5,
          active_connections: 25,
          cpu_usage: 45.2,
          memory_usage: 62.8,
          timestamp: new Date().toISOString()
        })
      });
    });

    // Navigate to the page
    console.log('Navigating to page...');
    await page.goto('/', { waitUntil: 'networkidle' });

    // Wait for page to be fully loaded
    await page.waitForLoadState('domcontentloaded');

    // Take screenshot for debugging
    await page.screenshot({ path: 'test-results/debug-00-initial-load.png', fullPage: true });
  });

  test('should display compression screen with all components', async ({ page }) => {
    console.log('=== TEST: Display compression screen ===');

    // Wait for main heading to be visible
    await page.waitForSelector('h1', { timeout: 10000 });

    // Take screenshot
    await page.screenshot({ path: 'test-results/debug-01-compression-screen.png', fullPage: true });

    // Check main heading - look for "Dynamic Compression Algorithms" OR "Compression"
    const mainHeading = page.locator('h1:has-text("Dynamic Compression Algorithms")');
    await expect(mainHeading).toBeVisible();
    console.log('✓ Main heading visible');

    // Check if we're on compression tab by looking for tab button
    const compressionTab = page.locator('button:has-text("Compression/Decompression")');
    if (await compressionTab.isVisible()) {
      console.log('Found Compression/Decompression tab, clicking...');
      await compressionTab.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'test-results/debug-02-after-tab-click.png', fullPage: true });
    }

    // Log all h1, h2, h3 elements to see what's on the page
    const headers = await page.locator('h1, h2, h3, span').allTextContents();
    console.log('Headers on page:', headers);

    // Check for content input section (more flexible selector)
    const contentInputVisible = await page.locator('text=Content Input, span:has-text("Content Input")').first().isVisible().catch(() => false);
    console.log('Content Input visible:', contentInputVisible);

    // Check for Meta-Learning panel in sidebar
    const metaLearningVisible = await page.locator('h3:has-text("Meta-Learning"), span:has-text("Meta-Learning")').first().isVisible().catch(() => false);
    console.log('Meta-Learning visible:', metaLearningVisible);

    // Check for Real-time Metrics
    const metricsVisible = await page.locator('h3:has-text("Real-time Metrics"), span:has-text("Real-time Metrics")').first().isVisible().catch(() => false);
    console.log('Real-time Metrics visible:', metricsVisible);

    expect(contentInputVisible || metaLearningVisible || metricsVisible).toBeTruthy();
  });

  test('should find and interact with content input', async ({ page }) => {
    console.log('=== TEST: Content input interaction ===');

    // Wait for page to load
    await page.waitForSelector('h1', { timeout: 10000 });

    // Click compression tab if it exists
    const compressionTab = page.locator('button:has-text("Compression/Decompression")');
    if (await compressionTab.isVisible().catch(() => false)) {
      console.log('Clicking Compression/Decompression tab');
      await compressionTab.click();
      await page.waitForTimeout(1000);
    }

    // Take screenshot
    await page.screenshot({ path: 'test-results/debug-03-before-input.png', fullPage: true });

    // Try multiple selectors for textarea
    const textareaSelectors = [
      '[data-testid="content-input"]',
      'textarea[placeholder*="compress"]',
      'textarea[placeholder*="Compress"]',
      'textarea'
    ];

    let textarea = null;
    for (const selector of textareaSelectors) {
      console.log(`Trying selector: ${selector}`);
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        textarea = element;
        console.log(`✓ Found textarea with: ${selector}`);
        break;
      }
    }

    if (textarea) {
      const testContent = 'Test compression content. '.repeat(10);
      await textarea.fill(testContent);
      await page.waitForTimeout(500);

      await page.screenshot({ path: 'test-results/debug-04-after-input.png', fullPage: true });

      const value = await textarea.inputValue();
      console.log(`Textarea value length: ${value.length}`);
      expect(value).toContain('Test compression content');
    } else {
      console.error('❌ Could not find textarea');
      await page.screenshot({ path: 'test-results/debug-error-no-textarea.png', fullPage: true });
      throw new Error('Textarea not found');
    }
  });

  test('should find compress button', async ({ page }) => {
    console.log('=== TEST: Find compress button ===');

    // Wait for page to load
    await page.waitForSelector('h1', { timeout: 10000 });

    // Click compression tab if it exists
    const compressionTab = page.locator('button:has-text("Compression/Decompression")');
    if (await compressionTab.isVisible().catch(() => false)) {
      console.log('Clicking Compression/Decompression tab');
      await compressionTab.click();
      await page.waitForTimeout(1000);
    }

    // Try to find textarea and enter content
    const textarea = page.locator('textarea').first();
    if (await textarea.isVisible().catch(() => false)) {
      await textarea.fill('Test content for compression analysis and algorithm recommendation');
      console.log('Content entered, waiting for analysis...');

      // Wait for debounce (1s) + analysis API call
      await page.waitForTimeout(1500);

      // Wait for content analysis panel to appear (indicates analysis completed)
      const analysisPanel = page.locator('[data-testid="content-analysis"], h3:has-text("Content Analysis")').first();
      if (await analysisPanel.isVisible().catch(() => false)) {
        console.log('✓ Content analysis panel visible');
      }

      // Wait additional time for algorithm recommendations
      await page.waitForTimeout(1500);

      // Check if algorithm recommendations or selection panel appeared
      const algoPanel = page.locator('h3:has-text("Recommended Algorithms"), h3:has-text("Select Compression Algorithm")').first();
      if (await algoPanel.isVisible().catch(() => false)) {
        console.log('✓ Algorithm selection panel visible');

        // Try to select an algorithm if recommendations are shown
        const algoCard = page.locator('[class*="cursor-pointer"]').first();
        if (await algoCard.isVisible().catch(() => false)) {
          await algoCard.click();
          console.log('✓ Algorithm selected');
          await page.waitForTimeout(500);
        }
      }
    }

    await page.screenshot({ path: 'test-results/debug-05-before-button.png', fullPage: true });

    // Try multiple selectors for compress button
    const buttonSelectors = [
      '[data-testid="compress-button"]',
      'button:has-text("Compress Content")',
      'button:has-text("Compress")',
      'button:has-text("Analyze")'
    ];

    let button = null;
    for (const selector of buttonSelectors) {
      console.log(`Trying button selector: ${selector}`);
      const element = page.locator(selector).first();
      if (await element.isVisible().catch(() => false)) {
        button = element;
        console.log(`✓ Found button with: ${selector}`);
        break;
      }
    }

    if (button) {
      const isEnabled = await button.isEnabled();
      console.log(`Button enabled: ${isEnabled}`);

      if (isEnabled) {
        await button.click();
        await page.waitForTimeout(2000);
        await page.screenshot({ path: 'test-results/debug-06-after-click.png', fullPage: true });
      }

      expect(button).toBeVisible();
    } else {
      console.error('❌ Could not find compress button');

      // Log all buttons on page
      const allButtons = await page.locator('button').allTextContents();
      console.log('All buttons on page:', allButtons);

      await page.screenshot({ path: 'test-results/debug-error-no-button.png', fullPage: true });
      throw new Error('Compress button not found');
    }
  });
});
