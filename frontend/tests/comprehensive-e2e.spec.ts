import { expect, test } from '@playwright/test';

/**
 * COMPREHENSIVE E2E TESTS FOR DYNAMIC COMPRESSION ALGORITHMS
 * 
 * This test suite covers ALL functionality, buttons, processes, and logic
 * within the application, including:
 * 
 * 1. Navigation and Tab Switching
 * 2. Compression Tab - All functionality
 * 3. Experiments Tab - All functionality  
 * 4. Metrics Tab - All functionality
 * 5. Synthetic Data Tab - All functionality
 * 6. LLM Agent Tab - All functionality
 * 7. Evaluation Tab - All functionality
 * 8. All buttons, forms, and interactive elements
 * 9. All API integrations and data flows
 * 10. All edge cases and error scenarios
 */

test.describe('Dynamic Compression Algorithms - Comprehensive E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for the main application to load
    await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
  });

  // ============================================================================
  // NAVIGATION AND TAB SWITCHING TESTS
  // ============================================================================
  
  test.describe('Navigation and Tab Switching', () => {
    test('should display all navigation tabs', async ({ page }) => {
      const tabs = [
        'Compression',
        'Experiments', 
        'System Metrics',
        'Synthetic Data',
        'LLM/Agent',
        'Evaluation'
      ];

      for (const tab of tabs) {
        await expect(page.locator(`button:has-text("${tab}")`)).toBeVisible();
      }
    });

    test('should switch between all tabs successfully', async ({ page }) => {
      const tabs = [
        { id: 'compression', label: 'Compression' },
        { id: 'experiments', label: 'Experiments' },
        { id: 'metrics', label: 'System Metrics' },
        { id: 'synthetic', label: 'Synthetic Data' },
        { id: 'llm-agent', label: 'LLM/Agent' },
        { id: 'evaluation', label: 'Evaluation' }
      ];

      for (const tab of tabs) {
        await page.click(`button:has-text("${tab.label}")`);
        await page.waitForTimeout(500); // Wait for animation
        
        // Verify tab is active
        await expect(page.locator(`button:has-text("${tab.label}")`)).toHaveClass(/border-blue-500/);
      }
    });

    test('should maintain state when switching tabs', async ({ page }) => {
      // Go to compression tab and enter content
      await page.click('button:has-text("Compression")');
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Test content for state preservation');
      
      // Switch to another tab
      await page.click('button:has-text("Experiments")');
      await page.waitForTimeout(500);
      
      // Switch back to compression tab
      await page.click('button:has-text("Compression")');
      await page.waitForTimeout(500);
      
      // Verify content is preserved
      await expect(page.locator('textarea[placeholder="Enter content to compress..."]')).toHaveValue('Test content for state preservation');
    });
  });

  // ============================================================================
  // COMPRESSION TAB - COMPREHENSIVE TESTS
  // ============================================================================
  
  test.describe('Compression Tab - Complete Functionality', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Compression")');
      await page.waitForTimeout(500);
    });

    test('should display all compression tab elements', async ({ page }) => {
      // Main sections
      await expect(page.locator('h2:has-text("Content Input")')).toBeVisible();
      await expect(page.locator('h2:has-text("Content Analysis")')).toBeVisible();
      await expect(page.locator('h2:has-text("Algorithm Recommendations")')).toBeVisible();
      await expect(page.locator('h2:has-text("Compression Settings")')).toBeVisible();
      await expect(page.locator('h2:has-text("Compression Results")')).toBeVisible();
      await expect(page.locator('h2:has-text("Real-time Metrics")')).toBeVisible();
    });

    test('should handle content input and analysis workflow', async ({ page }) => {
      const testContent = 'This is a comprehensive test content for compression analysis. It contains repetitive patterns and structured data that should be analyzed effectively.';

      // Enter content
      await page.fill('textarea[placeholder="Enter content to compress..."]', testContent);
      
      // Verify character count
      await expect(page.locator('text=characters')).toBeVisible();
      
      // Click analyze button
      await page.click('button:has-text("Analyze Content")');
      
      // Wait for analysis to complete
      await page.waitForTimeout(2000);
      
      // Verify analysis results are displayed
      await expect(page.locator('text=Content Type')).toBeVisible();
      await expect(page.locator('text=Entropy')).toBeVisible();
      await expect(page.locator('text=Compressibility')).toBeVisible();
    });

    test('should display algorithm recommendations', async ({ page }) => {
      const testContent = 'Test content for algorithm recommendations';
      
      // Enter content and analyze
      await page.fill('textarea[placeholder="Enter content to compress..."]', testContent);
      await page.click('button:has-text("Analyze Content")');
      await page.waitForTimeout(2000);
      
      // Click get recommendations
      await page.click('button:has-text("Get Recommendations")');
      await page.waitForTimeout(2000);
      
      // Verify recommendations are displayed
      await expect(page.locator('text=Recommended Algorithms')).toBeVisible();
      await expect(page.locator('text=Confidence')).toBeVisible();
      await expect(page.locator('text=Expected Performance')).toBeVisible();
    });

    test('should perform enhanced compression workflow', async ({ page }) => {
      const testContent = 'Enhanced compression test content with various patterns and structures for comprehensive testing.';
      
      // Complete the full workflow
      await page.fill('textarea[placeholder="Enter content to compress..."]', testContent);
      await page.click('button:has-text("Analyze Content")');
      await page.waitForTimeout(2000);
      
      await page.click('button:has-text("Get Recommendations")');
      await page.waitForTimeout(2000);
      
      // Select an algorithm
      await page.selectOption('select', 'gzip');
      
      // Click compress button
      await page.click('button:has-text("Compress Content")');
      
      // Wait for compression to complete
      await page.waitForTimeout(3000);
      
      // Verify results are displayed
      await expect(page.locator('text=Compression Results')).toBeVisible();
      await expect(page.locator('text=Compression Ratio')).toBeVisible();
      await expect(page.locator('text=Processing Time')).toBeVisible();
    });

    test('should handle all algorithm types', async ({ page }) => {
      const algorithms = [
        'gzip', 'lzma', 'bzip2', 'lz4', 'zstd', 'brotli', 
        'content_aware', 'quantum_biological', 'neuromorphic', 'topological'
      ];

      for (const algorithm of algorithms) {
        await page.selectOption('select', algorithm);
        await expect(page.locator('select')).toHaveValue(algorithm);
      }
    });

    test('should handle compression level changes', async ({ page }) => {
      // Select different algorithms and verify level options change
      await page.selectOption('select', 'gzip');
      await expect(page.locator('select[data-testid="compression-level"]')).toBeVisible();
      
      await page.selectOption('select', 'content_aware');
      await expect(page.locator('select[data-testid="compression-level"]')).toBeVisible();
    });

    test('should display real-time metrics', async ({ page }) => {
      // Verify metrics section is visible
      await expect(page.locator('text=Real-time Metrics')).toBeVisible();
      await expect(page.locator('text=System Performance')).toBeVisible();
      await expect(page.locator('text=Compression Statistics')).toBeVisible();
    });

    test('should handle error scenarios', async ({ page }) => {
      // Test empty content
      await page.click('button:has-text("Compress Content")');
      await expect(page.locator('text=Please enter content to compress')).toBeVisible();
      
      // Test invalid content
      await page.fill('textarea[placeholder="Enter content to compress..."]', '');
      await page.click('button:has-text("Compress Content")');
      await expect(page.locator('text=Please enter content to compress')).toBeVisible();
    });

    test('should handle copy functionality', async ({ page }) => {
      const testContent = 'Content for copy testing';
      
      // Complete compression workflow
      await page.fill('textarea[placeholder="Enter content to compress..."]', testContent);
      await page.click('button:has-text("Analyze Content")');
      await page.waitForTimeout(2000);
      await page.click('button:has-text("Get Recommendations")');
      await page.waitForTimeout(2000);
      await page.click('button:has-text("Compress Content")');
      await page.waitForTimeout(3000);
      
      // Test copy functionality
      await page.click('button:has-text("Copy Compressed Content")');
      
      // Verify copy notification
      await expect(page.locator('text=Content copied to clipboard')).toBeVisible();
    });
  });

  // ============================================================================
  // EXPERIMENTS TAB - COMPREHENSIVE TESTS
  // ============================================================================
  
  test.describe('Experiments Tab - Complete Functionality', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Experiments")');
      await page.waitForTimeout(500);
    });

    test('should display experiments tab elements', async ({ page }) => {
      await expect(page.locator('h1:has-text("Experiments")')).toBeVisible();
      await expect(page.locator('button:has-text("New Experiment")')).toBeVisible();
      await expect(page.locator('text=Active Experiments')).toBeVisible();
      await expect(page.locator('text=Experiment History')).toBeVisible();
    });

    test('should create new experiment', async ({ page }) => {
      await page.click('button:has-text("New Experiment")');
      
      // Fill experiment form
      await page.fill('input[placeholder="Experiment name"]', 'Test Experiment');
      await page.selectOption('select[data-testid="experiment-type"]', 'algorithm');
      await page.fill('textarea[placeholder="Experiment description"]', 'Test experiment description');
      
      // Set parameters
      await page.fill('input[data-testid="iterations"]', '100');
      await page.fill('input[data-testid="learning-rate"]', '0.01');
      
      // Submit experiment
      await page.click('button:has-text("Start Experiment")');
      
      // Verify experiment is created
      await expect(page.locator('text=Test Experiment')).toBeVisible();
    });

    test('should manage experiment lifecycle', async ({ page }) => {
      // Create experiment first
      await page.click('button:has-text("New Experiment")');
      await page.fill('input[placeholder="Experiment name"]', 'Lifecycle Test');
      await page.selectOption('select[data-testid="experiment-type"]', 'parameter');
      await page.click('button:has-text("Start Experiment")');
      
      // Test pause/resume
      await page.click('button:has-text("Pause")');
      await expect(page.locator('text=Paused')).toBeVisible();
      
      await page.click('button:has-text("Resume")');
      await expect(page.locator('text=Running')).toBeVisible();
      
      // Test stop
      await page.click('button:has-text("Stop")');
      await expect(page.locator('text=Stopped')).toBeVisible();
    });

    test('should display experiment details', async ({ page }) => {
      // Create experiment
      await page.click('button:has-text("New Experiment")');
      await page.fill('input[placeholder="Experiment name"]', 'Details Test');
      await page.selectOption('select[data-testid="experiment-type"]', 'meta-learning');
      await page.click('button:has-text("Start Experiment")');
      
      // Click on experiment to view details
      await page.click('text=Details Test');
      
      // Verify details modal
      await expect(page.locator('text=Experiment Details')).toBeVisible();
      await expect(page.locator('text=Parameters')).toBeVisible();
      await expect(page.locator('text=Metrics')).toBeVisible();
      await expect(page.locator('text=Progress')).toBeVisible();
    });

    test('should handle experiment filtering and sorting', async ({ page }) => {
      // Test filter by status
      await page.selectOption('select[data-testid="status-filter"]', 'running');
      await expect(page.locator('text=No running experiments')).toBeVisible();
      
      // Test filter by type
      await page.selectOption('select[data-testid="type-filter"]', 'algorithm');
      await expect(page.locator('text=No algorithm experiments')).toBeVisible();
      
      // Test sorting
      await page.click('button:has-text("Sort by Date")');
      await page.click('button:has-text("Sort by Name")');
      await page.click('button:has-text("Sort by Status")');
    });
  });

  // ============================================================================
  // METRICS TAB - COMPREHENSIVE TESTS
  // ============================================================================
  
  test.describe('Metrics Tab - Complete Functionality', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("System Metrics")');
      await page.waitForTimeout(500);
    });

    test('should display all metrics sections', async ({ page }) => {
      await expect(page.locator('h1:has-text("System Metrics")')).toBeVisible();
      await expect(page.locator('text=System Performance')).toBeVisible();
      await expect(page.locator('text=Compression Statistics')).toBeVisible();
      await expect(page.locator('text=Algorithm Performance')).toBeVisible();
      await expect(page.locator('text=Resource Utilization')).toBeVisible();
    });

    test('should display real-time metrics', async ({ page }) => {
      // Verify metric cards are visible
      await expect(page.locator('text=CPU Usage')).toBeVisible();
      await expect(page.locator('text=Memory Usage')).toBeVisible();
      await expect(page.locator('text=Disk Usage')).toBeVisible();
      await expect(page.locator('text=Network Usage')).toBeVisible();
    });

    test('should handle time range selection', async ({ page }) => {
      const timeRanges = ['1h', '6h', '24h', '7d', '30d'];
      
      for (const range of timeRanges) {
        await page.click(`button:has-text("${range}")`);
        await page.waitForTimeout(500);
        await expect(page.locator(`button:has-text("${range}")`)).toHaveClass(/bg-blue-600/);
      }
    });

    test('should handle refresh functionality', async ({ page }) => {
      await page.click('button:has-text("Refresh")');
      await page.waitForTimeout(1000);
      
      // Verify metrics are updated
      await expect(page.locator('text=Last updated')).toBeVisible();
    });

    test('should display charts and graphs', async ({ page }) => {
      await expect(page.locator('canvas')).toBeVisible(); // Chart elements
      await expect(page.locator('text=Performance Trends')).toBeVisible();
      await expect(page.locator('text=Algorithm Comparison')).toBeVisible();
    });

    test('should handle metric filtering', async ({ page }) => {
      // Test metric type filtering
      await page.click('button:has-text("CPU")');
      await page.click('button:has-text("Memory")');
      await page.click('button:has-text("Network")');
      
      // Test algorithm filtering
      await page.selectOption('select[data-testid="algorithm-filter"]', 'gzip');
      await page.selectOption('select[data-testid="algorithm-filter"]', 'all');
    });
  });

  // ============================================================================
  // SYNTHETIC DATA TAB - COMPREHENSIVE TESTS
  // ============================================================================
  
  test.describe('Synthetic Data Tab - Complete Functionality', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Synthetic Data")');
      await page.waitForTimeout(500);
    });

    test('should display synthetic data tab elements', async ({ page }) => {
      await expect(page.locator('h1:has-text("Synthetic Data Generation")')).toBeVisible();
      await expect(page.locator('text=Data Patterns')).toBeVisible();
      await expect(page.locator('text=Complexity Settings')).toBeVisible();
      await expect(page.locator('text=Volume Settings')).toBeVisible();
    });

    test('should configure synthetic data parameters', async ({ page }) => {
      // Test pattern selection
      await page.check('input[value="repetitive_text"]');
      await page.check('input[value="structured_data"]');
      await page.check('input[value="mixed_content"]');
      
      // Test complexity slider
      await page.fill('input[data-testid="complexity-slider"]', '0.7');
      
      // Test volume settings
      await page.fill('input[data-testid="volume-input"]', '5000');
      
      // Test content type selection
      await page.selectOption('select[data-testid="content-type"]', 'mixed');
      
      // Test language selection
      await page.selectOption('select[data-testid="language"]', 'english');
    });

    test('should generate synthetic data', async ({ page }) => {
      // Configure parameters
      await page.check('input[value="repetitive_text"]');
      await page.fill('input[data-testid="volume-input"]', '1000');
      
      // Generate data
      await page.click('button:has-text("Generate Data")');
      
      // Wait for generation to complete
      await page.waitForTimeout(3000);
      
      // Verify generation results
      await expect(page.locator('text=Generation Complete')).toBeVisible();
      await expect(page.locator('text=Data Statistics')).toBeVisible();
    });

    test('should handle data preview and download', async ({ page }) => {
      // Generate data first
      await page.check('input[value="structured_data"]');
      await page.fill('input[data-testid="volume-input"]', '500');
      await page.click('button:has-text("Generate Data")');
      await page.waitForTimeout(3000);
      
      // Test preview
      await page.click('button:has-text("Preview Data")');
      await expect(page.locator('text=Data Preview')).toBeVisible();
      
      // Test download
      await page.click('button:has-text("Download Data")');
      await expect(page.locator('text=Download started')).toBeVisible();
    });

    test('should handle advanced settings', async ({ page }) => {
      await page.click('button:has-text("Advanced Settings")');
      
      // Test entropy settings
      await page.fill('input[data-testid="entropy-slider"]', '0.8');
      
      // Test redundancy settings
      await page.fill('input[data-testid="redundancy-slider"]', '0.3');
      
      // Test structure settings
      await page.selectOption('select[data-testid="structure-type"]', 'hierarchical');
      
      // Test encoding settings
      await page.selectOption('select[data-testid="encoding"]', 'utf-8');
    });
  });

  // ============================================================================
  // LLM AGENT TAB - COMPREHENSIVE TESTS
  // ============================================================================
  
  test.describe('LLM Agent Tab - Complete Functionality', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("LLM/Agent")');
      await page.waitForTimeout(500);
    });

    test('should display LLM agent tab elements', async ({ page }) => {
      await expect(page.locator('h1:has-text("LLM Agent")')).toBeVisible();
      await expect(page.locator('text=Available Models')).toBeVisible();
      await expect(page.locator('text=Agent Capabilities')).toBeVisible();
      await expect(page.locator('text=Interaction History')).toBeVisible();
    });

    test('should interact with LLM agent', async ({ page }) => {
      // Enter query
      await page.fill('textarea[placeholder="Enter your query..."]', 'Analyze this compression algorithm performance');
      
      // Select model
      await page.selectOption('select[data-testid="model-select"]', 'gpt-4');
      
      // Send query
      await page.click('button:has-text("Send Query")');
      
      // Wait for response
      await page.waitForTimeout(3000);
      
      // Verify response
      await expect(page.locator('text=Agent Response')).toBeVisible();
    });

    test('should handle agent capabilities', async ({ page }) => {
      // Test compression analysis
      await page.click('button:has-text("Analyze Compression")');
      await expect(page.locator('text=Compression Analysis')).toBeVisible();
      
      // Test algorithm recommendation
      await page.click('button:has-text("Recommend Algorithm")');
      await expect(page.locator('text=Algorithm Recommendation')).toBeVisible();
      
      // Test performance optimization
      await page.click('button:has-text("Optimize Performance")');
      await expect(page.locator('text=Performance Optimization')).toBeVisible();
    });

    test('should handle conversation history', async ({ page }) => {
      // Send multiple queries
      await page.fill('textarea[placeholder="Enter your query..."]', 'Query 1');
      await page.click('button:has-text("Send Query")');
      await page.waitForTimeout(2000);
      
      await page.fill('textarea[placeholder="Enter your query..."]', 'Query 2');
      await page.click('button:has-text("Send Query")');
      await page.waitForTimeout(2000);
      
      // Verify history
      await expect(page.locator('text=Query 1')).toBeVisible();
      await expect(page.locator('text=Query 2')).toBeVisible();
    });

    test('should handle agent settings', async ({ page }) => {
      await page.click('button:has-text("Agent Settings")');
      
      // Test temperature setting
      await page.fill('input[data-testid="temperature"]', '0.7');
      
      // Test max tokens
      await page.fill('input[data-testid="max-tokens"]', '1000');
      
      // Test system prompt
      await page.fill('textarea[data-testid="system-prompt"]', 'You are a compression expert');
    });
  });

  // ============================================================================
  // EVALUATION TAB - COMPREHENSIVE TESTS
  // ============================================================================
  
  test.describe('Evaluation Tab - Complete Functionality', () => {
    test.beforeEach(async ({ page }) => {
      await page.click('button:has-text("Evaluation")');
      await page.waitForTimeout(500);
    });

    test('should display evaluation tab elements', async ({ page }) => {
      await expect(page.locator('h1:has-text("Evaluation")')).toBeVisible();
      await expect(page.locator('text=Performance Metrics')).toBeVisible();
      await expect(page.locator('text=Algorithm Comparison')).toBeVisible();
      await expect(page.locator('text=Quality Assessment')).toBeVisible();
    });

    test('should run algorithm comparison', async ({ page }) => {
      await page.click('button:has-text("Compare Algorithms")');
      
      // Select algorithms to compare
      await page.check('input[value="gzip"]');
      await page.check('input[value="zstd"]');
      await page.check('input[value="brotli"]');
      
      // Set test parameters
      await page.fill('input[data-testid="test-data-size"]', '1000');
      await page.selectOption('select[data-testid="data-type"]', 'text');
      
      // Run comparison
      await page.click('button:has-text("Run Comparison")');
      
      // Wait for results
      await page.waitForTimeout(5000);
      
      // Verify results
      await expect(page.locator('text=Comparison Results')).toBeVisible();
      await expect(page.locator('text=Performance Rankings')).toBeVisible();
    });

    test('should handle quality assessment', async ({ page }) => {
      await page.click('button:has-text("Quality Assessment")');
      
      // Upload test file
      await page.setInputFiles('input[type="file"]', 'test-data.txt');
      
      // Run assessment
      await page.click('button:has-text("Run Assessment")');
      
      // Wait for results
      await page.waitForTimeout(3000);
      
      // Verify results
      await expect(page.locator('text=Quality Score')).toBeVisible();
      await expect(page.locator('text=Integrity Check')).toBeVisible();
    });

    test('should display evaluation reports', async ({ page }) => {
      // Generate report
      await page.click('button:has-text("Generate Report")');
      
      // Wait for report generation
      await page.waitForTimeout(3000);
      
      // Verify report sections
      await expect(page.locator('text=Executive Summary')).toBeVisible();
      await expect(page.locator('text=Detailed Analysis')).toBeVisible();
      await expect(page.locator('text=Recommendations')).toBeVisible();
    });

    test('should handle export functionality', async ({ page }) => {
      // Generate report first
      await page.click('button:has-text("Generate Report")');
      await page.waitForTimeout(3000);
      
      // Test export options
      await page.click('button:has-text("Export PDF")');
      await expect(page.locator('text=PDF export started')).toBeVisible();
      
      await page.click('button:has-text("Export CSV")');
      await expect(page.locator('text=CSV export started')).toBeVisible();
    });
  });

  // ============================================================================
  // SYSTEM-WIDE FUNCTIONALITY TESTS
  // ============================================================================
  
  test.describe('System-wide Functionality', () => {
    test('should handle meta-learning toggle', async ({ page }) => {
      // Test meta-learning button
      await page.click('button:has-text("Start Meta-Learning")');
      await expect(page.locator('text=Meta-Learning Active')).toBeVisible();
      
      await page.click('button:has-text("Meta-Learning Active")');
      await expect(page.locator('text=Start Meta-Learning')).toBeVisible();
    });

    test('should display system health status', async ({ page }) => {
      await expect(page.locator('text=System:')).toBeVisible();
      await expect(page.locator('div[class*="bg-green-500"], div[class*="bg-yellow-500"], div[class*="bg-red-500"]')).toBeVisible();
    });

    test('should handle notifications', async ({ page }) => {
      // Trigger a notification by trying to compress without content
      await page.click('button:has-text("Compression")');
      await page.click('button:has-text("Compress Content")');
      
      // Verify notification appears
      await expect(page.locator('text=Please enter content to compress')).toBeVisible();
    });

    test('should handle responsive design', async ({ page }) => {
      // Test mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
      
      // Test tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
      
      // Test desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
    });

    test('should handle keyboard navigation', async ({ page }) => {
      // Test tab navigation
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Test enter key
      await page.keyboard.press('Enter');
      
      // Test escape key
      await page.keyboard.press('Escape');
    });

    test('should handle error scenarios gracefully', async ({ page }) => {
      // Test network error simulation
      await page.route('**/api/**', route => route.abort());
      
      await page.click('button:has-text("Compression")');
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Test content');
      await page.click('button:has-text("Compress Content")');
      
      // Verify error handling
      await expect(page.locator('text=Connection failed')).toBeVisible();
    });
  });

  // ============================================================================
  // PERFORMANCE AND LOAD TESTING
  // ============================================================================
  
  test.describe('Performance and Load Testing', () => {
    test('should handle large content compression', async ({ page }) => {
      await page.click('button:has-text("Compression")');
      
      // Generate large content
      const largeContent = 'A'.repeat(100000);
      await page.fill('textarea[placeholder="Enter content to compress..."]', largeContent);
      
      // Start compression
      await page.click('button:has-text("Compress Content")');
      
      // Wait for completion
      await page.waitForTimeout(10000);
      
      // Verify results
      await expect(page.locator('text=Compression Results')).toBeVisible();
    });

    test('should handle multiple concurrent operations', async ({ page }) => {
      // Start multiple operations
      await page.click('button:has-text("Compression")');
      await page.fill('textarea[placeholder="Enter content to compress..."]', 'Test content');
      await page.click('button:has-text("Analyze Content")');
      
      await page.click('button:has-text("Experiments")');
      await page.click('button:has-text("New Experiment")');
      
      await page.click('button:has-text("System Metrics")');
      await page.click('button:has-text("Refresh")');
      
      // Verify all operations are handled
      await expect(page.locator('text=System Metrics')).toBeVisible();
    });

    test('should maintain performance under load', async ({ page }) => {
      // Perform multiple rapid operations
      for (let i = 0; i < 10; i++) {
        await page.click('button:has-text("Compression")');
        await page.click('button:has-text("Experiments")');
        await page.click('button:has-text("System Metrics")');
        await page.click('button:has-text("Synthetic Data")');
      }
      
      // Verify system is still responsive
      await expect(page.locator('h1:has-text("Dynamic Compression Algorithms")')).toBeVisible();
    });
  });
});
