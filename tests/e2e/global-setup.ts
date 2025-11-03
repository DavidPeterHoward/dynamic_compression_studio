import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global test setup...');
  
  // Check if services are running
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Skip frontend check for now - focus on backend API testing
    console.log('📱 Skipping frontend service check (focusing on backend API)...');
    
    // Check backend service
    console.log('🔧 Checking backend service...');
    const backendResponse = await page.goto('http://localhost:8443/health', { timeout: 30000 });
    if (backendResponse?.status() === 200) {
      console.log('✅ Backend service is running');
    } else {
      throw new Error('Backend service is not responding');
    }
    
    // Test compression API
    console.log('🧪 Testing compression API...');
    const compressionResponse = await page.request.post('http://localhost:8443/api/v1/compression/compress', {
      data: {
        content: 'Test content for setup verification',
        parameters: {
          algorithm: 'gzip',
          level: 6
        }
      }
    });
    
    if (compressionResponse.ok()) {
      const result = await compressionResponse.json();
      if (result.success && result.compressed_content) {
        console.log('✅ Compression API is working correctly');
      } else {
        throw new Error('Compression API returned invalid response');
      }
    } else {
      throw new Error('Compression API is not responding');
    }
    
    console.log('🎉 Global setup completed successfully!');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;
