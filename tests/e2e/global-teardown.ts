import { chromium } from '@playwright/test';

async function globalTeardown() {
  console.log('🧹 Starting global test teardown...');
  
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Clean up any test data or resources
    console.log('🧽 Cleaning up test data...');
    
    // Check if services are still running
    const frontendResponse = await page.goto('http://localhost:8449', { timeout: 10000 }).catch(() => null);
    const backendResponse = await page.goto('http://localhost:8443/health', { timeout: 10000 }).catch(() => null);
    
    if (frontendResponse?.status() === 200) {
      console.log('✅ Frontend service is still running');
    }
    
    if (backendResponse?.status() === 200) {
      console.log('✅ Backend service is still running');
    }
    
    console.log('🎉 Global teardown completed successfully!');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  } finally {
    await browser.close();
  }
}

export default globalTeardown;
