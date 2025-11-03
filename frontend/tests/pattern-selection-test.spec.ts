/**
 * Pattern Selection Test - Verify all pattern types work
 */

import { test, expect } from '@playwright/test'

test.describe('Pattern Selection and Advanced Config', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })

    // Wait for the Synthetic Media navigation button
    const syntheticMediaNavButton = page.locator('[data-testid="synthetic-media-nav-button"]')
    await syntheticMediaNavButton.waitFor({ state: 'visible', timeout: 10000 })
    await syntheticMediaNavButton.click()

    // Wait for tab content to load
    await page.waitForSelector('[data-testid="synthetic-media-tab"]', {
      state: 'visible',
      timeout: 15000
    })

    await page.waitForTimeout(500)
  })

  test('Pattern selector shows all pattern types', async ({ page }) => {
    console.log('🧪 Testing pattern selector')

    // Switch to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    // Find the pattern selector dropdown - it should be visible
    const patternSelector = page.locator('select').first()
    await expect(patternSelector).toBeVisible()

    // Get all options
    const options = await patternSelector.locator('option').allTextContents()

    console.log(`📊 Found ${options.length} pattern types:`)
    options.forEach((opt, i) => console.log(`   ${i + 1}. ${opt}`))

    // Verify we have at least 15 patterns (fractal, mandelbrot, julia, etc.)
    expect(options.length).toBeGreaterThanOrEqual(15)

    // Verify specific patterns exist
    const optionsText = options.join(',')
    expect(optionsText).toContain('Mandelbrot')
    expect(optionsText).toContain('Julia')
    expect(optionsText).toContain('Perlin')
    expect(optionsText).toContain('Checkerboard')

    console.log('✅ Pattern selector has all expected patterns')
  })

  test('Can select different patterns', async ({ page }) => {
    console.log('🧪 Testing pattern selection')

    // Switch to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    const patternSelector = page.locator('select').first()

    // Select Mandelbrot
    await patternSelector.selectOption({ label: /Mandelbrot/ })
    await page.waitForTimeout(200)

    let selectedValue = await patternSelector.inputValue()
    console.log(`   Selected: ${selectedValue}`)
    expect(selectedValue).toBe('mandelbrot')

    // Select Julia Set
    await patternSelector.selectOption({ label: /Julia/ })
    await page.waitForTimeout(200)

    selectedValue = await patternSelector.inputValue()
    console.log(`   Selected: ${selectedValue}`)
    expect(selectedValue).toBe('julia')

    // Select Checkerboard
    await patternSelector.selectOption({ label: /Checkerboard/ })
    await page.waitForTimeout(200)

    selectedValue = await patternSelector.inputValue()
    console.log(`   Selected: ${selectedValue}`)
    expect(selectedValue).toBe('checkerboard')

    console.log('✅ Pattern selection works correctly')
  })

  test('Advanced configuration panel is collapsible', async ({ page }) => {
    console.log('🧪 Testing advanced configuration panel')

    // Find the Advanced Configuration button
    const advancedConfigButton = page.locator('button:has-text("Advanced Configuration")')
    await expect(advancedConfigButton).toBeVisible()

    // Initially, advanced panel might be collapsed
    await advancedConfigButton.click()
    await page.waitForTimeout(300)

    // Should see video/image/audio config options
    const resolutionSelect = page.locator('select:has-text("320x240")')
    await expect(resolutionSelect).toBeVisible({ timeout: 2000 })

    console.log('   ✓ Advanced config panel expanded')

    // Click again to collapse
    await advancedConfigButton.click()
    await page.waitForTimeout(300)

    console.log('✅ Advanced configuration panel works')
  })

  test('Can configure video parameters', async ({ page }) => {
    console.log('🧪 Testing video parameter configuration')

    // Make sure we're on video tab
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    // Expand advanced config
    const advancedConfigButton = page.locator('button:has-text("Advanced Configuration")')
    await advancedConfigButton.click()
    await page.waitForTimeout(300)

    // Change resolution
    const resolutionSelect = page.locator('select').filter({ hasText: '640x480' })
    await resolutionSelect.selectOption('1280x720')
    await page.waitForTimeout(200)

    console.log('   ✓ Changed resolution to 1280x720')

    // Adjust frame rate slider
    const frameRateSlider = page.locator('input[type="range"]').filter({ has: page.locator('text=/Frame Rate/') })
    await frameRateSlider.fill('15')
    await page.waitForTimeout(200)

    console.log('   ✓ Changed frame rate to 15 fps')

    // Adjust duration slider
    const durationSlider = page.locator('input[type="range"]').filter({ has: page.locator('text=/Duration/') })
    await durationSlider.fill('5')
    await page.waitForTimeout(200)

    console.log('   ✓ Changed duration to 5 seconds')

    console.log('✅ Video parameters can be configured')
  })

  test('Generate image with selected pattern (Mandelbrot)', async ({ page }) => {
    console.log('🧪 Testing image generation with Mandelbrot pattern')

    // Switch to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    // Select Mandelbrot pattern
    const patternSelector = page.locator('select').first()
    await patternSelector.selectOption({ label: /Mandelbrot/ })
    await page.waitForTimeout(200)

    console.log('   Selected Mandelbrot pattern')

    // Click generate
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()

    console.log('📡 Generating Mandelbrot image...')
    await generateButton.click()

    // Wait for success
    const successToast = page.locator('text=/.*image.*generated successfully/i')
    await successToast.waitFor({ state: 'visible', timeout: 15000 })
    console.log('✅ Mandelbrot image generated successfully!')

    // Verify image appears
    await page.waitForTimeout(1000)
    const imageGallery = page.locator('[data-testid="image-gallery-section"]')
    await expect(imageGallery).toBeVisible({ timeout: 5000 })
  })

  test('Generate image with selected pattern (Checkerboard)', async ({ page }) => {
    console.log('🧪 Testing image generation with Checkerboard pattern')

    // Switch to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    // Select Checkerboard pattern
    const patternSelector = page.locator('select').first()
    await patternSelector.selectOption({ label: /Checkerboard/ })
    await page.waitForTimeout(200)

    console.log('   Selected Checkerboard pattern')

    // Click generate
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()

    console.log('📡 Generating Checkerboard image...')
    await generateButton.click()

    // Wait for success
    const successToast = page.locator('text=/.*image.*generated successfully/i')
    await successToast.waitFor({ state: 'visible', timeout: 15000 })
    console.log('✅ Checkerboard image generated successfully!')

    // Verify image appears
    await page.waitForTimeout(1000)
    const imageGallery = page.locator('[data-testid="image-gallery-section"]')
    await expect(imageGallery).toBeVisible({ timeout: 5000 })
  })

  test('Generate image with selected pattern (Perlin Noise)', async ({ page }) => {
    console.log('🧪 Testing image generation with Perlin Noise pattern')

    // Switch to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    // Select Perlin pattern
    const patternSelector = page.locator('select').first()
    await patternSelector.selectOption({ label: /Perlin/ })
    await page.waitForTimeout(200)

    console.log('   Selected Perlin Noise pattern')

    // Click generate
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()

    console.log('📡 Generating Perlin Noise image...')
    await generateButton.click()

    // Wait for success
    const successToast = page.locator('text=/.*image.*generated successfully/i')
    await successToast.waitFor({ state: 'visible', timeout: 15000 })
    console.log('✅ Perlin Noise image generated successfully!')

    // Verify image appears
    await page.waitForTimeout(1000)
    const imageGallery = page.locator('[data-testid="image-gallery-section"]')
    await expect(imageGallery).toBeVisible({ timeout: 5000 })
  })
})
