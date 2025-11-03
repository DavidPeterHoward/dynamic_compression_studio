/**
 * Live Integration Proof Test
 * Tests actual media generation with real backend, verifies:
 * - Files are created and accessible (not 404)
 * - Images/videos contain actual colors (not black)
 * - Complete data pipeline from generation to display
 */

import { test, expect } from '@playwright/test'
import { PNG } from 'pngjs'

interface ColorStats {
  avgR: number
  avgG: number
  avgB: number
  isBlack: boolean
  hasColor: boolean
  variance: number
}

function analyzePNGColors(buffer: Buffer): ColorStats {
  const png = PNG.sync.read(buffer)

  let sumR = 0, sumG = 0, sumB = 0
  let minR = 255, minG = 255, minB = 255
  let maxR = 0, maxG = 0, maxB = 0
  let nonBlackPixels = 0
  let totalPixels = 0

  // Sample pixels for performance
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
    isBlack: avgR < 5 && avgG < 5 && avgB < 5,
    hasColor: nonBlackPixels > totalPixels * 0.5,
    variance
  }
}

test.describe('Live Integration Proof', () => {
  test.setTimeout(120000) // 2 minutes for real generation

  test('should generate image with colors and verify no 404', async ({ page }) => {
    console.log('\n🎨 Testing Image Generation with Color Verification...')

    await page.goto('http://localhost:8449')

    // Navigate to Synthetic Media
    await page.click('button:has-text("Synthetic Media")')
    await page.waitForSelector('[data-testid="synthetic-media-tab"]')

    // Navigate to Images
    await page.click('[data-testid="image-tab"]')
    await page.waitForTimeout(500)

    // Generate image
    console.log('  📤 Triggering image generation...')
    await page.click('[data-testid="generate-button"]')

    // Wait for generation (real backend takes time)
    await page.waitForTimeout(5000)

    // Wait for image card
    const imageCard = page.locator('[data-testid="image-card-0"]')
    await expect(imageCard).toBeVisible({ timeout: 15000 })
    console.log('  ✅ Image card appeared')

    // Get image URL
    const imgElement = imageCard.locator('img').first()
    await expect(imgElement).toBeVisible()

    const imgSrc = await imgElement.getAttribute('src')
    console.log(`  🔗 Image URL: ${imgSrc}`)

    // Verify it's not a data URL or placeholder
    expect(imgSrc).toMatch(/\/media\/(images|thumbnails)\//)

    // Test 1: Verify file is accessible (not 404)
    console.log('  🌐 Checking file accessibility...')
    const response = await page.request.get(`http://localhost:8449${imgSrc}`)

    console.log(`  📊 Response status: ${response.status()}`)
    expect(response.status()).toBe(200)
    expect(response.ok()).toBeTruthy()
    console.log('  ✅ File is accessible (not 404)')

    // Test 2: Verify file has content
    const imageBuffer = await response.body()
    console.log(`  📦 File size: ${imageBuffer.length} bytes`)
    expect(imageBuffer.length).toBeGreaterThan(1000)
    console.log('  ✅ File has content')

    // Test 3: Color analysis
    console.log('  🎨 Analyzing pixel colors...')
    const colorStats = analyzePNGColors(imageBuffer)

    console.log(`  📈 Color Analysis:`)
    console.log(`     Average RGB: (${colorStats.avgR.toFixed(1)}, ${colorStats.avgG.toFixed(1)}, ${colorStats.avgB.toFixed(1)})`)
    console.log(`     Variance: ${colorStats.variance.toFixed(2)}`)
    console.log(`     Is Black: ${colorStats.isBlack}`)
    console.log(`     Has Color: ${colorStats.hasColor}`)

    expect(colorStats.isBlack).toBe(false)
    expect(colorStats.hasColor).toBe(true)
    expect(colorStats.avgR).toBeGreaterThan(10)
    expect(colorStats.avgG).toBeGreaterThan(10)
    expect(colorStats.avgB).toBeGreaterThan(10)
    expect(colorStats.variance).toBeGreaterThan(50)

    console.log('  ✅ Image has verified color content')

    // Screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/live-image-proof.png',
      fullPage: true
    })

    console.log('✨ Image test PASSED\n')
  })

  test('should generate video and verify no 404', async ({ page }) => {
    console.log('\n🎬 Testing Video Generation and Accessibility...')

    await page.goto('http://localhost:8449')

    await page.click('button:has-text("Synthetic Media")')
    await page.waitForSelector('[data-testid="synthetic-media-tab"]')

    await page.click('[data-testid="video-tab"]')
    await page.waitForTimeout(500)

    console.log('  📤 Triggering video generation...')
    await page.click('[data-testid="generate-button"]')

    // Videos take longer
    await page.waitForTimeout(10000)

    const videoPlayer = page.locator('[data-testid="video-player"]')
    await expect(videoPlayer).toBeVisible({ timeout: 20000 })
    console.log('  ✅ Video player appeared')

    const videoSrc = await videoPlayer.getAttribute('src')
    console.log(`  🔗 Video URL: ${videoSrc}`)

    expect(videoSrc).toMatch(/\/media\/videos\//)

    // Test 1: Verify file is accessible
    console.log('  🌐 Checking video file accessibility...')
    const response = await page.request.get(`http://localhost:8449${videoSrc}`)

    console.log(`  📊 Response status: ${response.status()}`)
    expect(response.status()).toBe(200)
    expect(response.ok()).toBeTruthy()
    console.log('  ✅ Video file is accessible (not 404)')

    // Test 2: Verify file size
    const videoBuffer = await response.body()
    console.log(`  📦 Video file size: ${videoBuffer.length} bytes`)
    expect(videoBuffer.length).toBeGreaterThan(10000)
    console.log('  ✅ Video has content')

    // Test 3: Verify video metadata loads
    const hasMetadata = await videoPlayer.evaluate((video: HTMLVideoElement) => {
      return video.readyState >= 1 // HAVE_METADATA
    })
    expect(hasMetadata).toBe(true)
    console.log('  ✅ Video metadata loaded')

    // Screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/live-video-proof.png',
      fullPage: true
    })

    console.log('✨ Video test PASSED\n')
  })

  test('should generate audio and verify no 404', async ({ page }) => {
    console.log('\n🎵 Testing Audio Generation and Accessibility...')

    await page.goto('http://localhost:8449')

    await page.click('button:has-text("Synthetic Media")')
    await page.waitForSelector('[data-testid="synthetic-media-tab"]')

    await page.click('[data-testid="audio-tab"]')
    await page.waitForTimeout(500)

    console.log('  📤 Triggering audio generation...')
    await page.click('[data-testid="generate-button"]')

    await page.waitForTimeout(5000)

    const audioPlayer = page.locator('[data-testid="audio-element"]')
    await expect(audioPlayer).toBeVisible({ timeout: 15000 })
    console.log('  ✅ Audio player appeared')

    const audioSrc = await audioPlayer.getAttribute('src')
    console.log(`  🔗 Audio URL: ${audioSrc}`)

    expect(audioSrc).toMatch(/\/media\/audio\//)

    // Test 1: Verify file is accessible
    console.log('  🌐 Checking audio file accessibility...')
    const response = await page.request.get(`http://localhost:8449${audioSrc}`)

    console.log(`  📊 Response status: ${response.status()}`)
    expect(response.status()).toBe(200)
    expect(response.ok()).toBeTruthy()
    console.log('  ✅ Audio file is accessible (not 404)')

    // Test 2: Verify file size
    const audioBuffer = await response.body()
    console.log(`  📦 Audio file size: ${audioBuffer.length} bytes`)
    expect(audioBuffer.length).toBeGreaterThan(1000)
    console.log('  ✅ Audio has content')

    // Screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/live-audio-proof.png',
      fullPage: true
    })

    console.log('✨ Audio test PASSED\n')
  })

  test('E2E: Generate all media types and verify complete pipeline', async ({ page }) => {
    console.log('\n🚀 Complete E2E Pipeline Test...')

    await page.goto('http://localhost:8449')
    await page.click('button:has-text("Synthetic Media")')
    await page.waitForSelector('[data-testid="synthetic-media-tab"]')

    // Test Image
    console.log('  1️⃣ Testing Image Pipeline...')
    await page.click('[data-testid="image-tab"]')
    await page.click('[data-testid="generate-button"]')
    await page.waitForTimeout(5000)

    const imageCard = page.locator('[data-testid="image-card-0"]')
    await expect(imageCard).toBeVisible({ timeout: 15000 })

    const imgSrc = await imageCard.locator('img').first().getAttribute('src')
    const imgResponse = await page.request.get(`http://localhost:8449${imgSrc}`)
    expect(imgResponse.status()).toBe(200)

    const imgBuffer = await imgResponse.body()
    const imgColors = analyzePNGColors(imgBuffer)
    expect(imgColors.hasColor).toBe(true)
    console.log(`     ✅ Image: ${imgBuffer.length} bytes, RGB(${imgColors.avgR.toFixed(0)}, ${imgColors.avgG.toFixed(0)}, ${imgColors.avgB.toFixed(0)})`)

    // Test Video
    console.log('  2️⃣ Testing Video Pipeline...')
    await page.click('[data-testid="video-tab"]')
    await page.click('[data-testid="generate-button"]')
    await page.waitForTimeout(10000)

    const videoPlayer = page.locator('[data-testid="video-player"]')
    await expect(videoPlayer).toBeVisible({ timeout: 20000 })

    const videoSrc = await videoPlayer.getAttribute('src')
    const videoResponse = await page.request.get(`http://localhost:8449${videoSrc}`)
    expect(videoResponse.status()).toBe(200)

    const videoBuffer = await videoResponse.body()
    expect(videoBuffer.length).toBeGreaterThan(10000)
    console.log(`     ✅ Video: ${videoBuffer.length} bytes`)

    // Test Audio
    console.log('  3️⃣ Testing Audio Pipeline...')
    await page.click('[data-testid="audio-tab"]')
    await page.click('[data-testid="generate-button"]')
    await page.waitForTimeout(5000)

    const audioPlayer = page.locator('[data-testid="audio-element"]')
    await expect(audioPlayer).toBeVisible({ timeout: 15000 })

    const audioSrc = await audioPlayer.getAttribute('src')
    const audioResponse = await page.request.get(`http://localhost:8449${audioSrc}`)
    expect(audioResponse.status()).toBe(200)

    const audioBuffer = await audioResponse.body()
    expect(audioBuffer.length).toBeGreaterThan(1000)
    console.log(`     ✅ Audio: ${audioBuffer.length} bytes`)

    // Final screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/live-e2e-complete.png',
      fullPage: true
    })

    console.log('✨ Complete E2E Pipeline test PASSED\n')
  })
})
