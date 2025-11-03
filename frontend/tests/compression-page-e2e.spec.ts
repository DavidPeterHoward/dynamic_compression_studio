import { expect, test } from '@playwright/test'

test.describe('Compression Page E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the compression page
    await page.goto('http://localhost:8449/')
    
    // Wait for the page to load
    await page.waitForLoadState('networkidle')
  })

  test('should load the compression page successfully', async ({ page }) => {
    // Check if the main compression interface is visible
    await expect(page.locator('text=Enhanced Compression')).toBeVisible()
    
    // Check if the input area is present
    await expect(page.locator('textarea[placeholder*="Enter your content"]')).toBeVisible()
    
    // Check if the compress button is present
    await expect(page.locator('button:has-text("Compress Content")')).toBeVisible()
  })

  test('should have auto-optimization disabled by default', async ({ page }) => {
    // Check that auto-optimization toggle is OFF by default
    const toggle = page.locator('[data-testid="auto-optimization-toggle"]')
    await expect(toggle).toBeVisible()
    
    // Check that the toggle shows OFF state
    await expect(page.locator('text=OFF')).toBeVisible()
    
    // Check that the button text shows "Compress Content" (not "Optimize & Compress")
    await expect(page.locator('button:has-text("Compress Content")')).toBeVisible()
  })

  test('should allow toggling auto-optimization', async ({ page }) => {
    // Click the auto-optimization toggle
    await page.locator('[data-testid="auto-optimization-toggle"]').click()
    
    // Check that the toggle shows ON state
    await expect(page.locator('text=ON')).toBeVisible()
    
    // Check that the button text changes to "Optimize & Compress"
    await expect(page.locator('button:has-text("Optimize & Compress")')).toBeVisible()
    
    // Toggle back to OFF
    await page.locator('[data-testid="auto-optimization-toggle"]').click()
    
    // Check that it's back to OFF
    await expect(page.locator('text=OFF')).toBeVisible()
    await expect(page.locator('button:has-text("Compress Content")')).toBeVisible()
  })

  test('should perform basic compression without auto-optimization', async ({ page }) => {
    // Enter test content
    const testContent = 'This is a test content for compression. It contains some repetitive text that should compress well.'
    await page.fill('textarea[placeholder*="Enter your content"]', testContent)
    
    // Wait for content analysis (if any)
    await page.waitForTimeout(1000)
    
    // Click compress button
    await page.click('button:has-text("Compress Content")')
    
    // Wait for compression to complete
    await page.waitForSelector('[data-testid="compression-results"]', { timeout: 10000 })
    
    // Check that results are displayed
    await expect(page.locator('[data-testid="compression-results"]')).toBeVisible()
    
    // Check for compression metrics
    await expect(page.locator('text=Compression Ratio')).toBeVisible()
    await expect(page.locator('text=Space Saved')).toBeVisible()
  })

  test('should perform compression with auto-optimization enabled', async ({ page }) => {
    // Enable auto-optimization
    await page.locator('[data-testid="auto-optimization-toggle"]').click()
    
    // Enter test content
    const testContent = 'This is a test content for compression. It contains some repetitive text that should compress well.'
    await page.fill('textarea[placeholder*="Enter your content"]', testContent)
    
    // Wait for content analysis
    await page.waitForTimeout(1000)
    
    // Click optimize & compress button
    await page.click('button:has-text("Optimize & Compress")')
    
    // Wait for optimization to complete
    await page.waitForSelector('[data-testid="optimization-results"]', { timeout: 15000 })
    
    // Check that optimization results are displayed
    await expect(page.locator('[data-testid="optimization-results"]')).toBeVisible()
    
    // Check for optimization metrics
    await expect(page.locator('text=Optimization Results')).toBeVisible()
  })

  test('should display algorithm selection', async ({ page }) => {
    // Enter test content
    const testContent = 'This is a test content for compression.'
    await page.fill('textarea[placeholder*="Enter your content"]', testContent)
    
    // Wait for content analysis
    await page.waitForTimeout(1000)
    
    // Check that algorithm selection is visible
    await expect(page.locator('text=Algorithm Selection')).toBeVisible()
    
    // Check for algorithm options
    await expect(page.locator('text=GZIP')).toBeVisible()
    await expect(page.locator('text=ZSTD')).toBeVisible()
    await expect(page.locator('text=LZ4')).toBeVisible()
  })

  test('should show real-time metrics', async ({ page }) => {
    // Check that metrics section is visible
    await expect(page.locator('text=Real-time Metrics')).toBeVisible()
    
    // Check for performance metrics
    await expect(page.locator('text=CPU Usage')).toBeVisible()
    await expect(page.locator('text=Memory Usage')).toBeVisible()
    await expect(page.locator('text=Compression Speed')).toBeVisible()
  })

  test('should handle content analysis', async ({ page }) => {
    // Enter test content
    const testContent = 'This is a test content for compression analysis.'
    await page.fill('textarea[placeholder*="Enter your content"]', testContent)
    
    // Wait for content analysis to complete
    await page.waitForTimeout(2000)
    
    // Check that content analysis results are displayed
    await expect(page.locator('text=Content Analysis')).toBeVisible()
    
    // Check for analysis metrics
    await expect(page.locator('text=Content Type')).toBeVisible()
    await expect(page.locator('text=Entropy')).toBeVisible()
    await expect(page.locator('text=Compressibility')).toBeVisible()
  })

  test('should display compression history', async ({ page }) => {
    // Perform a compression first
    const testContent = 'This is a test content for compression.'
    await page.fill('textarea[placeholder*="Enter your content"]', testContent)
    await page.click('button:has-text("Compress Content")')
    await page.waitForSelector('[data-testid="compression-results"]', { timeout: 10000 })
    
    // Check that history is displayed
    await expect(page.locator('text=Compression History')).toBeVisible()
    
    // Check for history entries
    await expect(page.locator('[data-testid="compression-history"]')).toBeVisible()
  })

  test('should handle error states gracefully', async ({ page }) => {
    // Try to compress empty content
    await page.click('button:has-text("Compress Content")')
    
    // Check for error message or validation
    await expect(page.locator('text=Please enter content to compress')).toBeVisible()
  })

  test('should support different content types', async ({ page }) => {
    // Test with JSON content
    const jsonContent = JSON.stringify({ test: 'data', number: 123, array: [1, 2, 3] })
    await page.fill('textarea[placeholder*="Enter your content"]', jsonContent)
    await page.click('button:has-text("Compress Content")')
    await page.waitForSelector('[data-testid="compression-results"]', { timeout: 10000 })
    
    // Check that JSON content is detected
    await expect(page.locator('text=JSON')).toBeVisible()
    
    // Test with text content
    await page.fill('textarea[placeholder*="Enter your content"]', 'This is plain text content for compression.')
    await page.click('button:has-text("Compress Content")')
    await page.waitForSelector('[data-testid="compression-results"]', { timeout: 10000 })
    
    // Check that text content is detected
    await expect(page.locator('text=Text')).toBeVisible()
  })

  test('should display performance metrics correctly', async ({ page }) => {
    // Perform compression
    const testContent = 'This is a test content for compression performance testing.'
    await page.fill('textarea[placeholder*="Enter your content"]', testContent)
    await page.click('button:has-text("Compress Content")')
    await page.waitForSelector('[data-testid="compression-results"]', { timeout: 10000 })
    
    // Check for performance metrics
    await expect(page.locator('text=Processing Time')).toBeVisible()
    await expect(page.locator('text=Compression Speed')).toBeVisible()
    await expect(page.locator('text=Quality Score')).toBeVisible()
  })

  test('should support algorithm comparison', async ({ page }) => {
    // Enable auto-optimization to get algorithm comparison
    await page.locator('[data-testid="auto-optimization-toggle"]').click()
    
    // Enter test content
    const testContent = 'This is a test content for algorithm comparison.'
    await page.fill('textarea[placeholder*="Enter your content"]', testContent)
    await page.click('button:has-text("Optimize & Compress")')
    await page.waitForSelector('[data-testid="optimization-results"]', { timeout: 15000 })
    
    // Check for algorithm comparison results
    await expect(page.locator('text=Algorithm Comparison')).toBeVisible()
    await expect(page.locator('text=Best Algorithm')).toBeVisible()
  })
})

