/**
 * E2E Test: Synthetic Video Generation
 * Tests the complete workflow from configuration to video playback
 */

import { test, expect } from '@playwright/test'

test.describe('Synthetic Video Generation E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API endpoints for consistent testing
    await page.route('**/api/v1/synthetic/video/generate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          video_url: '/media/videos/test_video.mp4',
          thumbnail_url: '/media/thumbnails/test_video.jpg',
          metadata: {
            width: 1920,
            height: 1080,
            duration: 10,
            frameRate: 30,
            fileSize: 15728640,
            codec: 'h264'
          },
          analysis: {
            complexity: {
              kolmogorov: 0.595,
              structural: 0.72,
              cyclomatic: 10
            },
            entropy: {
              shannon: 0.58,
              temporal: 0.45
            },
            redundancy: {
              overall: 0.3,
              patterns: []
            },
            compressibility: {
              ratio: 2.4,
              algorithm: 'h264',
              efficiency: 0.85
            },
            steganography: {
              isSuspicious: false,
              confidence: 0.05,
              methods: []
            }
          },
          processing_time: 8.234,
          request_id: 'vid_test123'
        })
      })
    })

    // Navigate to the application
    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle')

    // Click the Synthetic Media tab
    const syntheticMediaTab = page.locator('button:has-text("Synthetic Media")')
    await syntheticMediaTab.waitFor({ state: 'visible', timeout: 15000 })
    await syntheticMediaTab.click()

    // Wait for tab content to load
    await page.waitForSelector('[data-testid="synthetic-media-tab"]', {
      state: 'visible',
      timeout: 15000
    })
  })

  test('should display synthetic media tab', async ({ page }) => {
    // Tab content already loaded by beforeEach

    const syntheticTab = page.locator('[data-testid="synthetic-media-tab"]')
    await expect(syntheticTab).toBeVisible()

    // Verify title and subtitle
    const title = page.locator('[data-testid="tab-title"]')
    await expect(title).toContainText('Synthetic Media Generation')

    const subtitle = page.locator('[data-testid="tab-subtitle"]')
    await expect(subtitle).toBeVisible()
  })

  test('should switch between media types', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Test Video tab
    const videoTab = page.locator('[data-testid="video-tab"]')
    await expect(videoTab).toBeVisible()
    await videoTab.click()
    await page.waitForTimeout(300)

    // Test Image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await expect(imageTab).toBeVisible()
    await imageTab.click()
    await page.waitForTimeout(300)

    // Test Audio tab
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await expect(audioTab).toBeVisible()
    await audioTab.click()
    await page.waitForTimeout(300)

    // Switch back to video
    await videoTab.click()
    await page.waitForTimeout(300)
  })

  test('should generate video with complete workflow', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Ensure we're on the video tab
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(500)

    // Adjust configuration sliders
    const complexitySlider = page.locator('input[type="range"]').first()
    await expect(complexitySlider).toBeVisible()

    // Click generate button
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()
    await generateButton.click()

    // Wait for API call to complete
    await page.waitForTimeout(1500)

    // Verify video player appears
    const videoPlayerSection = page.locator('[data-testid="video-player-section"]')
    await expect(videoPlayerSection).toBeVisible({ timeout: 5000 })

    // Verify video player element exists
    const videoPlayer = page.locator('[data-testid="video-player"]')
    await expect(videoPlayer).toBeVisible()

    // Take screenshot for verification
    await page.screenshot({
      path: 'frontend/tests/screenshots/video-generation-complete.png',
      fullPage: true
    })
  })

  test('should display video metadata correctly', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate a video first
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(1500)

    // Wait for video info panel
    const videoInfoPanel = page.locator('[data-testid="video-info-panel"]')
    await expect(videoInfoPanel).toBeVisible({ timeout: 5000 })

    // Verify resolution
    const resolutionValue = page.locator('[data-testid="prop-value-resolution"]')
    await expect(resolutionValue).toContainText('1920x1080')

    // Verify framerate
    const framerateValue = page.locator('[data-testid="prop-value-framerate"]')
    await expect(framerateValue).toContainText('30 fps')

    // Verify duration
    const durationValue = page.locator('[data-testid="prop-value-duration"]')
    await expect(durationValue).toContainText('10s')

    // Verify file size
    const filesizeValue = page.locator('[data-testid="prop-value-filesize"]')
    await expect(filesizeValue).toBeVisible()
  })

  test('should display analysis metrics', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate a video
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(1500)

    // Wait for video info panel
    await page.waitForSelector('[data-testid="video-info-panel"]', { timeout: 5000 })

    // Verify complexity metric
    const complexityValue = page.locator('[data-testid="metric-value-complexity"]')
    await expect(complexityValue).toBeVisible()
    await expect(complexityValue).toContainText('0.72')

    // Verify entropy metric
    const entropyValue = page.locator('[data-testid="metric-value-entropy"]')
    await expect(entropyValue).toBeVisible()
    await expect(entropyValue).toContainText('0.58')

    // Verify compressibility metric
    const compressibilityValue = page.locator('[data-testid="metric-value-compressibility"]')
    await expect(compressibilityValue).toBeVisible()
    await expect(compressibilityValue).toContainText('2.4x')
  })

  test('should toggle analysis overlay', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate a video
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(1500)

    // Wait for video player
    await page.waitForSelector('[data-testid="video-player"]', { timeout: 5000 })

    // Find analysis toggle button
    const analysisToggle = page.locator('[data-testid="analysis-toggle"]')
    await expect(analysisToggle).toBeVisible()

    // Click to show overlay
    await analysisToggle.click()
    await page.waitForTimeout(300)

    // Verify overlay is visible
    const analysisOverlay = page.locator('[data-testid="video-analysis-overlay"]')
    await expect(analysisOverlay).toBeVisible()

    // Click to hide overlay
    await analysisToggle.click()
    await page.waitForTimeout(300)

    // Verify overlay is hidden
    await expect(analysisOverlay).not.toBeVisible()

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/video-analysis-toggle.png',
      fullPage: true
    })
  })

  test('should handle video playback controls', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate a video
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(1500)

    // Wait for video player
    await page.waitForSelector('[data-testid="video-player"]', { timeout: 5000 })

    // Test play button
    const playButton = page.locator('[data-testid="play-button"]')
    await expect(playButton).toBeVisible()
    await playButton.click()
    await page.waitForTimeout(500)

    // Test skip forward
    const skipForwardButton = page.locator('[data-testid="skip-forward-button"]')
    await expect(skipForwardButton).toBeVisible()
    await skipForwardButton.click()
    await page.waitForTimeout(300)

    // Test skip back
    const skipBackButton = page.locator('[data-testid="skip-back-button"]')
    await expect(skipBackButton).toBeVisible()
    await skipBackButton.click()
    await page.waitForTimeout(300)

    // Verify timeline is visible
    const timeline = page.locator('[data-testid="video-timeline"]')
    await expect(timeline).toBeVisible()

    // Verify time display
    const timeDisplay = page.locator('[data-testid="time-display"]')
    await expect(timeDisplay).toBeVisible()
  })

  test('should handle video generation error gracefully', async ({ page }) => {
    // Override mock to return error
    await page.route('**/api/v1/synthetic/video/generate', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          detail: 'Video generation failed: out of memory'
        })
      })
    })

    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })

    // Click Synthetic Media tab
    const syntheticMediaTab = page.locator('button:has-text("Synthetic Media")')
    await syntheticMediaTab.waitFor({ state: 'visible', timeout: 15000 })
    await syntheticMediaTab.click()
    await page.waitForSelector('[data-testid="synthetic-media-tab"]', {
      state: 'visible',
      timeout: 15000
    })

    // Try to generate
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()

    // Wait for error handling
    await page.waitForTimeout(2000)

    // Verify error toast or message appears (implementation dependent)
    // The toast library should show an error
    const body = await page.locator('body').textContent()
    // Error should be handled, generation should stop
    await expect(generateButton).toBeEnabled()
  })

  test('should delete video', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate a video
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(1500)

    // Wait for video info panel
    await page.waitForSelector('[data-testid="video-info-panel"]', { timeout: 5000 })

    // Click delete button
    const deleteButton = page.locator('[data-testid="delete-video-button"]')
    await expect(deleteButton).toBeVisible()
    await deleteButton.click()
    await page.waitForTimeout(500)

    // Verify video player section shows empty state
    const videoPlayerSection = page.locator('[data-testid="video-player-section"]')
    const emptyMessage = videoPlayerSection.locator('text=No videos generated yet')
    await expect(emptyMessage).toBeVisible()
  })
})
