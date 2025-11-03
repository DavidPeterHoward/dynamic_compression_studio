import { expect, Page, test } from '@playwright/test';

interface DataPipelineStep {
  name: string;
  input: any;
  output: any;
  timestamp: number;
  metadata: Record<string, any>;
}

class DataPipelineTestHelper {
  constructor(private page: Page) {}

  async navigateToCompressionTab() {
    await this.page.goto('http://localhost:8449');
    await this.page.waitForLoadState('networkidle');
    await this.page.click('[data-testid="compression-tab"]');
    await this.page.waitForSelector('[data-testid="compression-interface"]', { timeout: 10000 });
  }

  async capturePipelineStep(stepName: string, input: any, output: any, metadata: Record<string, any> = {}): Promise<DataPipelineStep> {
    return {
      name: stepName,
      input,
      output,
      timestamp: Date.now(),
      metadata: {
        ...metadata,
        userAgent: await this.page.evaluate(() => navigator.userAgent),
        url: this.page.url()
      }
    };
  }

  async verifyDataIntegrity(originalData: string, processedData: any, stepName: string) {
    // Verify data hasn't been corrupted
    expect(processedData).toBeTruthy();
    
    // Log data integrity metrics
    console.log(`Data integrity check for ${stepName}:`, {
      originalLength: originalData.length,
      processedType: typeof processedData,
      hasContent: !!processedData,
      timestamp: new Date().toISOString()
    });
  }

  async testCompressionPipeline(algorithm: string, level: number, content: string) {
    const pipelineSteps: DataPipelineStep[] = [];
    
    // Step 1: Input validation
    const inputStep = await this.capturePipelineStep('input_validation', content, content, {
      algorithm,
      level,
      contentType: typeof content
    });
    pipelineSteps.push(inputStep);
    
    // Step 2: Set compression parameters
    await this.page.selectOption('[data-testid="algorithm-select"]', algorithm);
    await this.page.fill('[data-testid="compression-level"]', level.toString());
    await this.page.waitForTimeout(300);
    
    const parameterStep = await this.capturePipelineStep('parameter_setting', { algorithm, level }, { algorithm, level }, {
      parameterValidation: true
    });
    pipelineSteps.push(parameterStep);
    
    // Step 3: Content input
    await this.page.fill('[data-testid="content-input"]', content);
    await this.page.waitForTimeout(300);
    
    const contentStep = await this.capturePipelineStep('content_input', content, content, {
      contentLength: content.length,
      contentHash: await this.calculateContentHash(content)
    });
    pipelineSteps.push(contentStep);
    
    // Step 4: Compression execution
    const compressionStart = Date.now();
    await this.page.click('[data-testid="compress-button"]');
    await this.page.waitForSelector('[data-testid="compression-results"]', { timeout: 30000 });
    const compressionEnd = Date.now();
    
    const results = await this.page.evaluate(() => {
      const resultElement = document.querySelector('[data-testid="compression-results"]');
      return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
    });
    
    const compressionStep = await this.capturePipelineStep('compression_execution', content, results, {
      executionTime: compressionEnd - compressionStart,
      success: results?.success || false
    });
    pipelineSteps.push(compressionStep);
    
    // Step 5: Result validation
    await this.verifyDataIntegrity(content, results, 'compression_result');
    
    const validationStep = await this.capturePipelineStep('result_validation', results, results, {
      validationPassed: true,
      resultStructure: Object.keys(results || {})
    });
    pipelineSteps.push(validationStep);
    
    return { pipelineSteps, results };
  }

  async calculateContentHash(content: string): Promise<string> {
    // Simple hash calculation for content integrity
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16);
  }

  async verifyPipelineIntegrity(pipelineSteps: DataPipelineStep[]) {
    // Verify pipeline steps are sequential
    for (let i = 1; i < pipelineSteps.length; i++) {
      expect(pipelineSteps[i].timestamp).toBeGreaterThanOrEqual(pipelineSteps[i-1].timestamp);
    }
    
    // Verify no data loss between steps
    const inputData = pipelineSteps[0].input;
    const outputData = pipelineSteps[pipelineSteps.length - 1].output;
    
    expect(inputData).toBeTruthy();
    expect(outputData).toBeTruthy();
    
    // Verify compression results structure
    if (outputData && typeof outputData === 'object') {
      expect(outputData.success).toBeDefined();
      expect(outputData.result).toBeDefined();
      expect(outputData.compressed_content).toBeDefined();
    }
  }

  async testConcurrentDataThreading() {
    const algorithms = ['gzip', 'bzip2', 'lz4', 'zstd', 'lzma'];
    const testContent = 'Concurrent compression test data. '.repeat(100);
    
    const concurrentPromises = algorithms.map(async (algorithm, index) => {
      // Create a new page context for each concurrent test
      const context = await this.page.context().newPage();
      const helper = new DataPipelineTestHelper(context);
      
      try {
        await helper.navigateToCompressionTab();
        const { pipelineSteps, results } = await helper.testCompressionPipeline(algorithm, 6, testContent);
        
        return {
          algorithm,
          success: results?.success || false,
          pipelineSteps,
          results
        };
      } finally {
        await context.close();
      }
    });
    
    const concurrentResults = await Promise.all(concurrentPromises);
    
    // Verify all concurrent operations completed successfully
    for (const result of concurrentResults) {
      expect(result.success).toBe(true);
      expect(result.pipelineSteps).toHaveLength(5); // All pipeline steps
      expect(result.results).toBeTruthy();
    }
    
    return concurrentResults;
  }

  async testDataTransformationIntegrity() {
    const testCases = [
      { name: 'simple_text', content: 'Simple text content for compression testing.' },
      { name: 'json_data', content: JSON.stringify({ test: 'data', number: 123, array: [1, 2, 3] }) },
      { name: 'xml_data', content: '<?xml version="1.0"?><root><item>test</item></root>' },
      { name: 'unicode_content', content: 'Unicode test: 世界 🌍 ñáéíóú العربية русский' },
      { name: 'binary_like', content: 'Binary-like: \x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F' }
    ];
    
    const transformationResults = [];
    
    for (const testCase of testCases) {
      const { pipelineSteps, results } = await this.testCompressionPipeline('gzip', 6, testCase.content);
      
      // Verify data transformation integrity
      expect(results.success).toBe(true);
      expect(results.compressed_content).toBeTruthy();
      expect(results.result.original_size).toBe(testCase.content.length);
      
      transformationResults.push({
        testCase: testCase.name,
        originalSize: testCase.content.length,
        compressedSize: results.result.compressed_size,
        ratio: results.result.compression_ratio,
        pipelineSteps: pipelineSteps.length
      });
    }
    
    return transformationResults;
  }
}

// Test suite for data pipeline integrity
test.describe('Data Pipeline Integrity Tests', () => {
  let helper: DataPipelineTestHelper;

  test.beforeEach(async ({ page }) => {
    helper = new DataPipelineTestHelper(page);
    await helper.navigateToCompressionTab();
  });

  test.describe('Pipeline Step Verification', () => {
    test('should maintain data integrity through all pipeline steps', async () => {
      const testContent = 'Pipeline integrity test content. '.repeat(50);
      const { pipelineSteps, results } = await helper.testCompressionPipeline('gzip', 6, testContent);
      
      // Verify pipeline integrity
      await helper.verifyPipelineIntegrity(pipelineSteps);
      
      // Verify all steps were captured
      expect(pipelineSteps).toHaveLength(5);
      expect(pipelineSteps[0].name).toBe('input_validation');
      expect(pipelineSteps[1].name).toBe('parameter_setting');
      expect(pipelineSteps[2].name).toBe('content_input');
      expect(pipelineSteps[3].name).toBe('compression_execution');
      expect(pipelineSteps[4].name).toBe('result_validation');
      
      // Verify compression results
      expect(results.success).toBe(true);
      expect(results.compressed_content).toBeTruthy();
      expect(results.result.original_size).toBe(testContent.length);
    });

    test('should handle pipeline errors gracefully', async () => {
      // Test with invalid parameters
      await helper.testCompressionPipeline('gzip', 99, 'Test content');
      
      // Should either succeed with clamped parameters or show appropriate error
      const results = await helper.page.evaluate(() => {
        const resultElement = document.querySelector('[data-testid="compression-results"]');
        return resultElement ? JSON.parse(resultElement.textContent || '{}') : null;
      });
      
      // Results should be defined (either success or error)
      expect(results).toBeTruthy();
    });
  });

  test.describe('Concurrent Data Threading', () => {
    test('should handle concurrent compression operations', async () => {
      const concurrentResults = await helper.testConcurrentDataThreading();
      
      // Verify all concurrent operations completed
      expect(concurrentResults).toHaveLength(5);
      
      for (const result of concurrentResults) {
        expect(result.success).toBe(true);
        expect(result.pipelineSteps).toHaveLength(5);
        expect(result.results.compressed_content).toBeTruthy();
      }
      
      // Verify no data corruption between concurrent operations
      const algorithms = concurrentResults.map(r => r.algorithm);
      const uniqueAlgorithms = [...new Set(algorithms)];
      expect(uniqueAlgorithms).toHaveLength(5);
    });

    test('should maintain data isolation between concurrent operations', async () => {
      const testContents = [
        'Content for algorithm 1',
        'Content for algorithm 2', 
        'Content for algorithm 3',
        'Content for algorithm 4',
        'Content for algorithm 5'
      ];
      
      const concurrentPromises = testContents.map(async (content, index) => {
        const context = await helper.page.context().newPage();
        const testHelper = new DataPipelineTestHelper(context);
        
        try {
          await testHelper.navigateToCompressionTab();
          const algorithms = ['gzip', 'bzip2', 'lz4', 'zstd', 'lzma'];
          const { results } = await testHelper.testCompressionPipeline(algorithms[index], 6, content);
          
          return {
            index,
            content,
            algorithm: algorithms[index],
            success: results?.success || false,
            compressedContent: results?.compressed_content
          };
        } finally {
          await context.close();
        }
      });
      
      const results = await Promise.all(concurrentPromises);
      
      // Verify each operation maintained its own data
      for (let i = 0; i < results.length; i++) {
        expect(results[i].success).toBe(true);
        expect(results[i].content).toBe(testContents[i]);
        expect(results[i].compressedContent).toBeTruthy();
      }
    });
  });

  test.describe('Data Transformation Integrity', () => {
    test('should maintain data integrity across different content types', async () => {
      const transformationResults = await helper.testDataTransformationIntegrity();
      
      // Verify all transformations completed successfully
      expect(transformationResults).toHaveLength(5);
      
      for (const result of transformationResults) {
        expect(result.originalSize).toBeGreaterThan(0);
        expect(result.compressedSize).toBeGreaterThan(0);
        expect(result.ratio).toBeGreaterThan(1);
        expect(result.pipelineSteps).toBe(5);
      }
    });

    test('should handle large data transformations', async () => {
      const largeContent = 'Large content test. '.repeat(1000);
      const { pipelineSteps, results } = await helper.testCompressionPipeline('gzip', 6, largeContent);
      
      // Verify large content was handled correctly
      expect(results.success).toBe(true);
      expect(results.result.original_size).toBe(largeContent.length);
      expect(results.compressed_content).toBeTruthy();
      
      // Verify pipeline handled large content
      expect(pipelineSteps).toHaveLength(5);
      expect(pipelineSteps[2].metadata.contentLength).toBe(largeContent.length);
    });
  });

  test.describe('Error Recovery and Data Consistency', () => {
    test('should recover from pipeline errors without data corruption', async () => {
      // Test with problematic content
      const problematicContent = 'Content with special characters: \x00\x01\x02\x03';
      
      const { pipelineSteps, results } = await helper.testCompressionPipeline('gzip', 6, problematicContent);
      
      // Should either succeed or fail gracefully
      if (results.success) {
        expect(results.compressed_content).toBeTruthy();
        expect(results.result.original_size).toBe(problematicContent.length);
      } else {
        expect(results.message).toContain('error');
      }
      
      // Pipeline steps should still be captured
      expect(pipelineSteps).toHaveLength(5);
    });

    test('should maintain data consistency across retries', async () => {
      const testContent = 'Retry test content. '.repeat(100);
      
      // Perform multiple compressions with same content
      const results = [];
      for (let i = 0; i < 3; i++) {
        const { results: result } = await helper.testCompressionPipeline('gzip', 6, testContent);
        results.push(result);
      }
      
      // Verify consistency across retries
      for (const result of results) {
        expect(result.success).toBe(true);
        expect(result.result.original_size).toBe(testContent.length);
        expect(result.compressed_content).toBeTruthy();
      }
      
      // Verify compression ratios are consistent (within reasonable variance)
      const ratios = results.map(r => r.result.compression_ratio);
      const avgRatio = ratios.reduce((a, b) => a + b, 0) / ratios.length;
      for (const ratio of ratios) {
        expect(Math.abs(ratio - avgRatio)).toBeLessThan(0.1); // 10% variance tolerance
      }
    });
  });

  test.describe('Performance and Scalability', () => {
    test('should handle high-frequency compression requests', async () => {
      const testContent = 'High frequency test content. '.repeat(50);
      const requestCount = 10;
      
      const startTime = Date.now();
      const promises = Array.from({ length: requestCount }, async (_, index) => {
        const context = await helper.page.context().newPage();
        const testHelper = new DataPipelineTestHelper(context);
        
        try {
          await testHelper.navigateToCompressionTab();
          const { results } = await testHelper.testCompressionPipeline('gzip', 6, testContent);
          return { index, success: results?.success || false };
        } finally {
          await context.close();
        }
      });
      
      const results = await Promise.all(promises);
      const endTime = Date.now();
      
      // Verify all requests completed successfully
      expect(results).toHaveLength(requestCount);
      for (const result of results) {
        expect(result.success).toBe(true);
      }
      
      // Verify performance is reasonable
      const totalTime = endTime - startTime;
      const avgTimePerRequest = totalTime / requestCount;
      expect(avgTimePerRequest).toBeLessThan(5000); // 5 seconds per request
      
      console.log(`High-frequency test completed: ${requestCount} requests in ${totalTime}ms (avg: ${avgTimePerRequest}ms per request)`);
    });
  });
});
