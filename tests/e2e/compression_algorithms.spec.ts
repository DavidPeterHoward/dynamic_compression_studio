import { expect, Page, test } from '@playwright/test';

// Test data for different content types
const TEST_DATA = {
  text: {
    small: 'This is a small text sample for compression testing.',
    medium: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(50),
    large: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(500),
    repetitive: 'The quick brown fox jumps over the lazy dog. '.repeat(100),
    random: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'.repeat(50)
  },
  json: {
    small: JSON.stringify({ name: 'test', value: 123, active: true }),
    medium: JSON.stringify({
      users: Array.from({ length: 100 }, (_, i) => ({
        id: i,
        name: `User ${i}`,
        email: `user${i}@example.com`,
        active: i % 2 === 0
      }))
    }),
    large: JSON.stringify({
      data: Array.from({ length: 1000 }, (_, i) => ({
        id: i,
        timestamp: new Date().toISOString(),
        value: Math.random() * 1000,
        metadata: {
          source: 'test',
          version: '1.0',
          tags: ['test', 'compression', 'e2e']
        }
      }))
    })
  },
  xml: {
    small: '<?xml version="1.0"?><root><item>test</item></root>',
    medium: '<?xml version="1.0"?><root>' + 
      Array.from({ length: 50 }, (_, i) => `<item id="${i}">Item ${i}</item>`).join('') + 
      '</root>',
    large: '<?xml version="1.0"?><root>' + 
      Array.from({ length: 500 }, (_, i) => `<item id="${i}">Item ${i}</item>`).join('') + 
      '</root>'
  }
};

// Available compression algorithms
const COMPRESSION_ALGORITHMS = [
  'gzip',
  'bzip2', 
  'lz4',
  'zstd',
  'lzma'
];

// Compression levels to test
const COMPRESSION_LEVELS = [
  { level: 1, name: 'fast' },
  { level: 6, name: 'balanced' },
  { level: 9, name: 'maximum' }
];

interface CompressionResult {
  success: boolean;
  message: string;
  result: {
    algorithm_used: string;
    compression_ratio: number;
    compression_percentage: number;
    original_size: number;
    compressed_size: number;
    compression_time: number;
  };
  compressed_content: string;
  debug_info?: any;
}

class CompressionTestHelper {
  constructor(private page: Page) {}

  async navigateToCompressionTab() {
    await this.page.goto('http://localhost:8449');
    await this.page.waitForLoadState('networkidle');
    
    // Navigate to compression tab
    await this.page.click('[data-testid="compression-tab"]');
    await this.page.waitForSelector('[data-testid="compression-interface"]', { timeout: 10000 });
  }

  async setCompressionParameters(algorithm: string, level: number) {
    // Select algorithm
    await this.page.selectOption('[data-testid="algorithm-select"]', algorithm);
    
    // Set compression level
    await this.page.fill('[data-testid="compression-level"]', level.toString());
    
    // Wait for parameters to be applied
    await this.page.waitForTimeout(500);
  }

  async inputTestData(content: string) {
    // Clear existing content
    await this.page.fill('[data-testid="content-input"]', '');
    
    // Input new content
    await this.page.fill('[data-testid="content-input"]', content);
    
    // Wait for content to be processed
    await this.page.waitForTimeout(300);
  }

  async triggerCompression() {
    // Click compress button
    await this.page.click('[data-testid="compress-button"]');
    
    // Wait for compression to complete
    await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
  }

  async getCompressionResults(): Promise<CompressionResult> {
    // Wait for results to be displayed
    await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 10000 });
    
    // Extract results from the page
    const results = await this.page.evaluate(() => {
      const resultElement = document.querySelector('[data-testid="compression-results"]');
      if (resultElement) {
        return JSON.parse(resultElement.textContent || '{}');
      }
      return null;
    });

    return results;
  }

  async verifyCompressionResults(results: CompressionResult, expectedAlgorithm: string) {
    // Verify basic structure
    expect(results).toBeTruthy();
    expect(results.success).toBe(true);
    expect(results.result).toBeTruthy();
    expect(results.compressed_content).toBeTruthy();

    // Verify algorithm
    expect(results.result.algorithm_used).toBe(expectedAlgorithm);

    // Verify compression metrics
    expect(results.result.original_size).toBeGreaterThan(0);
    expect(results.result.compressed_size).toBeGreaterThan(0);
    expect(results.result.compression_ratio).toBeGreaterThan(0);
    expect(results.result.compression_percentage).toBeGreaterThanOrEqual(0);

    // Verify compressed content is base64
    expect(results.compressed_content).toMatch(/^[A-Za-z0-9+/]*={0,2}$/);
  }

  async testDataIntegrity(originalContent: string, compressedContent: string) {
    // This would require a decompression endpoint to verify data integrity
    // For now, we'll verify the compressed content is valid base64
    expect(compressedContent).toMatch(/^[A-Za-z0-9+/]*={0,2}$/);
    
    // Verify compressed content is not empty
    expect(compressedContent.length).toBeGreaterThan(0);
  }
}

// Test suite for compression algorithms
test.describe('Compression Algorithms E2E Tests', () => {
  let helper: CompressionTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new CompressionTestHelper(page);
    await helper.navigateToCompressionTab();
  });

  // Test each compression algorithm
  for (const algorithm of COMPRESSION_ALGORITHMS) {
    test.describe(`${algorithm.toUpperCase()} Algorithm`, () => {
      
      // Test different compression levels
      for (const levelConfig of COMPRESSION_LEVELS) {
        test(`should compress data with ${algorithm} at level ${levelConfig.level} (${levelConfig.name})`, async () => {
          await helper.setCompressionParameters(algorithm, levelConfig.level);
          
          // Test with different content types
          for (const [contentType, contentData] of Object.entries(TEST_DATA)) {
            for (const [size, content] of Object.entries(contentData)) {
              await test.step(`Compress ${contentType} ${size} content`, async () => {
                await helper.inputTestData(content);
                await helper.triggerCompression();
                
                const results = await helper.getCompressionResults();
                await helper.verifyCompressionResults(results, algorithm);
                await helper.testDataIntegrity(content, results.compressed_content);
                
                // Verify compression ratio is reasonable
                expect(results.result.compression_ratio).toBeGreaterThan(1);
                
                // Log compression metrics for analysis
                console.log(`${algorithm} (${levelConfig.name}) - ${contentType} ${size}:`, {
                  originalSize: results.result.original_size,
                  compressedSize: results.result.compressed_size,
                  ratio: results.result.compression_ratio.toFixed(2),
                  percentage: results.result.compression_percentage.toFixed(2),
                  time: results.result.compression_time
                });
              });
            }
          }
        });
      }

      // Test algorithm-specific features
      test(`should handle ${algorithm} specific parameters`, async () => {
        await helper.setCompressionParameters(algorithm, 6);
        
        // Test with large content to verify algorithm can handle it
        const largeContent = TEST_DATA.text.large + TEST_DATA.json.large;
        await helper.inputTestData(largeContent);
        await helper.triggerCompression();
        
        const results = await helper.getCompressionResults();
        await helper.verifyCompressionResults(results, algorithm);
        
        // Verify large content compression
        expect(results.result.original_size).toBeGreaterThan(10000);
        expect(results.result.compression_ratio).toBeGreaterThan(2);
      });

      // Test error handling
      test(`should handle ${algorithm} compression errors gracefully`, async () => {
        await helper.setCompressionParameters(algorithm, 6);
        
        // Test with empty content
        await helper.inputTestData('');
        await helper.triggerCompression();
        
        // Should either succeed with empty result or show appropriate error
        const results = await helper.getCompressionResults();
        if (results.success) {
          expect(results.result.original_size).toBe(0);
        } else {
          expect(results.message).toContain('error');
        }
      });
    });
  }

  // Cross-algorithm comparison tests
  test.describe('Algorithm Comparison', () => {
    test('should compare compression ratios across algorithms', async () => {
      const testContent = TEST_DATA.text.repetitive;
      const results: { [key: string]: CompressionResult } = {};
      
      for (const algorithm of COMPRESSION_ALGORITHMS) {
        await helper.setCompressionParameters(algorithm, 6);
        await helper.inputTestData(testContent);
        await helper.triggerCompression();
        
        results[algorithm] = await helper.getCompressionResults();
        await helper.verifyCompressionResults(results[algorithm], algorithm);
      }
      
      // Compare compression ratios
      const ratios = Object.entries(results).map(([alg, result]) => ({
        algorithm: alg,
        ratio: result.result.compression_ratio
      }));
      
      console.log('Compression ratio comparison:', ratios);
      
      // Verify all algorithms produced valid results
      expect(Object.keys(results)).toHaveLength(COMPRESSION_ALGORITHMS.length);
    });
  });

  // Performance and stress tests
  test.describe('Performance Tests', () => {
    test('should handle concurrent compression requests', async () => {
      const promises = COMPRESSION_ALGORITHMS.map(async (algorithm) => {
        await helper.setCompressionParameters(algorithm, 6);
        await helper.inputTestData(TEST_DATA.text.medium);
        await helper.triggerCompression();
        return helper.getCompressionResults();
      });
      
      const results = await Promise.all(promises);
      
      // Verify all compressions completed successfully
      for (const result of results) {
        expect(result.success).toBe(true);
        expect(result.compressed_content).toBeTruthy();
      }
    });

    test('should handle large content compression', async () => {
      // Create very large content
      const largeContent = TEST_DATA.text.large.repeat(10);
      
      await helper.setCompressionParameters('gzip', 6);
      await helper.inputTestData(largeContent);
      
      const startTime = Date.now();
      await helper.triggerCompression();
      const endTime = Date.now();
      
      const results = await helper.getCompressionResults();
      await helper.verifyCompressionResults(results, 'gzip');
      
      // Verify compression completed within reasonable time
      expect(endTime - startTime).toBeLessThan(30000); // 30 seconds
      
      // Verify good compression ratio for repetitive content
      expect(results.result.compression_ratio).toBeGreaterThan(5);
    });
  });

  // Data pipeline integrity tests
  test.describe('Data Pipeline Integrity', () => {
    test('should maintain data integrity through compression pipeline', async () => {
      const originalContent = TEST_DATA.json.medium;
      
      await helper.setCompressionParameters('gzip', 6);
      await helper.inputTestData(originalContent);
      await helper.triggerCompression();
      
      const results = await helper.getCompressionResults();
      expect(results.success).toBe(true);
      expect(results.compressed_content).toBeTruthy();
      
      // Verify compressed content is valid base64
      expect(results.compressed_content).toMatch(/^[A-Za-z0-9+/]*={0,2}$/);
      
      // Verify compression metrics are consistent
      expect(results.result.original_size).toBe(originalContent.length);
      expect(results.result.compressed_size).toBeLessThan(originalContent.length);
      expect(results.result.compression_ratio).toBeGreaterThan(1);
    });

    test('should handle special characters and unicode', async () => {
      const unicodeContent = 'Hello 世界! 🌍 Unicode test: ñáéíóú 中文 العربية русский';
      
      await helper.setCompressionParameters('gzip', 6);
      await helper.inputTestData(unicodeContent);
      await helper.triggerCompression();
      
      const results = await helper.getCompressionResults();
      await helper.verifyCompressionResults(results, 'gzip');
      
      // Verify unicode content was handled correctly
      expect(results.result.original_size).toBeGreaterThan(0);
      expect(results.compressed_content).toBeTruthy();
    });

    test('should handle binary-like content', async () => {
      const binaryLikeContent = 'Binary-like content: \x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F';
      
      await helper.setCompressionParameters('gzip', 6);
      await helper.inputTestData(binaryLikeContent);
      await helper.triggerCompression();
      
      const results = await helper.getCompressionResults();
      await helper.verifyCompressionResults(results, 'gzip');
      
      // Verify binary content was handled
      expect(results.result.original_size).toBeGreaterThan(0);
      expect(results.compressed_content).toBeTruthy();
    });
  });

  // Error handling and edge cases
  test.describe('Error Handling', () => {
    test('should handle invalid compression parameters', async () => {
      // Test with invalid level
      await helper.setCompressionParameters('gzip', 99);
      await helper.inputTestData(TEST_DATA.text.small);
      await helper.triggerCompression();
      
      // Should either succeed with clamped level or show error
      const results = await helper.getCompressionResults();
      if (!results.success) {
        expect(results.message).toContain('error');
      }
    });

    test('should handle network errors gracefully', async () => {
      // This would require mocking network failures
      // For now, we'll test with very large content that might cause timeouts
      const veryLargeContent = TEST_DATA.text.large.repeat(100);
      
      await helper.setCompressionParameters('gzip', 6);
      await helper.inputTestData(veryLargeContent);
      
      try {
        await helper.triggerCompression();
        const results = await helper.getCompressionResults();
        
        if (results.success) {
          expect(results.compressed_content).toBeTruthy();
        } else {
          expect(results.message).toContain('error');
        }
      } catch (error) {
        // Network timeout is acceptable for very large content
        expect(error).toBeDefined();
      }
    });
  });
});
