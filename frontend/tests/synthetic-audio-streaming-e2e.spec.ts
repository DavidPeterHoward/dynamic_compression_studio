/**
 * E2E Test: Synthetic Audio Streaming
 * Tests audio generation, playback controls, and playlist navigation
 */

import { test, expect } from '@playwright/test'

test.describe('Synthetic Audio Streaming E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Mock audio generation API
    await page.route('**/api/v1/synthetic/audio/generate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          audio_url: '/media/audio/test_audio.wav',
          metadata: {
            sampleRate: 44100,
            bitDepth: 16,
            channels: 2,
            duration: 30,
            fileSize: 5292000,
            format: 'wav'
          },
          analysis: {
            complexity: {
              kolmogorov: 0.56,
              structural: 0.65
            },
            entropy: {
              shannon: 0.72,
              temporal: 0.68
            },
            redundancy: {
              overall: 0.25,
              patterns: []
            },
            compressibility: {
              ratio: 1.8,
              algorithm: 'wav',
              efficiency: 0.78
            },
            steganography: {
              isSuspicious: false,
              confidence: 0.02,
              methods: []
            }
          },
          processing_time: 3.5,
          request_id: 'aud_test123'
        })
      })
    })

    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle')

    // Click the Synthetic Media tab
    const syntheticMediaTab = page.locator('button:has-text("Synthetic Media")')
    await syntheticMediaTab.waitFor({ state: 'visible', timeout: 10000 })
    await syntheticMediaTab.click()

    // Wait for tab content to load
    await page.waitForSelector('[data-testid="synthetic-media-tab"]', {
      state: 'visible',
      timeout: 15000
    })
  })

  test('should generate and display audio player', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Navigate to audio tab
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(500)

    // Generate audio
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()
    await generateButton.click()

    // Wait for generation
    await page.waitForTimeout(2000)

    // Verify audio player section is visible
    const audioPlayerSection = page.locator('[data-testid="audio-player-section"]')
    await expect(audioPlayerSection).toBeVisible({ timeout: 5000 })

    // Verify playlist
    const playlist = page.locator('[data-testid="playlist"]')
    await expect(playlist).toBeVisible()

    // Verify main player
    const audioPlayerMain = page.locator('[data-testid="audio-player-main"]')
    await expect(audioPlayerMain).toBeVisible()

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/audio-generated.png',
      fullPage: true
    })
  })

  test('should display audio metadata correctly', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Verify track info
    const trackInfo = page.locator('[data-testid="track-info"]')
    await expect(trackInfo).toBeVisible({ timeout: 5000 })

    const trackName = page.locator('[data-testid="current-track-name"]')
    await expect(trackName).toContainText('Track 1')

    const trackDetails = page.locator('[data-testid="current-track-details"]')
    await expect(trackDetails).toBeVisible()
    await expect(trackDetails).toContainText('44.1kHz')
    await expect(trackDetails).toContainText('16bit')
    await expect(trackDetails).toContainText('2ch')
  })

  test('should handle playback controls', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for player
    await page.waitForSelector('[data-testid="playback-controls"]', { timeout: 5000 })

    // Test play/pause button
    const playPauseButton = page.locator('[data-testid="play-pause-button"]')
    await expect(playPauseButton).toBeVisible()
    await playPauseButton.click()
    await page.waitForTimeout(500)

    // Test previous button
    const previousButton = page.locator('[data-testid="previous-button"]')
    await expect(previousButton).toBeVisible()
    await previousButton.click()
    await page.waitForTimeout(300)

    // Test next button
    const nextButton = page.locator('[data-testid="next-button"]')
    await expect(nextButton).toBeVisible()
    await nextButton.click()
    await page.waitForTimeout(300)

    // Test shuffle button
    const shuffleButton = page.locator('[data-testid="shuffle-button"]')
    await expect(shuffleButton).toBeVisible()
    await shuffleButton.click()
    await page.waitForTimeout(300)

    // Test repeat button
    const repeatButton = page.locator('[data-testid="repeat-button"]')
    await expect(repeatButton).toBeVisible()
    await repeatButton.click()
    await page.waitForTimeout(300)

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/audio-playback-controls.png',
      fullPage: true
    })
  })

  test('should control volume', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for additional controls
    await page.waitForSelector('[data-testid="additional-controls"]', { timeout: 5000 })

    // Test volume slider
    const volumeSlider = page.locator('[data-testid="volume-slider"]')
    await expect(volumeSlider).toBeVisible()

    // Set volume to 50%
    await volumeSlider.fill('0.5')
    await page.waitForTimeout(300)

    // Verify volume display
    const volumeDisplay = page.locator('[data-testid="volume-display"]')
    await expect(volumeDisplay).toContainText('50%')

    // Set volume to 100%
    await volumeSlider.fill('1')
    await page.waitForTimeout(300)
    await expect(volumeDisplay).toContainText('100%')

    // Set volume to 0%
    await volumeSlider.fill('0')
    await page.waitForTimeout(300)
    await expect(volumeDisplay).toContainText('0%')
  })

  test('should control playback speed', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for controls
    await page.waitForSelector('[data-testid="additional-controls"]', { timeout: 5000 })

    // Test playback speed selector
    const speedSelect = page.locator('[data-testid="playback-speed-select"]')
    await expect(speedSelect).toBeVisible()

    // Test different speeds
    await speedSelect.selectOption('0.5')
    await page.waitForTimeout(300)

    await speedSelect.selectOption('1.5')
    await page.waitForTimeout(300)

    await speedSelect.selectOption('2')
    await page.waitForTimeout(300)

    await speedSelect.selectOption('1')
    await page.waitForTimeout(300)
  })

  test('should display analysis metrics', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for analysis panel
    await page.waitForSelector('[data-testid="audio-analysis-panel"]', { timeout: 5000 })

    const analysisPanel = page.locator('[data-testid="audio-analysis-panel"]')
    await expect(analysisPanel).toBeVisible()

    // Verify complexity metric
    const complexityMetric = page.locator('[data-testid="analysis-complexity"]')
    await expect(complexityMetric).toBeVisible()
    await expect(complexityMetric).toContainText('0.65')

    // Verify entropy metric
    const entropyMetric = page.locator('[data-testid="analysis-entropy"]')
    await expect(entropyMetric).toBeVisible()
    await expect(entropyMetric).toContainText('0.72')

    // Verify compressibility metric
    const compressibilityMetric = page.locator('[data-testid="analysis-compressibility"]')
    await expect(compressibilityMetric).toBeVisible()
    await expect(compressibilityMetric).toContainText('1.8x')
  })

  test('should navigate seekbar', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for seekbar
    await page.waitForSelector('[data-testid="seekbar-container"]', { timeout: 5000 })

    const seekbar = page.locator('[data-testid="seekbar"]')
    await expect(seekbar).toBeVisible()

    // Verify time displays
    const currentTime = page.locator('[data-testid="current-time"]')
    await expect(currentTime).toBeVisible()

    const totalDuration = page.locator('[data-testid="total-duration"]')
    await expect(totalDuration).toBeVisible()
    await expect(totalDuration).toContainText('0:30')
  })

  test('should manage playlist with multiple tracks', async ({ page }) => {
    // Tab content already loaded by beforeEach

    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    // Generate first track
    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Verify first playlist item
    await page.waitForSelector('[data-testid="playlist-item-0"]', { timeout: 5000 })
    const firstPlaylistItem = page.locator('[data-testid="playlist-item-0"]')
    await expect(firstPlaylistItem).toBeVisible()

    // Generate second track
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Verify second playlist item
    const secondPlaylistItem = page.locator('[data-testid="playlist-item-1"]')
    await expect(secondPlaylistItem).toBeVisible()

    // Verify track names
    const firstTrackName = page.locator('[data-testid="track-name-0"]')
    await expect(firstTrackName).toContainText('Track 1')

    const secondTrackName = page.locator('[data-testid="track-name-1"]')
    await expect(secondTrackName).toContainText('Track 2')

    // Click to switch to second track
    await secondPlaylistItem.click()
    await page.waitForTimeout(500)

    // Verify current track name updated
    const currentTrackName = page.locator('[data-testid="current-track-name"]')
    await expect(currentTrackName).toContainText('Track 2')

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/audio-playlist.png',
      fullPage: true
    })
  })

  test('should delete audio track', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for playlist
    await page.waitForSelector('[data-testid="playlist-item-0"]', { timeout: 5000 })

    // Click delete button in playlist
    const deleteButton = page.locator('[data-testid="track-delete-0"]')
    await expect(deleteButton).toBeVisible()
    await deleteButton.click()
    await page.waitForTimeout(500)

    // Verify empty state
    const audioPlayerSection = page.locator('[data-testid="audio-player-section"]')
    const emptyMessage = audioPlayerSection.locator('text=No audio tracks generated yet')
    await expect(emptyMessage).toBeVisible()
  })

  test('should show playing indicator', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for player
    await page.waitForSelector('[data-testid="play-pause-button"]', { timeout: 5000 })

    // Click play
    const playPauseButton = page.locator('[data-testid="play-pause-button"]')
    await playPauseButton.click()
    await page.waitForTimeout(500)

    // Verify playing indicator appears
    const playingIndicator = page.locator('[data-testid="playing-indicator"]')
    await expect(playingIndicator).toBeVisible()
  })

  test('should handle empty audio state', async ({ page }) => {
    // Override to simulate no audio generation
    await page.route('**/api/v1/synthetic/audio/generate', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          detail: 'Invalid audio parameters'
        })
      })
    })

    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })
    // Wait removed - using domcontentloaded
    // Tab content already loaded by beforeEach

    // Navigate to audio tab
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(500)

    // Verify empty state
    const audioPlayerSection = page.locator('[data-testid="audio-player-section"]')
    await expect(audioPlayerSection).toBeVisible()

    const emptyMessage = audioPlayerSection.locator('text=No audio tracks generated yet')
    await expect(emptyMessage).toBeVisible()
  })
})
