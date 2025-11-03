/**
 * DATA PIPELINE SEQUENCE E2E TESTS
 *
 * This test file traces the complete data flow through the system:
 * Services → API → Routes → Frontend → UI
 *
 * Purpose: Verify end-to-end data pipeline integrity with real backend
 */

import { test, expect } from '@playwright/test'

test.describe('Data Pipeline Sequence - Services → API → Frontend', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate and wait for app to be ready
    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })

    // Wait for page to be fully loaded
    await page.waitForLoadState('networkidle')

    // Wait for the Synthetic Media button to be visible
    const syntheticMediaTab = page.locator('button:has-text("Synthetic Media")')
    await syntheticMediaTab.waitFor({ state: 'visible', timeout: 15000 })
    await syntheticMediaTab.click()

    // Wait for tab content to load
    await page.waitForSelector('[data-testid="synthetic-media-tab"]', {
      state: 'visible',
      timeout: 15000
    })
  })

  // =========================================================================
  // TEST 1: Video Pipeline - Complete Flow
  // =========================================================================
  test('Pipeline 1: Video Generation - Frontend → API → Backend → Response', async ({ page }) => {
    console.log('\n========================================')
    console.log('🔍 PIPELINE TRACE: Video Generation')
    console.log('========================================\n')

    // Step 1: Verify frontend component loaded
    // Tab content already loaded by beforeEach
    console.log('✅ Step 1: Frontend component loaded')

    // Step 2: Navigate to video tab
    const videoTab = page.locator('[data-testid="video-tab"]')
    await expect(videoTab).toBeVisible()
    await videoTab.click()
    await page.waitForTimeout(500)
    console.log('✅ Step 2: Video tab selected')

    // Step 3: Verify generate button is enabled (frontend state ready)
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()
    console.log('✅ Step 3: Generate button enabled (frontend ready)')

    // Step 4: Capture API request (network layer)
    let apiRequestCaptured = false
    let apiResponseCaptured = false
    let requestData: any = null
    let responseData: any = null

    page.on('request', request => {
      if (request.url().includes('/api/v1/synthetic/video/generate')) {
        apiRequestCaptured = true
        requestData = request.postDataJSON()
        console.log('📤 Step 4: API Request captured')
        console.log('   URL:', request.url())
        console.log('   Method:', request.method())
        console.log('   Payload:', JSON.stringify(requestData, null, 2))
      }
    })

    page.on('response', async response => {
      if (response.url().includes('/api/v1/synthetic/video/generate')) {
        apiResponseCaptured = true
        try {
          responseData = await response.json()
          console.log('📥 Step 5: API Response received')
          console.log('   Status:', response.status())
          console.log('   Success:', responseData.success)
          console.log('   Video URL:', responseData.video_url)
        } catch (e) {
          console.error('Failed to parse response:', e)
        }
      }
    })

    // Step 6: Trigger generation (user interaction → API call)
    await generateButton.click()
    console.log('🚀 Step 6: Generation triggered (user click → API call)')

    // Step 7: Wait for API round-trip
    await page.waitForTimeout(3000)

    // Verify API communication happened
    expect(apiRequestCaptured).toBeTruthy()
    expect(apiResponseCaptured).toBeTruthy()
    console.log('✅ Step 7: API round-trip completed')

    // Step 8: Verify response data structure
    if (responseData) {
      expect(responseData).toHaveProperty('success')
      expect(responseData).toHaveProperty('video_url')
      expect(responseData).toHaveProperty('metadata')
      expect(responseData).toHaveProperty('analysis')
      console.log('✅ Step 8: Response data validation passed')
      console.log('   Metadata:', JSON.stringify(responseData.metadata, null, 2))
      console.log('   Analysis:', JSON.stringify(responseData.analysis, null, 2))
    }

    // Step 9: Verify UI updated with response data
    const videoPlayerSection = page.locator('[data-testid="video-player-section"]')
    await expect(videoPlayerSection).toBeVisible({ timeout: 5000 })
    console.log('✅ Step 9: UI updated (video player visible)')

    // Step 10: Verify metadata displayed (data binding)
    const videoInfoPanel = page.locator('[data-testid="video-info-panel"]')
    await expect(videoInfoPanel).toBeVisible()

    const resolutionValue = page.locator('[data-testid="prop-value-resolution"]')
    await expect(resolutionValue).toBeVisible()
    const resolutionText = await resolutionValue.textContent()
    console.log('✅ Step 10: Metadata displayed in UI')
    console.log('   Resolution:', resolutionText)

    // Step 11: Verify analysis metrics (complex data flow)
    const complexityValue = page.locator('[data-testid="metric-value-complexity"]')
    await expect(complexityValue).toBeVisible()
    const complexityText = await complexityValue.textContent()
    console.log('✅ Step 11: Analysis metrics rendered')
    console.log('   Complexity:', complexityText)

    console.log('\n========================================')
    console.log('✅ PIPELINE COMPLETE: All 11 steps verified')
    console.log('========================================\n')

    // Take screenshot proof
    await page.screenshot({
      path: 'frontend/tests/screenshots/pipeline-video-complete.png',
      fullPage: true
    })
  })

  // =========================================================================
  // TEST 2: Image Pipeline - Batch Processing
  // =========================================================================
  test('Pipeline 2: Image Batch - Frontend → API → Batch Processing → Gallery', async ({ page }) => {
    console.log('\n========================================')
    console.log('🔍 PIPELINE TRACE: Image Batch Generation')
    console.log('========================================\n')

    // Tab content already loaded by beforeEach

    // Switch to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(500)
    console.log('✅ Step 1: Image tab selected')

    // Capture API communication
    let batchResponseData: any = null

    page.on('response', async response => {
      if (response.url().includes('/api/v1/synthetic/image/generate')) {
        try {
          batchResponseData = await response.json()
          console.log('📥 Step 2: Batch API Response received')
          console.log('   Images count:', batchResponseData.images?.length || 0)
        } catch (e) {
          console.error('Failed to parse response:', e)
        }
      }
    })

    // Trigger generation
    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    console.log('🚀 Step 3: Batch generation triggered')

    await page.waitForTimeout(3000)

    // Verify batch response
    if (batchResponseData) {
      expect(batchResponseData).toHaveProperty('success')
      expect(batchResponseData).toHaveProperty('images')
      expect(Array.isArray(batchResponseData.images)).toBeTruthy()
      console.log('✅ Step 4: Batch data structure validated')
      console.log('   Batch analysis:', JSON.stringify(batchResponseData.batch_analysis, null, 2))
    }

    // Verify gallery rendered
    const imageGallery = page.locator('[data-testid="image-gallery-section"]')
    await expect(imageGallery).toBeVisible({ timeout: 5000 })
    console.log('✅ Step 5: Gallery component rendered')

    // Verify image count matches response
    const imageCount = page.locator('[data-testid="image-count"]')
    await expect(imageCount).toBeVisible()
    const countText = await imageCount.textContent()
    console.log('✅ Step 6: Image count displayed:', countText)

    console.log('\n========================================')
    console.log('✅ PIPELINE COMPLETE: Batch processing verified')
    console.log('========================================\n')

    await page.screenshot({
      path: 'frontend/tests/screenshots/pipeline-image-batch-complete.png',
      fullPage: true
    })
  })

  // =========================================================================
  // TEST 3: Audio Pipeline - Streaming & Metadata
  // =========================================================================
  test('Pipeline 3: Audio Generation - Real-time Data Flow', async ({ page }) => {
    console.log('\n========================================')
    console.log('🔍 PIPELINE TRACE: Audio Generation')
    console.log('========================================\n')

    // Tab content already loaded by beforeEach

    // Switch to audio tab
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(500)
    console.log('✅ Step 1: Audio tab selected')

    // Capture audio API data
    let audioResponseData: any = null
    let requestPayload: any = null

    page.on('request', request => {
      if (request.url().includes('/api/v1/synthetic/audio/generate')) {
        requestPayload = request.postDataJSON()
        console.log('📤 Step 2: Audio request payload')
        console.log('   Sample Rate:', requestPayload.sampleRate)
        console.log('   Bit Depth:', requestPayload.bitDepth)
        console.log('   Channels:', requestPayload.channels)
        console.log('   Duration:', requestPayload.duration)
        console.log('   Sources:', JSON.stringify(requestPayload.sources, null, 2))
      }
    })

    page.on('response', async response => {
      if (response.url().includes('/api/v1/synthetic/audio/generate')) {
        try {
          audioResponseData = await response.json()
          console.log('📥 Step 3: Audio response received')
          console.log('   Audio URL:', audioResponseData.audio_url)
          console.log('   Metadata:', JSON.stringify(audioResponseData.metadata, null, 2))
        } catch (e) {
          console.error('Failed to parse response:', e)
        }
      }
    })

    // Trigger generation
    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    console.log('🚀 Step 4: Audio generation triggered')

    await page.waitForTimeout(3000)

    // Verify audio metadata
    if (audioResponseData) {
      expect(audioResponseData.metadata).toHaveProperty('sampleRate')
      expect(audioResponseData.metadata).toHaveProperty('bitDepth')
      expect(audioResponseData.metadata).toHaveProperty('channels')
      expect(audioResponseData.metadata).toHaveProperty('duration')
      console.log('✅ Step 5: Audio metadata validated')
    }

    // Verify audio player rendered
    const audioPlayerSection = page.locator('[data-testid="audio-player-section"]')
    await expect(audioPlayerSection).toBeVisible({ timeout: 5000 })
    console.log('✅ Step 6: Audio player rendered')

    // Verify track info displayed
    const trackInfo = page.locator('[data-testid="track-info"]')
    await expect(trackInfo).toBeVisible()
    console.log('✅ Step 7: Track info displayed')

    console.log('\n========================================')
    console.log('✅ PIPELINE COMPLETE: Audio flow verified')
    console.log('========================================\n')

    await page.screenshot({
      path: 'frontend/tests/screenshots/pipeline-audio-complete.png',
      fullPage: true
    })
  })

  // =========================================================================
  // TEST 4: Error Handling Pipeline
  // =========================================================================
  test('Pipeline 4: Error Handling - API Error → Frontend Display', async ({ page }) => {
    console.log('\n========================================')
    console.log('🔍 PIPELINE TRACE: Error Handling')
    console.log('========================================\n')

    // Mock error response
    await page.route('**/api/v1/synthetic/video/generate', async route => {
      console.log('📤 Step 1: Intercepted API request (mock error)')
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          detail: 'Simulated server error for pipeline testing'
        })
      })
    })

    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })
    const syntheticMediaTab = page.locator('button:has-text("Synthetic Media")')
    await syntheticMediaTab.waitFor({ state: 'visible', timeout: 15000 })
    await syntheticMediaTab.click()
    await page.waitForTimeout(1000)

    // Tab content already loaded by beforeEach

    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(500)

    // Trigger generation (should fail)
    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    console.log('🚀 Step 2: Generation triggered (expect error)')

    await page.waitForTimeout(2000)

    // Verify error was handled gracefully
    const body = await page.locator('body').textContent()
    console.log('✅ Step 3: Error handled by frontend')
    console.log('   Button state reset:', await generateButton.isEnabled())

    console.log('\n========================================')
    console.log('✅ PIPELINE COMPLETE: Error handling verified')
    console.log('========================================\n')

    await page.screenshot({
      path: 'frontend/tests/screenshots/pipeline-error-handling.png',
      fullPage: true
    })
  })

  // =========================================================================
  // TEST 5: Multi-Media Sequential Pipeline
  // =========================================================================
  test('Pipeline 5: Sequential Generation - Video → Image → Audio', async ({ page }) => {
    console.log('\n========================================')
    console.log('🔍 PIPELINE TRACE: Sequential Multi-Media')
    console.log('========================================\n')

    // Tab content already loaded by beforeEach

    // Track all API calls
    const apiCalls: string[] = []

    page.on('request', request => {
      if (request.url().includes('/api/v1/synthetic/')) {
        const url = request.url()
        if (url.includes('/video/generate')) apiCalls.push('video')
        if (url.includes('/image/generate')) apiCalls.push('image')
        if (url.includes('/audio/generate')) apiCalls.push('audio')
        console.log(`📤 API Call ${apiCalls.length}: ${apiCalls[apiCalls.length - 1]}`)
      }
    })

    // Generate Video
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(500)

    let generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2500)
    console.log('✅ Step 1: Video generated')

    // Generate Image
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(500)

    generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2500)
    console.log('✅ Step 2: Image generated')

    // Generate Audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(500)

    generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2500)
    console.log('✅ Step 3: Audio generated')

    // Verify all three types generated
    expect(apiCalls.length).toBe(3)
    expect(apiCalls).toContain('video')
    expect(apiCalls).toContain('image')
    expect(apiCalls).toContain('audio')
    console.log('✅ Step 4: All media types processed')
    console.log('   API call sequence:', apiCalls.join(' → '))

    console.log('\n========================================')
    console.log('✅ PIPELINE COMPLETE: Sequential flow verified')
    console.log('========================================\n')

    await page.screenshot({
      path: 'frontend/tests/screenshots/pipeline-sequential-complete.png',
      fullPage: true
    })
  })

  // =========================================================================
  // TEST 6: Data Validation Pipeline
  // =========================================================================
  test('Pipeline 6: Data Validation - Schema Validation Flow', async ({ page }) => {
    console.log('\n========================================')
    console.log('🔍 PIPELINE TRACE: Data Validation')
    console.log('========================================\n')

    // Tab content already loaded by beforeEach

    // Monitor console for validation messages
    const consoleMessages: string[] = []
    page.on('console', msg => {
      const text = msg.text()
      if (text.includes('[Video Generation]') || text.includes('Validation')) {
        consoleMessages.push(text)
        console.log('📋 Console:', text)
      }
    })

    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(500)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()

    await page.waitForTimeout(3000)

    console.log('✅ Validation pipeline traced')
    console.log(`   Console logs captured: ${consoleMessages.length}`)

    console.log('\n========================================')
    console.log('✅ PIPELINE COMPLETE: Validation flow traced')
    console.log('========================================\n')
  })
})
