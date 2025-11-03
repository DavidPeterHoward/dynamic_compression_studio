import { expect, Page, test } from '@playwright/test';

interface SystemIntegrationTest {
  name: string;
  description: string;
  algorithm: string;
  level: number;
  content: string;
  expectedResults: {
    minCompressionRatio: number;
    maxCompressionTime: number;
    shouldSucceed: boolean;
  };
}

const SYSTEM_INTEGRATION_TESTS: SystemIntegrationTest[] = [
  {
    name: 'GZIP Text Compression',
    description: 'Test GZIP compression with text content',
    algorithm: 'gzip',
    level: 6,
    content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(100),
    expectedResults: {
      minCompressionRatio: 2.0,
      maxCompressionTime: 5000,
      shouldSucceed: true
    }
  },
  {
    name: 'BZIP2 Repetitive Content',
    description: 'Test BZIP2 with highly repetitive content',
    algorithm: 'bzip2',
    level: 6,
    content: 'The quick brown fox jumps over the lazy dog. '.repeat(200),
    expectedResults: {
      minCompressionRatio: 3.0,
      maxCompressionTime: 10000,
      shouldSucceed: true
    }
  },
  {
    name: 'LZ4 Fast Compression',
    description: 'Test LZ4 fast compression with binary-like content',
    algorithm: 'lz4',
    level: 3,
    content: 'Fast compression test data. '.repeat(50) + '\x00\x01\x02\x03\x04\x05'.repeat(10),
    expectedResults: {
      minCompressionRatio: 1.5,
      maxCompressionTime: 2000,
      shouldSucceed: true
    }
  },
  {
    name: 'ZSTD Mixed Content',
    description: 'Test ZSTD with mixed content types',
    algorithm: 'zstd',
    level: 15,
    content: JSON.stringify({
      text: 'Mixed content test',
      numbers: Array.from({ length: 100 }, (_, i) => i),
      nested: {
        data: 'Nested object data',
        array: Array.from({ length: 50 }, (_, i) => ({ id: i, value: `item_${i}` }))
      }
    }),
    expectedResults: {
      minCompressionRatio: 2.5,
      maxCompressionTime: 8000,
      shouldSucceed: true
    }
  },
  {
    name: 'LZMA Maximum Compression',
    description: 'Test LZMA with maximum compression settings',
    algorithm: 'lzma',
    level: 9,
    content: 'Maximum compression test with complex patterns. '.repeat(150) + 
             'Additional data for better compression ratios. '.repeat(100),
    expectedResults: {
      minCompressionRatio: 4.0,
      maxCompressionTime: 15000,
      shouldSucceed: true
    }
  }
];

class SystemIntegrationTester {
  constructor(private page: Page) {}

  async navigateToSystem() {
    await this.page.goto('http://localhost:8449');
    await this.page.waitForLoadState('networkidle');
    
    // Verify frontend is loaded
    await expect(this.page.locator('body')).toBeVisible();
    
    // Navigate to compression tab
    await this.page.click('[data-testid="compression-tab"]');
    await this.page.waitForSelector('[data-testid="compression-interface"]', { timeout: 10000 });
    
    // Verify compression interface is loaded
    await expect(this.page.locator('[data-testid="compression-interface"]')).toBeVisible();
  }

  async verifyBackendConnectivity() {
    // Test backend health endpoint
    const healthResponse = await this.page.request.get('http://localhost:8443/health');
    expect(healthResponse.status()).toBe(200);
    
    // Test compression API endpoint
    const compressionResponse = await this.page.request.post('http://localhost:8443/api/v1/compression/compress', {
      data: {
        content: 'Health check test',
        parameters: {
          algorithm: 'gzip',
          level: 6
        }
      }
    });
    
    expect(compressionResponse.status()).toBe(200);
    const result = await compressionResponse.json();
    expect(result.success).toBe(true);
    expect(result.compressed_content).toBeTruthy();
  }

  async executeCompressionTest(testConfig: SystemIntegrationTest) {
    const startTime = Date.now();
    
    // Set algorithm
    await this.page.selectOption('[data-testid="algorithm-select"]', testConfig.algorithm);
    await this.page.waitForTimeout(300);
    
    // Set compression level
    await this.page.fill('[data-testid="compression-level"]', testConfig.level.toString());
    await this.page.waitForTimeout(300);
    
    // Input content
    await this.page.fill('[data-testid="content-input"]', testConfig.content);
    await this.page.waitForTimeout(300);
    
    // Trigger compression
    await this.page.click('[data-testid="compress-button"]');
    await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
    
    const endTime = Date.now();
    const executionTime = endTime - startTime;
    
    // Get results
    const results = await this.page.evaluate(() => {
      const resultElement = document.querySelector('[data-testid="compression-results"]');
      return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
    });
    
    return {
      results,
      executionTime,
      testConfig
    };
  }

  async validateCompressionResults(testResult: any) {
    const { results, executionTime, testConfig } = testResult;
    
    // Verify basic structure
    expect(results).toBeTruthy();
    expect(results.success).toBe(testConfig.expectedResults.shouldSucceed);
    
    if (results.success) {
      // Verify algorithm
      expect(results.result.algorithm_used).toBe(testConfig.algorithm);
      
      // Verify compression metrics
      expect(results.result.original_size).toBe(testConfig.content.length);
      expect(results.result.compressed_size).toBeGreaterThan(0);
      expect(results.result.compression_ratio).toBeGreaterThanOrEqual(testConfig.expectedResults.minCompressionRatio);
      
      // Verify execution time
      expect(executionTime).toBeLessThan(testConfig.expectedResults.maxCompressionTime);
      
      // Verify compressed content
      expect(results.compressed_content).toBeTruthy();
      expect(results.compressed_content).toMatch(/^[A-Za-z0-9+/]*={0,2}$/);
      
      // Log performance metrics
      console.log(`${testConfig.name}:`, {
        algorithm: testConfig.algorithm,
        level: testConfig.level,
        originalSize: results.result.original_size,
        compressedSize: results.result.compressed_size,
        ratio: results.result.compression_ratio.toFixed(2),
        percentage: results.result.compression_percentage.toFixed(2),
        executionTime: executionTime,
        compressionTime: results.result.compression_time
      });
    } else {
      // Verify error handling
      expect(results.message).toContain('error');
      console.log(`${testConfig.name} failed:`, results.message);
    }
  }

  async testConcurrentSystemLoad() {
    const concurrentTests = 5;
    const testContent = 'Concurrent system load test. '.repeat(100);
    
    const startTime = Date.now();
    const promises = Array.from({ length: concurrentTests }, async (_, index) => {
      const context = await this.page.context().newPage();
      const tester = new SystemIntegrationTester(context);
      
      try {
        await tester.navigateToSystem();
        const testConfig: SystemIntegrationTest = {
          name: `Concurrent Test ${index + 1}`,
          description: 'Concurrent system load test',
          algorithm: ['gzip', 'bzip2', 'lz4', 'zstd', 'lzma'][index],
          level: 6,
          content: testContent,
          expectedResults: {
            minCompressionRatio: 1.5,
            maxCompressionTime: 15000,
            shouldSucceed: true
          }
        };
        
        return await tester.executeCompressionTest(testConfig);
      } finally {
        await context.close();
      }
    });
    
    const results = await Promise.all(promises);
    const endTime = Date.now();
    const totalTime = endTime - startTime;
    
    // Verify all concurrent operations completed
    expect(results).toHaveLength(concurrentTests);
    
    for (const result of results) {
      expect(result.results.success).toBe(true);
      expect(result.results.compressed_content).toBeTruthy();
    }
    
    console.log(`Concurrent system load test: ${concurrentTests} operations in ${totalTime}ms (avg: ${totalTime / concurrentTests}ms per operation)`);
    
    return results;
  }

  async testSystemResilience() {
    const resilienceTests = [
      {
        name: 'Empty Content',
        content: '',
        shouldSucceed: false
      },
      {
        name: 'Very Large Content',
        content: 'Large content test. '.repeat(10000),
        shouldSucceed: true
      },
      {
        name: 'Special Characters',
        content: 'Special chars: \x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F',
        shouldSucceed: true
      },
      {
        name: 'Unicode Content',
        content: 'Unicode test: 世界 🌍 ñáéíóú العربية русский',
        shouldSucceed: true
      },
      {
        name: 'Invalid Level',
        content: 'Test content',
        level: 999,
        shouldSucceed: false
      }
    ];
    
    const resilienceResults = [];
    
    for (const test of resilienceTests) {
      await this.page.selectOption('[data-testid="algorithm-select"]', 'gzip');
      await this.page.fill('[data-testid="compression-level"]', (test.level || 6).toString());
      await this.page.fill('[data-testid="content-input"]', test.content);
      await this.page.waitForTimeout(300);
      
      await this.page.click('[data-testid="compress-button"]');
      await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
      
      const results = await this.page.evaluate(() => {
        const resultElement = document.querySelector('[data-testid="compression-results"]');
        return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
      });
      
      resilienceResults.push({
        test: test.name,
        expectedSuccess: test.shouldSucceed,
        actualSuccess: results?.success || false,
        hasError: !results?.success,
        errorMessage: results?.message
      });
    }
    
    // Verify resilience
    for (const result of resilienceResults) {
      if (result.expectedSuccess) {
        expect(result.actualSuccess).toBe(true);
      } else {
        expect(result.hasError).toBe(true);
      }
    }
    
    console.log('System resilience test results:', resilienceResults);
    return resilienceResults;
  }
}

// System Integration Test Suite
test.describe('System Integration Tests', () => {
  let tester: SystemIntegrationTester;

  test.beforeEach(async ({ page }) => {
    tester = new SystemIntegrationTester(page);
    await tester.navigateToSystem();
  });

  test.describe('System Health and Connectivity', () => {
    test('should verify system connectivity', async () => {
      await tester.verifyBackendConnectivity();
    });

    test('should handle system startup gracefully', async () => {
      // Verify all UI elements are present
      await expect(tester.page.locator('[data-testid="algorithm-select"]')).toBeVisible();
      await expect(tester.page.locator('[data-testid="compression-level"]')).toBeVisible();
      await expect(tester.page.locator('[data-testid="content-input"]')).toBeVisible();
      await expect(tester.page.locator('[data-testid="compress-button"]')).toBeVisible();
    });
  });

  test.describe('End-to-End Compression Tests', () => {
    for (const testConfig of SYSTEM_INTEGRATION_TESTS) {
      test(`should handle ${testConfig.name}`, async () => {
        const testResult = await tester.executeCompressionTest(testConfig);
        await tester.validateCompressionResults(testResult);
      });
    }
  });

  test.describe('System Performance', () => {
    test('should handle concurrent system load', async () => {
      const concurrentResults = await tester.testConcurrentSystemLoad();
      
      // Verify all concurrent operations completed successfully
      expect(concurrentResults).toHaveLength(5);
      for (const result of concurrentResults) {
        expect(result.results.success).toBe(true);
      }
    });

    test('should maintain performance under load', async () => {
      const startTime = Date.now();
      
      // Run multiple compression operations
      const operations = 10;
      const promises = Array.from({ length: operations }, async (_, index) => {
        const testConfig: SystemIntegrationTest = {
          name: `Load Test ${index + 1}`,
          description: 'Performance load test',
          algorithm: 'gzip',
          level: 6,
          content: `Load test content ${index}. `.repeat(50),
          expectedResults: {
            minCompressionRatio: 1.5,
            maxCompressionTime: 5000,
            shouldSucceed: true
          }
        };
        
        return await tester.executeCompressionTest(testConfig);
      });
      
      const results = await Promise.all(promises);
      const endTime = Date.now();
      const totalTime = endTime - startTime;
      
      // Verify performance is acceptable
      expect(totalTime).toBeLessThan(60000); // 1 minute for 10 operations
      expect(results).toHaveLength(operations);
      
      for (const result of results) {
        expect(result.results.success).toBe(true);
      }
      
      console.log(`Performance test: ${operations} operations in ${totalTime}ms (avg: ${totalTime / operations}ms per operation)`);
    });
  });

  test.describe('System Resilience', () => {
    test('should handle edge cases gracefully', async () => {
      const resilienceResults = await tester.testSystemResilience();
      
      // Verify system handled edge cases appropriately
      expect(resilienceResults).toHaveLength(5);
      
      for (const result of resilienceResults) {
        if (result.expectedSuccess) {
          expect(result.actualSuccess).toBe(true);
        } else {
          expect(result.hasError).toBe(true);
        }
      }
    });

    test('should recover from errors', async () => {
      // Test error recovery by running valid operation after invalid one
      await tester.page.fill('[data-testid="compression-level"]', '999'); // Invalid level
      await tester.page.fill('[data-testid="content-input"]', 'Test content');
      await tester.page.click('[data-testid="compress-button"]');
      await tester.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
      
      // Now run valid operation
      await tester.page.fill('[data-testid="compression-level"]', '6'); // Valid level
      await tester.page.fill('[data-testid="content-input"]', 'Valid test content');
      await tester.page.click('[data-testid="compress-button"]');
      await tester.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
      
      const results = await tester.page.evaluate(() => {
        const resultElement = document.querySelector('[data-testid="compression-results"]');
        return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
      });
      
      // Should succeed after error recovery
      expect(results.success).toBe(true);
      expect(results.compressed_content).toBeTruthy();
    });
  });

  test.describe('Data Integrity', () => {
    test('should maintain data integrity across all operations', async () => {
      const testContent = 'Data integrity test content. '.repeat(100);
      const algorithms = ['gzip', 'bzip2', 'lz4', 'zstd', 'lzma'];
      
      const integrityResults = [];
      
      for (const algorithm of algorithms) {
        await tester.page.selectOption('[data-testid="algorithm-select"]', algorithm);
        await tester.page.fill('[data-testid="compression-level"]', '6');
        await tester.page.fill('[data-testid="content-input"]', testContent);
        await tester.page.waitForTimeout(300);
        
        await tester.page.click('[data-testid="compress-button"]');
        await tester.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
        
        const results = await tester.page.evaluate(() => {
          const resultElement = document.querySelector('[data-testid="compression-results"]');
          return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
        });
        
        integrityResults.push({
          algorithm,
          success: results.success,
          originalSize: results.result?.original_size,
          compressedSize: results.result?.compressed_size,
          ratio: results.result?.compression_ratio,
          hasCompressedContent: !!results.compressed_content
        });
      }
      
      // Verify data integrity across all algorithms
      for (const result of integrityResults) {
        expect(result.success).toBe(true);
        expect(result.originalSize).toBe(testContent.length);
        expect(result.compressedSize).toBeGreaterThan(0);
        expect(result.ratio).toBeGreaterThan(1);
        expect(result.hasCompressedContent).toBe(true);
      }
      
      console.log('Data integrity test results:', integrityResults);
    });
  });
});
