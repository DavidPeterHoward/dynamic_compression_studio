import { expect, test } from '@playwright/test';

test.describe('Backend API Compression Tests', () => {
  test('should test GZIP compression API', async ({ request }) => {
    const response = await request.post('http://localhost:8443/api/v1/compression/compress', {
      data: {
        content: 'This is a test string for GZIP compression. It should compress well due to repetitive patterns.',
        parameters: {
          algorithm: 'gzip',
          level: 6
        }
      }
    });

    expect(response.ok()).toBeTruthy();
    
    const result = await response.json();
    expect(result.success).toBe(true);
    expect(result.compressed_content).toBeTruthy();
    expect(result.result.algorithm_used).toBe('gzip');
    expect(result.result.compression_ratio).toBeGreaterThan(1);
    
    console.log('GZIP Test Results:', {
      originalSize: result.result.original_size,
      compressedSize: result.result.compressed_size,
      ratio: result.result.compression_ratio,
      compressedContent: result.compressed_content.substring(0, 50) + '...'
    });
  });

  test('should test BZIP2 compression API', async ({ request }) => {
    const response = await request.post('http://localhost:8443/api/v1/compression/compress', {
      data: {
        content: 'BZIP2 compression test with highly repetitive content. This should compress very well with BZIP2 algorithm.',
        parameters: {
          algorithm: 'bzip2',
          level: 6
        }
      }
    });

    expect(response.ok()).toBeTruthy();
    
    const result = await response.json();
    expect(result.success).toBe(true);
    expect(result.compressed_content).toBeTruthy();
    expect(result.result.algorithm_used).toBe('bzip2');
    expect(result.result.compression_ratio).toBeGreaterThan(1);
    
    console.log('BZIP2 Test Results:', {
      originalSize: result.result.original_size,
      compressedSize: result.result.compressed_size,
      ratio: result.result.compression_ratio,
      compressedContent: result.compressed_content.substring(0, 50) + '...'
    });
  });

  test('should test LZ4 compression API', async ({ request }) => {
    const response = await request.post('http://localhost:8443/api/v1/compression/compress', {
      data: {
        content: 'LZ4 fast compression test. LZ4 is designed for speed over compression ratio.',
        parameters: {
          algorithm: 'lz4',
          level: 3
        }
      }
    });

    expect(response.ok()).toBeTruthy();
    
    const result = await response.json();
    expect(result.success).toBe(true);
    expect(result.compressed_content).toBeTruthy();
    expect(result.result.algorithm_used).toBe('lz4');
    expect(result.result.compression_ratio).toBeGreaterThan(1);
    
    console.log('LZ4 Test Results:', {
      originalSize: result.result.original_size,
      compressedSize: result.result.compressed_size,
      ratio: result.result.compression_ratio,
      compressedContent: result.compressed_content.substring(0, 50) + '...'
    });
  });

  test('should test ZSTD compression API', async ({ request }) => {
    const response = await request.post('http://localhost:8443/api/v1/compression/compress', {
      data: {
        content: 'ZSTD compression test. ZSTD provides a good balance between speed and compression ratio.',
        parameters: {
          algorithm: 'zstd',
          level: 15
        }
      }
    });

    expect(response.ok()).toBeTruthy();
    
    const result = await response.json();
    expect(result.success).toBe(true);
    expect(result.compressed_content).toBeTruthy();
    expect(result.result.algorithm_used).toBe('zstd');
    expect(result.result.compression_ratio).toBeGreaterThan(1);
    
    console.log('ZSTD Test Results:', {
      originalSize: result.result.original_size,
      compressedSize: result.result.compressed_size,
      ratio: result.result.compression_ratio,
      compressedContent: result.compressed_content.substring(0, 50) + '...'
    });
  });

  test('should test LZMA compression API', async ({ request }) => {
    const response = await request.post('http://localhost:8443/api/v1/compression/compress', {
      data: {
        content: 'LZMA compression test. LZMA provides excellent compression ratios but is slower than other algorithms.',
        parameters: {
          algorithm: 'lzma',
          level: 9
        }
      }
    });

    expect(response.ok()).toBeTruthy();
    
    const result = await response.json();
    expect(result.success).toBe(true);
    expect(result.compressed_content).toBeTruthy();
    expect(result.result.algorithm_used).toBe('lzma');
    expect(result.result.compression_ratio).toBeGreaterThan(1);
    
    console.log('LZMA Test Results:', {
      originalSize: result.result.original_size,
      compressedSize: result.result.compressed_size,
      ratio: result.result.compression_ratio,
      compressedContent: result.compressed_content.substring(0, 50) + '...'
    });
  });

  test('should compare all compression algorithms', async ({ request }) => {
    const testContent = 'Comprehensive compression algorithm comparison test. This content will be compressed using all available algorithms to compare their performance characteristics.';
    const algorithms = ['gzip', 'bzip2', 'lz4', 'zstd', 'lzma'];
    const results = [];

    for (const algorithm of algorithms) {
      const response = await request.post('http://localhost:8443/api/v1/compression/compress', {
        data: {
          content: testContent,
          parameters: {
            algorithm: algorithm,
            level: 6
          }
        }
      });

      expect(response.ok()).toBeTruthy();
      
      const result = await response.json();
      expect(result.success).toBe(true);
      expect(result.compressed_content).toBeTruthy();
      
      results.push({
        algorithm,
        originalSize: result.result.original_size,
        compressedSize: result.result.compressed_size,
        ratio: result.result.compression_ratio,
        time: result.result.compression_time
      });
    }

    console.log('Algorithm Comparison Results:', results);
    
    // Verify all algorithms produced valid results
    expect(results).toHaveLength(5);
    
    // Find best compression ratio
    const bestRatio = Math.max(...results.map(r => r.ratio));
    const fastestTime = Math.min(...results.map(r => r.time));
    
    console.log(`Best compression ratio: ${bestRatio.toFixed(2)}`);
    console.log(`Fastest compression time: ${fastestTime.toFixed(2)}ms`);
  });

  test('should test compression with different content types', async ({ request }) => {
    const testCases = [
      {
        name: 'Text Content',
        content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(20)
      },
      {
        name: 'JSON Content',
        content: JSON.stringify({
          users: Array.from({ length: 50 }, (_, i) => ({
            id: i,
            name: `User ${i}`,
            email: `user${i}@example.com`,
            active: i % 2 === 0
          }))
        })
      },
      {
        name: 'Repetitive Content',
        content: 'The quick brown fox jumps over the lazy dog. '.repeat(30)
      }
    ];

    for (const testCase of testCases) {
      const response = await request.post('http://localhost:8443/api/v1/compression/compress', {
        data: {
          content: testCase.content,
          parameters: {
            algorithm: 'gzip',
            level: 6
          }
        }
      });

      expect(response.ok()).toBeTruthy();
      
      const result = await response.json();
      expect(result.success).toBe(true);
      expect(result.compressed_content).toBeTruthy();
      expect(result.result.original_size).toBe(testCase.content.length);
      
      console.log(`${testCase.name} Results:`, {
        originalSize: result.result.original_size,
        compressedSize: result.result.compressed_size,
        ratio: result.result.compression_ratio.toFixed(2)
      });
    }
  });
});

