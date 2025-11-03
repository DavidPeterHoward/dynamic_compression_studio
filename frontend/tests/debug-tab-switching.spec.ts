import { test, expect } from '@playwright/test'

test('Debug tab switching', async ({ page }) => {
  // Navigate
  await page.goto('http://localhost:8449')

  // Wait for page to load
  await page.waitForLoadState('networkidle')

  console.log('Page loaded')

  // Find the button
  const button = page.locator('button:has-text("Synthetic Media")')
  console.log('Looking for button...')

  await button.waitFor({ state: 'visible', timeout: 10000 })
  console.log('Button found and visible')

  // Take screenshot before click
  await page.screenshot({ path: 'test-results/before-click.png', fullPage: true })

  // Click the button
  console.log('Clicking button...')
  await button.click()
  console.log('Button clicked')

  // Wait a bit
  await page.waitForTimeout(2000)

  // Take screenshot after click
  await page.screenshot({ path: 'test-results/after-click.png', fullPage: true })

  // Check what's in the DOM
  const pageContent = await page.content()
  console.log('Checking for synthetic-media-tab in HTML...')
  console.log('Found:', pageContent.includes('synthetic-media-tab'))

  // Try to find the element
  const synthTab = page.locator('[data-testid="synthetic-media-tab"]')
  const isVisible = await synthTab.isVisible().catch(() => false)
  console.log('Is synthetic-media-tab visible?', isVisible)

  // Check what's actually rendered
  const mainContent = await page.locator('main').textContent()
  console.log('Main content includes "Compression"?', mainContent?.includes('Compression'))
  console.log('Main content includes "Synthetic Media Generation"?', mainContent?.includes('Synthetic Media Generation'))
})
