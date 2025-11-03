import { expect, Page, test } from '@playwright/test';

interface AlgorithmTestConfig {
  algorithm: string;
  supportedLevels: number[];
  expectedFeatures: string[];
  optimalContentTypes: string[];
  performanceExpectations: {
    minCompressionRatio: number;
    maxCompressionTime: number;
  };
}

const ALGORITHM_CONFIGS: AlgorithmTestConfig[] = [
  {
    algorithm: 'gzip',
    supportedLevels: [1, 6, 9],
    expectedFeatures: ['deflate', 'crc32', 'sliding_window'],
    optimalContentTypes: ['text', 'json', 'xml'],
    performanceExpectations: {
      minCompressionRatio: 2.0,
      maxCompressionTime: 5000
    }
  },
  {
    algorithm: 'bzip2',
    supportedLevels: [1, 6, 9],
    expectedFeatures: ['burrows_wheeler', 'huffman_coding', 'run_length_encoding'],
    optimalContentTypes: ['text', 'log', 'repetitive'],
    performanceExpectations: {
      minCompressionRatio: 3.0,
      maxCompressionTime: 10000
    }
  },
  {
    algorithm: 'lz4',
    supportedLevels: [1, 3, 6, 9],
    expectedFeatures: ['lz77', 'fast_compression', 'low_memory'],
    optimalContentTypes: ['binary', 'real_time', 'streaming'],
    performanceExpectations: {
      minCompressionRatio: 1.5,
      maxCompressionTime: 2000
    }
  },
  {
    algorithm: 'zstd',
    supportedLevels: [1, 6, 15, 22],
    expectedFeatures: ['dictionary_training', 'multi_threading', 'content_size'],
    optimalContentTypes: ['mixed', 'large_files', 'streaming'],
    performanceExpectations: {
      minCompressionRatio: 2.5,
      maxCompressionTime: 8000
    }
  },
  {
    algorithm: 'lzma',
    supportedLevels: [1, 6, 9],
    expectedFeatures: ['lzma2', 'range_coding', 'dictionary_compression'],
    optimalContentTypes: ['archives', 'executables', 'binary'],
    performanceExpectations: {
      minCompressionRatio: 4.0,
      maxCompressionTime: 15000
    }
  }
];

class IndividualAlgorithmTester {
  constructor(private page: Page) {}

  async navigateToCompressionTab() {
    await this.page.goto('http://localhost:8449');
    await this.page.waitForLoadState('networkidle');
    await this.page.click('[data-testid="compression-tab"]');
    await this.page.waitForSelector('[data-testid="compression-interface"]', { timeout: 10000 });
  }

  async testAlgorithmConfiguration(config: AlgorithmTestConfig) {
    // Test algorithm selection
    await this.page.selectOption('[data-testid="algorithm-select"]', config.algorithm);
    await this.page.waitForTimeout(500);
    
    // Verify algorithm is selected
    const selectedAlgorithm = await this.page.inputValue('[data-testid="algorithm-select"]');
    expect(selectedAlgorithm).toBe(config.algorithm);
  }

  async testCompressionLevels(config: AlgorithmTestConfig) {
    const testContent = 'Level testing content. '.repeat(100);
    
    for (const level of config.supportedLevels) {
      await test.step(`Test ${config.algorithm} at level ${level}`, async () => {
        // Set compression level
        await this.page.fill('[data-testid="compression-level"]', level.toString());
        await this.page.waitForTimeout(300);
        
        // Input test content
        await this.page.fill('[data-testid="content-input"]', testContent);
        await this.page.waitForTimeout(300);
        
        // Trigger compression
        const startTime = Date.now();
        await this.page.click('[data-testid="compress-button"]');
        await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
        const endTime = Date.now();
        
        // Get results
        const results = await this.page.evaluate(() => {
          const resultElement = document.querySelector('[data-testid="compression-results"]');
          return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
        });
        
        // Verify results
        expect(results).toBeTruthy();
        expect(results.success).toBe(true);
        expect(results.result.algorithm_used).toBe(config.algorithm);
        expect(results.compressed_content).toBeTruthy();
        
        // Verify performance expectations
        const compressionTime = endTime - startTime;
        expect(compressionTime).toBeLessThan(config.performanceExpectations.maxCompressionTime);
        expect(results.result.compression_ratio).toBeGreaterThanOrEqual(config.performanceExpectations.minCompressionRatio);
        
        console.log(`${config.algorithm} Level ${level}:`, {
          ratio: results.result.compression_ratio.toFixed(2),
          time: compressionTime,
          originalSize: results.result.original_size,
          compressedSize: results.result.compressed_size
        });
      });
    }
  }

  async testContentTypeOptimization(config: AlgorithmTestConfig) {
    const contentTypes = {
      text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(50),
      json: JSON.stringify({ data: Array.from({ length: 100 }, (_, i) => ({ id: i, value: `item_${i}` })) }),
      xml: '<?xml version="1.0"?><root>' + Array.from({ length: 50 }, (_, i) => `<item id="${i}">Item ${i}</item>`).join('') + '</root>',
      repetitive: 'The quick brown fox jumps over the lazy dog. '.repeat(100),
      binary: 'Binary-like content: \x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F'.repeat(10)
    };
    
    for (const [contentType, content] of Object.entries(contentTypes)) {
      await test.step(`Test ${config.algorithm} with ${contentType} content`, async () => {
        await this.page.fill('[data-testid="compression-level"]', '6');
        await this.page.fill('[data-testid="content-input"]', content);
        await this.page.waitForTimeout(300);
        
        await this.page.click('[data-testid="compress-button"]');
        await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
        
        const results = await this.page.evaluate(() => {
          const resultElement = document.querySelector('[data-testid="compression-results"]');
          return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
        });
        
        expect(results.success).toBe(true);
        expect(results.result.original_size).toBe(content.length);
        expect(results.compressed_content).toBeTruthy();
        
        // Log compression effectiveness for this content type
        console.log(`${config.algorithm} - ${contentType}:`, {
          ratio: results.result.compression_ratio.toFixed(2),
          percentage: results.result.compression_percentage.toFixed(2),
          originalSize: results.result.original_size,
          compressedSize: results.result.compressed_size
        });
      });
    }
  }

  async testAlgorithmSpecificFeatures(config: AlgorithmTestConfig) {
    await test.step(`Test ${config.algorithm} specific features`, async () => {
      // Test with optimal content for this algorithm
      const optimalContent = this.getOptimalContentForAlgorithm(config.algorithm);
      
      await this.page.fill('[data-testid="compression-level"]', '6');
      await this.page.fill('[data-testid="content-input"]', optimalContent);
      await this.page.waitForTimeout(300);
      
      await this.page.click('[data-testid="compress-button"]');
      await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
      
      const results = await this.page.evaluate(() => {
        const resultElement = document.querySelector('[data-testid="compression-results"]');
        return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
      });
      
      expect(results.success).toBe(true);
      
      // Verify algorithm-specific performance
      if (config.algorithm === 'lz4') {
        // LZ4 should be very fast
        expect(results.result.compression_time).toBeLessThan(1000);
      } else if (config.algorithm === 'lzma') {
        // LZMA should have high compression ratio
        expect(results.result.compression_ratio).toBeGreaterThan(3.0);
      } else if (config.algorithm === 'zstd') {
        // ZSTD should have good balance
        expect(results.result.compression_ratio).toBeGreaterThan(2.0);
        expect(results.result.compression_time).toBeLessThan(5000);
      }
    });
  }

  getOptimalContentForAlgorithm(algorithm: string): string {
    switch (algorithm) {
      case 'gzip':
        return 'Text content with some repetition. '.repeat(100);
      case 'bzip2':
        return 'Highly repetitive content for Burrows-Wheeler transform. '.repeat(200);
      case 'lz4':
        return 'Fast compression test data. '.repeat(50);
      case 'zstd':
        return 'Zstandard optimal content with mixed patterns. '.repeat(150);
      case 'lzma':
        return 'LZMA optimal content with complex patterns. '.repeat(100);
      default:
        return 'Default test content. '.repeat(100);
    }
  }

  async testErrorHandling(config: AlgorithmTestConfig) {
    await test.step(`Test ${config.algorithm} error handling`, async () => {
      // Test with empty content
      await this.page.fill('[data-testid="compression-level"]', '6');
      await this.page.fill('[data-testid="content-input"]', '');
      await this.page.waitForTimeout(300);
      
      await this.page.click('[data-testid="compress-button"]');
      await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
      
      const results = await this.page.evaluate(() => {
        const resultElement = document.querySelector('[data-testid="compression-results"]');
        return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
      });
      
      // Should handle empty content gracefully
      if (results.success) {
        expect(results.result.original_size).toBe(0);
      } else {
        expect(results.message).toContain('error');
      }
      
      // Test with invalid level
      await this.page.fill('[data-testid="compression-level"]', '999');
      await this.page.fill('[data-testid="content-input"]', 'Test content');
      await this.page.waitForTimeout(300);
      
      await this.page.click('[data-testid="compress-button"]');
      await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
      
      const invalidResults = await this.page.evaluate(() => {
        const resultElement = document.querySelector('[data-testid="compression-results"]');
        return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
      });
      
      // Should either succeed with clamped level or show error
      expect(invalidResults).toBeTruthy();
    });
  }
}

// Test suite for individual algorithm testing
test.describe('Individual Algorithm Tests', () => {
  let tester: IndividualAlgorithmTester;

  test.beforeEach(async ({ page }) => {
    tester = new IndividualAlgorithmTester(page);
    await tester.navigateToCompressionTab();
  });

  // Test each algorithm individually
  for (const config of ALGORITHM_CONFIGS) {
    test.describe(`${config.algorithm.toUpperCase()} Algorithm`, () => {
      
      test('should configure algorithm correctly', async () => {
        await tester.testAlgorithmConfiguration(config);
      });

      test('should support all compression levels', async () => {
        await tester.testCompressionLevels(config);
      });

      test('should optimize for different content types', async () => {
        await tester.testContentTypeOptimization(config);
      });

      test('should utilize algorithm-specific features', async () => {
        await tester.testAlgorithmSpecificFeatures(config);
      });

      test('should handle errors gracefully', async () => {
        await tester.testErrorHandling(config);
      });
    });
  }

  // Cross-algorithm comparison tests
  test.describe('Algorithm Comparison', () => {
    test('should compare compression effectiveness across algorithms', async () => {
      const testContent = 'Comparison test content with mixed patterns. '.repeat(200);
      const results: { [key: string]: any } = {};
      
      for (const config of ALGORITHM_CONFIGS) {
        await tester.navigateToCompressionTab();
        await tester.testAlgorithmConfiguration(config);
        
        await tester.page.fill('[data-testid="compression-level"]', '6');
        await tester.page.fill('[data-testid="content-input"]', testContent);
        await tester.page.waitForTimeout(300);
        
        await tester.page.click('[data-testid="compress-button"]');
        await tester.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
        
        const result = await tester.page.evaluate(() => {
          const resultElement = document.querySelector('[data-testid="compression-results"]');
          return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
        });
        
        results[config.algorithm] = result;
      }
      
      // Compare results
      const comparison = Object.entries(results).map(([algorithm, result]) => ({
        algorithm,
        ratio: result.result.compression_ratio,
        time: result.result.compression_time,
        originalSize: result.result.original_size,
        compressedSize: result.result.compressed_size
      }));
      
      console.log('Algorithm comparison results:', comparison);
      
      // Verify all algorithms produced valid results
      expect(Object.keys(results)).toHaveLength(ALGORITHM_CONFIGS.length);
      
      // Find best compression ratio
      const bestRatio = Math.max(...comparison.map(c => c.ratio));
      const fastestTime = Math.min(...comparison.map(c => c.time));
      
      console.log(`Best compression ratio: ${bestRatio.toFixed(2)}`);
      console.log(`Fastest compression time: ${fastestTime.toFixed(2)}ms`);
    });
  });
});
