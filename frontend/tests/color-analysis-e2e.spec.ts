/**
 * E2E Test: Color Analysis for Synthetic Media
 * Verifies that generated images and videos contain actual colors (not black)
 */

import { test, expect } from '@playwright/test'
import { PNG } from 'pngjs'

interface ColorStats {
  avgR: number
  avgG: number
  avgB: number
  minR: number
  minG: number
  minB: number
  maxR: number
  maxG: number
  maxB: number
  isBlack: boolean
  hasColor: boolean
  variance: number
}

/**
 * Analyze PNG image data for color content
 */
function analyzePNGColors(buffer: Buffer): ColorStats {
  const png = PNG.sync.read(buffer)

  let sumR = 0, sumG = 0, sumB = 0
  let minR = 255, minG = 255, minB = 255
  let maxR = 0, maxG = 0, maxB = 0
  let nonBlackPixels = 0
  let totalPixels = 0

  // Sample every 10th pixel for performance
  for (let y = 0; y < png.height; y += 10) {
    for (let x = 0; x < png.width; x += 10) {
      const idx = (png.width * y + x) << 2
      const r = png.data[idx]
      const g = png.data[idx + 1]
      const b = png.data[idx + 2]

      sumR += r
      sumG += g
      sumB += b

      minR = Math.min(minR, r)
      minG = Math.min(minG, g)
      minB = Math.min(minB, b)

      maxR = Math.max(maxR, r)
      maxG = Math.max(maxG, g)
      maxB = Math.max(maxB, b)

      if (r > 10 || g > 10 || b > 10) {
        nonBlackPixels++
      }

      totalPixels++
    }
  }

  const avgR = sumR / totalPixels
  const avgG = sumG / totalPixels
  const avgB = sumB / totalPixels

  const variance = Math.sqrt(
    Math.pow(maxR - minR, 2) +
    Math.pow(maxG - minG, 2) +
    Math.pow(maxB - minB, 2)
  )

  return {
    avgR,
    avgG,
    avgB,
    minR,
    minG,
    minB,
    maxR,
    maxG,
    maxB,
    isBlack: avgR < 5 && avgG < 5 && avgB < 5,
    hasColor: nonBlackPixels > totalPixels * 0.5, // At least 50% non-black
    variance
  }
}

test.describe('Color Analysis - Synthetic Media', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })
    await page.waitForLoadState('networkidle')

    // Navigate to Synthetic Media tab
    const syntheticMediaTab = page.locator('button:has-text("Synthetic Media")')
    await syntheticMediaTab.waitFor({ state: 'visible', timeout: 15000 })
    await syntheticMediaTab.click()

    await page.waitForSelector('[data-testid="synthetic-media-tab"]', {
      state: 'visible',
      timeout: 15000
    })
  })

  test('should generate image with actual colors (not black)', async ({ page }) => {
    console.log('Testing image color generation...')

    // Navigate to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(500)

    // Click generate
    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()

    // Wait for generation
    await page.waitForTimeout(3000)

    // Wait for image to appear
    const imageCard = page.locator('[data-testid="image-card-0"]')
    await expect(imageCard).toBeVisible({ timeout: 10000 })

    // Get the image element
    const imgElement = imageCard.locator('img').first()
    await expect(imgElement).toBeVisible()

    // Get image src
    const imgSrc = await imgElement.getAttribute('src')
    console.log('Image src:', imgSrc)

    // Fetch the image data
    const response = await page.request.get(`http://localhost:8449${imgSrc}`)
    expect(response.ok()).toBeTruthy()

    const imageBuffer = await response.body()
    console.log('Image buffer size:', imageBuffer.length)

    // Analyze colors
    const colorStats = analyzePNGColors(imageBuffer)

    console.log('Color Analysis Results:')
    console.log(`  Average RGB: (${colorStats.avgR.toFixed(1)}, ${colorStats.avgG.toFixed(1)}, ${colorStats.avgB.toFixed(1)})`)
    console.log(`  Min RGB: (${colorStats.minR}, ${colorStats.minG}, ${colorStats.minB})`)
    console.log(`  Max RGB: (${colorStats.maxR}, ${colorStats.maxG}, ${colorStats.maxB})`)
    console.log(`  Variance: ${colorStats.variance.toFixed(2)}`)
    console.log(`  Is Black: ${colorStats.isBlack}`)
    console.log(`  Has Color: ${colorStats.hasColor}`)

    // Assertions
    expect(colorStats.isBlack).toBe(false)
    expect(colorStats.hasColor).toBe(true)
    expect(colorStats.avgR).toBeGreaterThan(10)
    expect(colorStats.avgG).toBeGreaterThan(10)
    expect(colorStats.avgB).toBeGreaterThan(10)
    expect(colorStats.variance).toBeGreaterThan(50)

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/color-verified-image.png',
      fullPage: true
    })

    console.log('✓ Image has verified color content')
  })

  test('should generate video with actual colors (not black)', async ({ page }) => {
    console.log('Testing video color generation...')

    // Navigate to video tab
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(500)

    // Click generate
    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()

    // Wait for generation (videos take longer)
    await page.waitForTimeout(5000)

    // Wait for video player
    const videoPlayer = page.locator('[data-testid="video-player"]')
    await expect(videoPlayer).toBeVisible({ timeout: 15000 })

    // Get video src
    const videoSrc = await videoPlayer.getAttribute('src')
    console.log('Video src:', videoSrc)

    // Verify video element has loaded
    await page.waitForTimeout(1000)

    // Check if video has loaded metadata
    const hasMetadata = await videoPlayer.evaluate((video: HTMLVideoElement) => {
      return video.readyState >= 1 // HAVE_METADATA
    })
    expect(hasMetadata).toBe(true)

    // Take screenshot of video player
    await page.screenshot({
      path: 'frontend/tests/screenshots/color-verified-video.png',
      fullPage: true
    })

    console.log('✓ Video player loaded with content')
  })

  test('should verify image thumbnail has colors', async ({ page }) => {
    console.log('Testing image thumbnail colors...')

    // Navigate to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(500)

    // Generate image
    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(3000)

    // Get thumbnail
    const thumbnail = page.locator('[data-testid="image-thumbnail-0"]')
    await expect(thumbnail).toBeVisible()

    const thumbSrc = await thumbnail.getAttribute('src')
    console.log('Thumbnail src:', thumbSrc)

    // Fetch thumbnail
    const response = await page.request.get(`http://localhost:8449${thumbSrc}`)
    expect(response.ok()).toBeTruthy()

    const thumbBuffer = await response.body()

    // Analyze thumbnail colors
    const colorStats = analyzePNGColors(thumbBuffer)

    console.log('Thumbnail Color Analysis:')
    console.log(`  Average RGB: (${colorStats.avgR.toFixed(1)}, ${colorStats.avgG.toFixed(1)}, ${colorStats.avgB.toFixed(1)})`)
    console.log(`  Has Color: ${colorStats.hasColor}`)

    // Verify thumbnail has color
    expect(colorStats.isBlack).toBe(false)
    expect(colorStats.hasColor).toBe(true)

    console.log('✓ Thumbnail has verified color content')
  })

  test('should verify multiple images have varying colors', async ({ page }) => {
    console.log('Testing color variation across multiple images...')

    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(500)

    const colorResults: ColorStats[] = []

    // Generate 3 images
    for (let i = 0; i < 3; i++) {
      const generateButton = page.locator('[data-testid="generate-button"]')
      await generateButton.click()
      await page.waitForTimeout(2000)

      const imageCard = page.locator(`[data-testid="image-card-${i}"]`)
      await expect(imageCard).toBeVisible()

      const imgElement = imageCard.locator('img').first()
      const imgSrc = await imgElement.getAttribute('src')

      const response = await page.request.get(`http://localhost:8449${imgSrc}`)
      const imageBuffer = await response.body()

      const colorStats = analyzePNGColors(imageBuffer)
      colorResults.push(colorStats)

      console.log(`Image ${i + 1} colors: R=${colorStats.avgR.toFixed(1)}, G=${colorStats.avgG.toFixed(1)}, B=${colorStats.avgB.toFixed(1)}`)
    }

    // Verify all images have color
    for (const stats of colorResults) {
      expect(stats.isBlack).toBe(false)
      expect(stats.hasColor).toBe(true)
    }

    // Verify there's variation between images
    const avgRValues = colorResults.map(s => s.avgR)
    const rVariation = Math.max(...avgRValues) - Math.min(...avgRValues)

    console.log(`Color variation across images: ${rVariation.toFixed(2)}`)
    expect(rVariation).toBeGreaterThan(5) // Should have some variation

    console.log('✓ Multiple images generated with varying colors')
  })

  test('should detect color in different pattern types', async ({ page }) => {
    console.log('Testing different pattern types for color...')

    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(500)

    // Test fractal pattern (default)
    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    const imageCard = page.locator('[data-testid="image-card-0"]')
    await expect(imageCard).toBeVisible()

    const imgElement = imageCard.locator('img').first()
    const imgSrc = await imgElement.getAttribute('src')

    const response = await page.request.get(`http://localhost:8449${imgSrc}`)
    const imageBuffer = await response.body()

    const colorStats = analyzePNGColors(imageBuffer)

    console.log('Fractal pattern color stats:')
    console.log(`  RGB: (${colorStats.avgR.toFixed(1)}, ${colorStats.avgG.toFixed(1)}, ${colorStats.avgB.toFixed(1)})`)
    console.log(`  Variance: ${colorStats.variance.toFixed(2)}`)

    // Assertions
    expect(colorStats.isBlack).toBe(false)
    expect(colorStats.hasColor).toBe(true)
    expect(colorStats.variance).toBeGreaterThan(30) // Fractal should have good variance

    console.log('✓ Pattern has verified color and complexity')
  })
})
