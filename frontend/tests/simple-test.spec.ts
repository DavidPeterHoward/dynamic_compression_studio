import { expect, test } from '@playwright/test'

test('simple page load test', async ({ page }) => {
  // Navigate to the page
  await page.goto('http://localhost:8449/', { waitUntil: 'domcontentloaded' })
  
  // Wait a bit for the page to load
  await page.waitForTimeout(2000)
  
  // Check if we can see any text on the page
  const bodyText = await page.textContent('body')
  console.log('Page body text:', bodyText?.substring(0, 500))
  
  // Check for specific elements
  const compressionText = await page.locator('text=Compression').count()
  const enhancedText = await page.locator('text=Enhanced').count()
  const dynamicText = await page.locator('text=Dynamic').count()
  
  console.log('Compression text count:', compressionText)
  console.log('Enhanced text count:', enhancedText)
  console.log('Dynamic text count:', dynamicText)
  
  // Just check that the page loaded
  expect(bodyText).toBeTruthy()
})
