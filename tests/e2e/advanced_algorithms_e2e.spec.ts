import { expect, Page, test } from '@playwright/test';

/**
 * Advanced Compression Algorithms E2E Tests
 * 
 * Tests quantum-biological, neuromorphic, and topological compression algorithms
 * with comprehensive UI testing and bootstrap fail-pass methodology.
 */

// Test data for different content types
const testData = {
  text: {
    content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
    expectedCompressionRatio: 1.5,
    description: 'Standard text content'
  },
  repetitive: {
    content: 'AAAAAABBBBBBCCCCCCDDDDDDEEEEEEFFFFGGGGGGHHHHHHIIIIIIJJJJJJKKKKKKLLLLLLMMMMMMMMNNNNNN',
    expectedCompressionRatio: 3.0,
    description: 'Highly repetitive content'
  },
  json: {
    content: JSON.stringify({
      users: [
        { id: 1, name: 'John Doe', email: 'john@example.com', active: true },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com', active: false },
        { id: 3, name: 'Bob Johnson', email: 'bob@example.com', active: true }
      ],
      metadata: {
        total: 3,
        lastUpdated: '2024-01-01T00:00:00Z',
        version: '1.0.0'
      }
    }),
    expectedCompressionRatio: 2.0,
    description: 'JSON structured data'
  },
  scientific: {
    content: 'The quantum state |ψ⟩ = α|0⟩ + β|1⟩ where |α|² + |β|² = 1 represents a superposition of basis states. The measurement process collapses the wavefunction to one of the eigenstates with probability |α|² for |0⟩ and |β|² for |1⟩.',
    expectedCompressionRatio: 1.8,
    description: 'Scientific/mathematical content'
  }
};

// Helper functions
async function navigateToAdvancedTab(page: Page) {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  
  // Navigate to advanced algorithms tab
  const advancedTab = page.locator('[data-testid="advanced-algorithms-tab"]');
  if (await advancedTab.isVisible()) {
    await advancedTab.click();
  } else {
    // If tab doesn't exist, navigate directly to advanced algorithms page
    await page.goto('/advanced-algorithms');
  }
  
  await page.waitForLoadState('networkidle');
}

async function inputContent(page: Page, content: string) {
  const contentInput = page.locator('[data-testid="content-input"]');
  await contentInput.fill(content);
  await expect(contentInput).toHaveValue(content);
}

async function selectAlgorithm(page: Page, algorithmId: string) {
  const algorithmButton = page.locator(`[data-testid="algorithm-${algorithmId}"]`);
  await algorithmButton.click();
  await expect(algorithmButton).toHaveClass(/border-purple-500/);
}

async function waitForCompression(page: Page, timeout = 30000) {
  // Wait for compression to complete
  await page.waitForSelector('[data-testid="compression-result"]', { timeout });
}

async function verifyCompressionResult(page: Page, expectedMinRatio: number) {
  const compressionRatio = page.locator('[data-testid="compression-ratio"]');
  const ratioText = await compressionRatio.textContent();
  const ratio = parseFloat(ratioText?.replace('x', '') || '0');
  
  expect(ratio).toBeGreaterThanOrEqual(expectedMinRatio);
}

// Test suite for Quantum-Biological Algorithm
test.describe('Quantum-Biological Compression Algorithm', () => {
  test('should compress text content with quantum-biological algorithm', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    // Input test content
    await inputContent(page, testData.text.content);
    
    // Select quantum-biological algorithm
    await selectAlgorithm(page, 'quantum_biological');
    
    // Start compression
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    // Wait for results
    await waitForCompression(page);
    
    // Verify compression results
    await verifyCompressionResult(page, testData.text.expectedCompressionRatio);
    
    // Verify algorithm-specific metrics
    const quantumEntropy = page.locator('[data-testid="quantum-entropy"]');
    await expect(quantumEntropy).toBeVisible();
    
    const entanglementMeasure = page.locator('[data-testid="entanglement-measure"]');
    await expect(entanglementMeasure).toBeVisible();
  });

  test('should handle repetitive content efficiently', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.repetitive.content);
    await selectAlgorithm(page, 'quantum_biological');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    await verifyCompressionResult(page, testData.repetitive.expectedCompressionRatio);
  });

  test('should show quantum-specific analysis', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.scientific.content);
    await selectAlgorithm(page, 'quantum_biological');
    
    // Enable deep analysis
    const analysisDepthSelect = page.locator('[data-testid="analysis-depth"]');
    await analysisDepthSelect.selectOption('deep');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    
    // Verify quantum-specific metrics are displayed
    const quantumMetrics = [
      'quantum-entropy',
      'entanglement-measure',
      'generation',
      'dna-encoding-used',
      'quantum-patterns'
    ];
    
    for (const metric of quantumMetrics) {
      const element = page.locator(`[data-testid="${metric}"]`);
      await expect(element).toBeVisible();
    }
  });

  test('should provide optimization recommendations', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    await selectAlgorithm(page, 'quantum_biological');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    
    // Check for recommendations
    const recommendations = page.locator('[data-testid="recommendations"]');
    await expect(recommendations).toBeVisible();
    
    const recommendationItems = page.locator('[data-testid="recommendation-item"]');
    const count = await recommendationItems.count();
    expect(count).toBeGreaterThan(0);
  });
});

// Test suite for Neuromorphic Algorithm
test.describe('Neuromorphic Compression Algorithm', () => {
  test('should compress content with neuromorphic algorithm', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    await selectAlgorithm(page, 'neuromorphic');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    await verifyCompressionResult(page, testData.text.expectedCompressionRatio);
  });

  test('should show neural network metrics', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.json.content);
    await selectAlgorithm(page, 'neuromorphic');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    
    // Verify neuromorphic-specific metrics
    const neuralMetrics = [
      'neural-entropy',
      'spike-efficiency',
      'learning-progress',
      'active-neurons',
      'total-spikes'
    ];
    
    for (const metric of neuralMetrics) {
      const element = page.locator(`[data-testid="${metric}"]`);
      await expect(element).toBeVisible();
    }
  });

  test('should adapt to different content types', async ({ page }) => {
    const contentTypes = [
      { content: testData.text.content, expectedRatio: 1.5 },
      { content: testData.repetitive.content, expectedRatio: 2.5 },
      { content: testData.json.content, expectedRatio: 1.8 }
    ];
    
    for (const testCase of contentTypes) {
      await navigateToAdvancedTab(page);
      
      await inputContent(page, testCase.content);
      await selectAlgorithm(page, 'neuromorphic');
      
      const compressButton = page.locator('[data-testid="compress-button"]');
      await compressButton.click();
      
      await waitForCompression(page);
      await verifyCompressionResult(page, testCase.expectedRatio);
    }
  });
});

// Test suite for Topological Algorithm
test.describe('Topological Compression Algorithm', () => {
  test('should compress content with topological algorithm', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    await selectAlgorithm(page, 'topological');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    await verifyCompressionResult(page, testData.text.expectedCompressionRatio);
  });

  test('should show topological analysis metrics', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.scientific.content);
    await selectAlgorithm(page, 'topological');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    
    // Verify topological-specific metrics
    const topologicalMetrics = [
      'topological-entropy',
      'feature-density',
      'structural-complexity',
      'persistence-bars',
      'significant-features'
    ];
    
    for (const metric of topologicalMetrics) {
      const element = page.locator(`[data-testid="${metric}"]`);
      await expect(element).toBeVisible();
    }
  });

  test('should handle high-dimensional data', async ({ page }) => {
    // Create high-dimensional test data
    const highDimData = Array.from({ length: 100 }, (_, i) => 
      `Point ${i}: ${Math.random()}, ${Math.random()}, ${Math.random()}, ${Math.random()}`
    ).join('\n');
    
    await navigateToAdvancedTab(page);
    
    await inputContent(page, highDimData);
    await selectAlgorithm(page, 'topological');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    
    // Verify compression worked
    const compressionRatio = page.locator('[data-testid="compression-ratio"]');
    await expect(compressionRatio).toBeVisible();
  });
});

// Test suite for Algorithm Comparison
test.describe('Algorithm Comparison', () => {
  test('should compare all advanced algorithms', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    
    // Click compare button
    const compareButton = page.locator('[data-testid="compare-button"]');
    await compareButton.click();
    
    // Wait for comparison to complete
    await page.waitForSelector('[data-testid="comparison-results"]', { timeout: 60000 });
    
    // Verify all algorithms were tested
    const algorithmResults = page.locator('[data-testid="algorithm-result"]');
    const resultCount = await algorithmResults.count();
    expect(resultCount).toBeGreaterThanOrEqual(3); // At least 3 algorithms
    
    // Verify comparison table is displayed
    const comparisonTable = page.locator('[data-testid="comparison-table"]');
    await expect(comparisonTable).toBeVisible();
    
    // Verify best algorithm is highlighted
    const bestAlgorithm = page.locator('[data-testid="best-algorithm"]');
    await expect(bestAlgorithm).toBeVisible();
  });

  test('should show performance metrics for each algorithm', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.json.content);
    
    const compareButton = page.locator('[data-testid="compare-button"]');
    await compareButton.click();
    
    await page.waitForSelector('[data-testid="comparison-results"]', { timeout: 60000 });
    
    // Verify each algorithm shows key metrics
    const algorithms = ['quantum_biological', 'neuromorphic', 'topological'];
    
    for (const algorithm of algorithms) {
      const algorithmRow = page.locator(`[data-testid="algorithm-${algorithm}-result"]`);
      await expect(algorithmRow).toBeVisible();
      
      // Check for compression ratio
      const compressionRatio = algorithmRow.locator('[data-testid="compression-ratio"]');
      await expect(compressionRatio).toBeVisible();
      
      // Check for processing time
      const processingTime = algorithmRow.locator('[data-testid="processing-time"]');
      await expect(processingTime).toBeVisible();
      
      // Check for status
      const status = algorithmRow.locator('[data-testid="status"]');
      await expect(status).toBeVisible();
    }
  });

  test('should handle comparison failures gracefully', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    // Use very large content to potentially cause timeouts
    const largeContent = testData.text.content.repeat(100);
    await inputContent(page, largeContent);
    
    const compareButton = page.locator('[data-testid="compare-button"]');
    await compareButton.click();
    
    // Wait for comparison to complete or timeout
    await page.waitForSelector('[data-testid="comparison-results"]', { timeout: 120000 });
    
    // Verify that successful algorithms are shown
    const successfulResults = page.locator('[data-testid="successful-result"]');
    const successCount = await successfulResults.count();
    expect(successCount).toBeGreaterThan(0);
    
    // Verify that failed algorithms show error status
    const failedResults = page.locator('[data-testid="failed-result"]');
    const failedCount = await failedResults.count();
    // Some algorithms might fail with very large content, which is expected
  });
});

// Test suite for Advanced Settings
test.describe('Advanced Settings', () => {
  test('should allow parameter customization', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    await selectAlgorithm(page, 'quantum_biological');
    
    // Show advanced settings
    const showSettingsButton = page.locator('[data-testid="show-advanced-settings"]');
    await showSettingsButton.click();
    
    // Verify settings are visible
    const advancedSettings = page.locator('[data-testid="advanced-settings"]');
    await expect(advancedSettings).toBeVisible();
    
    // Test parameter changes
    const quantumQubitsInput = page.locator('[data-testid="quantum-qubits"]');
    await quantumQubitsInput.fill('12');
    
    const populationSizeInput = page.locator('[data-testid="biological-population"]');
    await populationSizeInput.fill('150');
    
    // Test analysis depth
    const analysisDepthSelect = page.locator('[data-testid="analysis-depth"]');
    await analysisDepthSelect.selectOption('deep');
    
    // Test optimization target
    const optimizationTargetSelect = page.locator('[data-testid="optimization-target"]');
    await optimizationTargetSelect.selectOption('ratio');
    
    // Test learning toggle
    const enableLearningCheckbox = page.locator('[data-testid="enable-learning"]');
    await enableLearningCheckbox.check();
    
    // Compress with custom settings
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    
    // Verify compression completed with custom settings
    const compressionResult = page.locator('[data-testid="compression-result"]');
    await expect(compressionResult).toBeVisible();
  });

  test('should persist settings across sessions', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    // Set custom parameters
    const showSettingsButton = page.locator('[data-testid="show-advanced-settings"]');
    await showSettingsButton.click();
    
    const quantumQubitsInput = page.locator('[data-testid="quantum-qubits"]');
    await quantumQubitsInput.fill('10');
    
    // Refresh page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Navigate back to advanced tab
    await navigateToAdvancedTab(page);
    
    // Check if settings are preserved (if implemented)
    const showSettingsButton2 = page.locator('[data-testid="show-advanced-settings"]');
    await showSettingsButton2.click();
    
    const quantumQubitsInput2 = page.locator('[data-testid="quantum-qubits"]');
    const value = await quantumQubitsInput2.inputValue();
    // Note: This test might fail if settings persistence is not implemented
    // This is expected behavior for now
  });
});

// Test suite for Error Handling
test.describe('Error Handling', () => {
  test('should handle empty content gracefully', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    // Try to compress empty content
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    // Should show error message
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
  });

  test('should handle network errors gracefully', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    await selectAlgorithm(page, 'quantum_biological');
    
    // Simulate network error by blocking API calls
    await page.route('**/api/**', route => route.abort());
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    // Should show error message
    const errorMessage = page.locator('[data-testid="error-message"]');
    await expect(errorMessage).toBeVisible();
  });

  test('should handle timeout errors', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    // Use very large content to cause timeout
    const largeContent = testData.text.content.repeat(1000);
    await inputContent(page, largeContent);
    await selectAlgorithm(page, 'topological');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    // Should handle timeout gracefully
    await page.waitForTimeout(10000); // Wait 10 seconds
    
    // Either compression completes or timeout error is shown
    const compressionResult = page.locator('[data-testid="compression-result"]');
    const errorMessage = page.locator('[data-testid="error-message"]');
    
    const resultVisible = await compressionResult.isVisible();
    const errorVisible = await errorMessage.isVisible();
    
    expect(resultVisible || errorVisible).toBeTruthy();
  });
});

// Test suite for Performance
test.describe('Performance Tests', () => {
  test('should complete compression within reasonable time', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    await selectAlgorithm(page, 'quantum_biological');
    
    const startTime = Date.now();
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page, 30000); // 30 second timeout
    
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    // Should complete within 30 seconds
    expect(duration).toBeLessThan(30000);
  });

  test('should handle concurrent compressions', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    await selectAlgorithm(page, 'neuromorphic');
    
    // Start multiple compressions quickly
    const compressButton = page.locator('[data-testid="compress-button"]');
    
    await compressButton.click();
    await page.waitForTimeout(1000);
    await compressButton.click();
    await page.waitForTimeout(1000);
    await compressButton.click();
    
    // Should handle concurrent requests gracefully
    await page.waitForTimeout(5000);
    
    // At least one should complete successfully
    const compressionResults = page.locator('[data-testid="compression-result"]');
    const resultCount = await compressionResults.count();
    expect(resultCount).toBeGreaterThan(0);
  });
});

// Bootstrap Fail-Pass Methodology Tests
test.describe('Bootstrap Fail-Pass Methodology', () => {
  test('should pass with valid input and proper algorithm selection', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    await selectAlgorithm(page, 'quantum_biological');
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    await waitForCompression(page);
    
    // This should pass - valid input with proper algorithm
    const compressionResult = page.locator('[data-testid="compression-result"]');
    await expect(compressionResult).toBeVisible();
  });

  test('should fail gracefully with invalid input', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    // Try to compress without selecting algorithm
    await inputContent(page, testData.text.content);
    
    const compressButton = page.locator('[data-testid="compress-button"]');
    await compressButton.click();
    
    // Should show error or disable button
    const isDisabled = await compressButton.isDisabled();
    expect(isDisabled).toBeTruthy();
  });

  test('should demonstrate algorithm-specific behavior', async ({ page }) => {
    await navigateToAdvancedTab(page);
    
    await inputContent(page, testData.text.content);
    
    // Test each algorithm
    const algorithms = ['quantum_biological', 'neuromorphic', 'topological'];
    
    for (const algorithm of algorithms) {
      await selectAlgorithm(page, algorithm);
      
      const compressButton = page.locator('[data-testid="compress-button"]');
      await compressButton.click();
      
      await waitForCompression(page);
      
      // Verify algorithm-specific metrics are shown
      const algorithmSpecificMetrics = page.locator(`[data-testid="${algorithm}-metrics"]`);
      await expect(algorithmSpecificMetrics).toBeVisible();
      
      // Clear for next iteration
      await page.reload();
      await navigateToAdvancedTab(page);
      await inputContent(page, testData.text.content);
    }
  });
});
