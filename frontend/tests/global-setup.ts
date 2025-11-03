import { chromium, FullConfig } from '@playwright/test';

/**
 * GLOBAL SETUP FOR COMPREHENSIVE E2E TESTS
 * 
 * This setup ensures the application is ready for testing by:
 * 1. Checking service availability
 * 2. Pre-warming the application
 * 3. Setting up test data
 * 4. Configuring test environment
 */

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for comprehensive E2E tests...');
  
  // Check if services are running
  await checkServices();
  
  // Pre-warm the application
  await preWarmApplication();
  
  // Setup test data
  await setupTestData();
  
  console.log('✅ Global setup completed successfully');
}

async function checkServices() {
  console.log('🔍 Checking service availability...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Check frontend
    console.log('Checking frontend (baseURL)...');
    await page.goto('/', { timeout: 30000 });
    await page.waitForSelector('h1:has-text("Dynamic Compression Algorithms")', { timeout: 10000 });
    console.log('✅ Frontend is accessible');
    
    // Check backend health
    console.log('Checking backend health...');
    const response = await page.request.get('http://localhost:8443/health');
    if (response.status() !== 200) {
      throw new Error(`Backend health check failed: ${response.status()}`);
    }
    console.log('✅ Backend is healthy');
    
    // Check API endpoints
    console.log('Checking API endpoints...');
    const apiResponse = await page.request.get('http://localhost:8443/api/v1/compression/algorithms');
    if (apiResponse.status() !== 200) {
      throw new Error(`API endpoint check failed: ${apiResponse.status()}`);
    }
    console.log('✅ API endpoints are accessible');
    
  } catch (error) {
    console.error('❌ Service check failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

async function preWarmApplication() {
  console.log('🔥 Pre-warming application...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Test navigation between tabs
    const tabs = ['Compression', 'Experiments', 'System Metrics', 'Synthetic Data', 'LLM/Agent', 'Evaluation'];
    for (const tab of tabs) {
      await page.click(`button:has-text("${tab}")`);
      await page.waitForTimeout(1000);
    }
    
    // Test basic functionality
    await page.click('button:has-text("Compression")');
    await page.fill('textarea[placeholder="Enter content to compress..."]', 'Test content for pre-warming');
    
    console.log('✅ Application pre-warmed successfully');
    
  } catch (error) {
    console.error('❌ Pre-warming failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

async function setupTestData() {
  console.log('📊 Setting up test data...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Create test files
    const testFiles = [
      { name: 'test-small.txt', content: 'Small test file content' },
      { name: 'test-medium.txt', content: 'Medium test file content with more data to compress'.repeat(100) },
      { name: 'test-large.txt', content: 'Large test file content with extensive data for compression testing'.repeat(1000) },
      { name: 'test-json.json', content: JSON.stringify({ test: 'data', numbers: [1, 2, 3, 4, 5] }) },
      { name: 'test-xml.xml', content: '<?xml version="1.0"?><root><item>test</item></root>' }
    ];
    
    // Upload test files
    for (const file of testFiles) {
      const response = await page.request.post('http://localhost:8443/api/v1/files/upload', {
        multipart: {
          file: {
            name: file.name,
            mimeType: 'text/plain',
            buffer: Buffer.from(file.content)
          }
        }
      });
      
      if (response.status() !== 200) {
        console.warn(`Failed to upload test file: ${file.name}`);
      }
    }
    
    // Create test experiments
    const testExperiments = [
      {
        name: 'Test Algorithm Experiment',
        type: 'algorithm',
        description: 'Test experiment for algorithm comparison'
      },
      {
        name: 'Test Parameter Experiment', 
        type: 'parameter',
        description: 'Test experiment for parameter optimization'
      }
    ];
    
    for (const experiment of testExperiments) {
      const response = await page.request.post('http://localhost:8443/api/v1/experiments', {
        data: experiment
      });
      
      if (response.status() !== 200) {
        console.warn(`Failed to create test experiment: ${experiment.name}`);
      }
    }
    
    console.log('✅ Test data setup completed');
    
  } catch (error) {
    console.error('❌ Test data setup failed:', error);
    // Don't throw error here as test data setup is not critical
  } finally {
    await browser.close();
  }
}

export default globalSetup;
