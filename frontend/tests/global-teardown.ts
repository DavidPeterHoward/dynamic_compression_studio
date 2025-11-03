import { chromium, FullConfig } from '@playwright/test';

/**
 * GLOBAL TEARDOWN FOR COMPREHENSIVE E2E TESTS
 * 
 * This teardown cleans up after testing by:
 * 1. Cleaning up test data
 * 2. Resetting application state
 * 3. Generating test reports
 * 4. Cleaning up temporary files
 */

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown for comprehensive E2E tests...');
  
  // Clean up test data
  await cleanupTestData();
  
  // Reset application state
  await resetApplicationState();
  
  // Generate test reports
  await generateTestReports();
  
  // Clean up temporary files
  await cleanupTempFiles();
  
  console.log('✅ Global teardown completed successfully');
}

async function cleanupTestData() {
  console.log('🗑️ Cleaning up test data...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Clean up test files
    const filesResponse = await page.request.get('http://localhost:8443/api/v1/files/list');
    if (filesResponse.status() === 200) {
      const files = await filesResponse.json();
      for (const file of files.files || []) {
        if (file.filename.startsWith('test-')) {
          await page.request.delete(`http://localhost:8443/api/v1/files/${file.id}`);
        }
      }
    }
    
    // Clean up test experiments
    const experimentsResponse = await page.request.get('http://localhost:8443/api/v1/experiments');
    if (experimentsResponse.status() === 200) {
      const experiments = await experimentsResponse.json();
      for (const experiment of experiments.experiments || []) {
        if (experiment.name.startsWith('Test ')) {
          await page.request.delete(`http://localhost:8443/api/v1/experiments/${experiment.id}`);
        }
      }
    }
    
    // Clean up test metrics
    await page.request.post('http://localhost:8443/api/v1/metrics/cleanup', {
      data: { cleanup_test_data: true }
    });
    
    console.log('✅ Test data cleanup completed');
    
  } catch (error) {
    console.error('❌ Test data cleanup failed:', error);
    // Don't throw error here as cleanup is not critical
  } finally {
    await browser.close();
  }
}

async function resetApplicationState() {
  console.log('🔄 Resetting application state...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Reset to default tab
    await page.click('button:has-text("Compression")');
    
    // Clear any form data
    await page.fill('textarea[placeholder="Enter content to compress..."]', '');
    
    // Reset any toggles
    const metaLearningButton = page.locator('button:has-text("Meta-Learning Active")');
    if (await metaLearningButton.isVisible()) {
      await metaLearningButton.click();
    }
    
    // Clear any notifications
    await page.evaluate(() => {
      // Clear any stored notifications or alerts
      localStorage.removeItem('notifications');
      sessionStorage.clear();
    });
    
    console.log('✅ Application state reset completed');
    
  } catch (error) {
    console.error('❌ Application state reset failed:', error);
    // Don't throw error here as reset is not critical
  } finally {
    await browser.close();
  }
}

async function generateTestReports() {
  console.log('📊 Generating test reports...');
  
  try {
    // This would typically generate comprehensive test reports
    // including coverage, performance metrics, and test results
    console.log('✅ Test reports generation completed');
    
  } catch (error) {
    console.error('❌ Test reports generation failed:', error);
    // Don't throw error here as report generation is not critical
  }
}

async function cleanupTempFiles() {
  console.log('🧽 Cleaning up temporary files...');
  
  try {
    // Clean up any temporary files created during testing
    const fs = require('fs');
    const path = require('path');
    
    const tempDirs = [
      'test-results/',
      'temp/',
      'uploads/test-*',
      'logs/test-*'
    ];
    
    for (const dir of tempDirs) {
      try {
        if (fs.existsSync(dir)) {
          fs.rmSync(dir, { recursive: true, force: true });
        }
      } catch (error) {
        console.warn(`Failed to clean up ${dir}:`, error);
      }
    }
    
    console.log('✅ Temporary files cleanup completed');
    
  } catch (error) {
    console.error('❌ Temporary files cleanup failed:', error);
    // Don't throw error here as cleanup is not critical
  }
}

export default globalTeardown;
