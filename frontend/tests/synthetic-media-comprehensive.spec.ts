/**
 * Comprehensive E2E Test: Synthetic Media Generation (Video, Image, Audio)
 * Tests complete workflow for all media types with output verification
 */

import { test, expect } from '@playwright/test'

test.describe('Synthetic Media Generation - Comprehensive', () => {
  test.beforeEach(async ({ page }) => {
    // Mock video generation API
    await page.route('**/api/v1/synthetic/video/generate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          video_url: '/media/videos/test_video.mp4',
          thumbnail_url: '/media/thumbnails/test_video.jpg',
          metadata: {
            width: 640,
            height: 480,
            duration: 2,
            frameRate: 10,
            fileSize: 1024000,
            codec: 'h264'
          },
          analysis: {
            complexity: {
              kolmogorov: 0.72,
              structural: 0.75
            },
            entropy: {
              shannon: 0.68,
              temporal: 0.55
            },
            redundancy: {
              overall: 0.28,
              patterns: []
            },
            compressibility: {
              ratio: 2.8,
              algorithm: 'h264',
              efficiency: 0.88
            },
            steganography: {
              isSuspicious: false,
              confidence: 0.05,
              methods: []
            }
          },
          processing_time: 5.2,
          request_id: 'vid_comp_test'
        })
      })
    })

    // Mock image generation API
    await page.route('**/api/v1/synthetic/image/generate', async (route) => {
      const images = Array.from({ length: 1 }, (_, i) => ({
        id: `img_comp_test_${i}`,
        image_url: `/media/images/test_${i}.png`,
        thumbnail_url: `/media/thumbnails/test_${i}.png`,
        metadata: {
          width: 512,
          height: 512,
          format: 'png',
          fileSize: 256000,
          colorSpace: 'rgb'
        },
        analysis: {
          complexity: {
            kolmogorov: 0.65,
            structural: 0.70
          },
          entropy: {
            shannon: 0.75,
            spatial: 0.68
          },
          redundancy: {
            overall: 0.25,
            patterns: []
          },
          compressibility: {
            ratio: 2.2,
            algorithm: 'png',
            efficiency: 0.85
          },
          steganography: {
            isSuspicious: false,
            confidence: 0.02,
            methods: []
          }
        }
      }))

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          images: images,
          batch_analysis: {
            avg_complexity: 0.70,
            avg_entropy: 0.75,
            avg_compressibility: 2.2
          },
          processing_time: 3.5
        })
      })
    })

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
            duration: 2,
            fileSize: 352800,
            format: 'wav'
          },
          analysis: {
            complexity: {
              kolmogorov: 0.58,
              structural: 0.62
            },
            entropy: {
              shannon: 0.70,
              temporal: 0.65
            },
            redundancy: {
              overall: 0.30,
              patterns: []
            },
            compressibility: {
              ratio: 1.5,
              algorithm: 'wav',
              efficiency: 0.75
            },
            steganography: {
              isSuspicious: false,
              confidence: 0.01,
              methods: []
            }
          },
          processing_time: 2.1,
          request_id: 'aud_comp_test'
        })
      })
    })

    // Navigate to application
    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })
    await page.waitForLoadState('networkidle')

    // Navigate to Synthetic Media tab
    const syntheticMediaTab = page.locator('button:has-text("Synthetic Media")')
    await syntheticMediaTab.waitFor({ state: 'visible', timeout: 15000 })
    await syntheticMediaTab.click()

    // Wait for tab content
    await page.waitForSelector('[data-testid="synthetic-media-tab"]', {
      state: 'visible',
      timeout: 15000
    })
  })

  test('should generate video and verify output display', async ({ page }) => {
    console.log('Testing video generation...')

    // Navigate to video tab
    const videoTab = page.locator('[data-testid="video-tab"]')
    await expect(videoTab).toBeVisible()
    await videoTab.click()
    await page.waitForTimeout(500)

    // Take screenshot before generation
    await page.screenshot({
      path: 'frontend/tests/screenshots/video-before-generation.png',
      fullPage: true
    })

    // Click generate button
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()
    console.log('Clicking generate button for video...')
    await generateButton.click()

    // Wait for generation
    await page.waitForTimeout(2000)

    // Verify video player section appears
    const videoPlayerSection = page.locator('[data-testid="video-player-section"]')
    await expect(videoPlayerSection).toBeVisible({ timeout: 10000 })
    console.log('Video player section is visible')

    // Verify video player element
    const videoPlayer = page.locator('[data-testid="video-player"]')
    await expect(videoPlayer).toBeVisible()
    console.log('Video player element is visible')

    // Verify video metadata
    const videoInfoPanel = page.locator('[data-testid="video-info-panel"]')
    await expect(videoInfoPanel).toBeVisible()

    const resolutionValue = page.locator('[data-testid="prop-value-resolution"]')
    await expect(resolutionValue).toContainText('640x480')

    const framerateValue = page.locator('[data-testid="prop-value-framerate"]')
    await expect(framerateValue).toContainText('10 fps')

    // Verify video controls are present
    const playButton = page.locator('[data-testid="play-button"]')
    await expect(playButton).toBeVisible()

    const timeline = page.locator('[data-testid="video-timeline"]')
    await expect(timeline).toBeVisible()

    // Take screenshot after generation
    await page.screenshot({
      path: 'frontend/tests/screenshots/video-after-generation.png',
      fullPage: true
    })

    console.log('Video generation test completed successfully')
  })

  test('should generate image and verify output display', async ({ page }) => {
    console.log('Testing image generation...')

    // Navigate to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await expect(imageTab).toBeVisible()
    await imageTab.click()
    await page.waitForTimeout(500)

    // Take screenshot before generation
    await page.screenshot({
      path: 'frontend/tests/screenshots/image-before-generation.png',
      fullPage: true
    })

    // Click generate button
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()
    console.log('Clicking generate button for image...')
    await generateButton.click()

    // Wait for generation
    await page.waitForTimeout(2000)

    // Verify image gallery section appears
    const imageGallerySection = page.locator('[data-testid="image-gallery-section"]')
    await expect(imageGallerySection).toBeVisible({ timeout: 10000 })
    console.log('Image gallery section is visible')

    // Verify gallery grid
    const galleryGrid = page.locator('[data-testid="gallery-grid"]')
    await expect(galleryGrid).toBeVisible()
    console.log('Gallery grid is visible')

    // Verify at least one image card exists
    const imageCard = page.locator('[data-testid="image-card-0"]')
    await expect(imageCard).toBeVisible()
    console.log('Image card is visible')

    // Verify image thumbnail
    const imageThumbnail = page.locator('[data-testid="image-thumbnail-0"]')
    await expect(imageThumbnail).toBeVisible()

    // Verify gallery controls
    const galleryControls = page.locator('[data-testid="gallery-controls"]')
    await expect(galleryControls).toBeVisible()

    const imageCount = page.locator('[data-testid="image-count"]')
    await expect(imageCount).toBeVisible()

    // Take screenshot after generation
    await page.screenshot({
      path: 'frontend/tests/screenshots/image-after-generation.png',
      fullPage: true
    })

    console.log('Image generation test completed successfully')
  })

  test('should generate audio and verify output display', async ({ page }) => {
    console.log('Testing audio generation...')

    // Navigate to audio tab
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await expect(audioTab).toBeVisible()
    await audioTab.click()
    await page.waitForTimeout(500)

    // Take screenshot before generation
    await page.screenshot({
      path: 'frontend/tests/screenshots/audio-before-generation.png',
      fullPage: true
    })

    // Click generate button
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()
    console.log('Clicking generate button for audio...')
    await generateButton.click()

    // Wait for generation
    await page.waitForTimeout(2000)

    // Verify audio player section appears
    const audioPlayerSection = page.locator('[data-testid="audio-player-section"]')
    await expect(audioPlayerSection).toBeVisible({ timeout: 10000 })
    console.log('Audio player section is visible')

    // Verify playlist
    const playlist = page.locator('[data-testid="playlist"]')
    await expect(playlist).toBeVisible()
    console.log('Playlist is visible')

    // Verify playlist item
    const playlistItem = page.locator('[data-testid="playlist-item-0"]')
    await expect(playlistItem).toBeVisible()
    console.log('Playlist item is visible')

    // Verify main audio player
    const audioPlayerMain = page.locator('[data-testid="audio-player-main"]')
    await expect(audioPlayerMain).toBeVisible()

    // Verify playback controls
    const playbackControls = page.locator('[data-testid="playback-controls"]')
    await expect(playbackControls).toBeVisible()

    const playPauseButton = page.locator('[data-testid="play-pause-button"]')
    await expect(playPauseButton).toBeVisible()

    // Verify track info
    const trackInfo = page.locator('[data-testid="track-info"]')
    await expect(trackInfo).toBeVisible()

    const currentTrackName = page.locator('[data-testid="current-track-name"]')
    await expect(currentTrackName).toContainText('Track 1')

    // Take screenshot after generation
    await page.screenshot({
      path: 'frontend/tests/screenshots/audio-after-generation.png',
      fullPage: true
    })

    console.log('Audio generation test completed successfully')
  })

  test('should switch between all media types and verify each display', async ({ page }) => {
    console.log('Testing media type switching with all three types...')

    // Test Video
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    let generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    const videoPlayerSection = page.locator('[data-testid="video-player-section"]')
    await expect(videoPlayerSection).toBeVisible()
    console.log('Video generated and visible')

    // Switch to Image
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    const imageGallerySection = page.locator('[data-testid="image-gallery-section"]')
    await expect(imageGallerySection).toBeVisible()
    console.log('Image generated and visible')

    // Switch to Audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    const audioPlayerSection = page.locator('[data-testid="audio-player-section"]')
    await expect(audioPlayerSection).toBeVisible()
    console.log('Audio generated and visible')

    // Verify statistics updated
    const videoCount = page.locator('text=Videos').locator('xpath=..').locator('.text-2xl')
    await expect(videoCount).toContainText('1')

    const imageCount = page.locator('text=Images').locator('xpath=..').locator('.text-2xl')
    await expect(imageCount).toContainText('1')

    const audioCount = page.locator('text=Audio').locator('xpath=..').locator('.text-2xl')
    await expect(audioCount).toContainText('1')

    // Take final screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/all-media-types-generated.png',
      fullPage: true
    })

    console.log('All media types switching test completed successfully')
  })

  test('should verify video playback functionality', async ({ page }) => {
    // Generate video
    const videoTab = page.locator('[data-testid="video-tab"]')
    await videoTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Test play button
    const playButton = page.locator('[data-testid="play-button"]')
    await expect(playButton).toBeVisible()
    await playButton.click()
    await page.waitForTimeout(500)

    // Test skip controls
    const skipForwardButton = page.locator('[data-testid="skip-forward-button"]')
    await expect(skipForwardButton).toBeVisible()
    await skipForwardButton.click()
    await page.waitForTimeout(300)

    const skipBackButton = page.locator('[data-testid="skip-back-button"]')
    await expect(skipBackButton).toBeVisible()
    await skipBackButton.click()
    await page.waitForTimeout(300)

    // Test analysis overlay toggle
    const analysisToggle = page.locator('[data-testid="analysis-toggle"]')
    await expect(analysisToggle).toBeVisible()
    await analysisToggle.click()
    await page.waitForTimeout(300)

    const analysisOverlay = page.locator('[data-testid="video-analysis-overlay"]')
    await expect(analysisOverlay).toBeVisible()

    await page.screenshot({
      path: 'frontend/tests/screenshots/video-playback-controls.png',
      fullPage: true
    })
  })

  test('should verify image lightbox functionality', async ({ page }) => {
    // Generate image
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Click on image to open lightbox
    const imageCard = page.locator('[data-testid="image-card-0"]')
    await imageCard.click()
    await page.waitForTimeout(500)

    // Verify lightbox opened
    const lightbox = page.locator('[data-testid="image-lightbox"]')
    await expect(lightbox).toBeVisible()

    const lightboxImage = page.locator('[data-testid="lightbox-image"]')
    await expect(lightboxImage).toBeVisible()

    const lightboxTitle = page.locator('[data-testid="lightbox-title"]')
    await expect(lightboxTitle).toBeVisible()

    await page.screenshot({
      path: 'frontend/tests/screenshots/image-lightbox.png',
      fullPage: true
    })

    // Close lightbox
    const closeButton = page.locator('[data-testid="lightbox-close"]')
    await closeButton.click()
    await page.waitForTimeout(500)

    await expect(lightbox).not.toBeVisible()
  })

  test('should verify audio playback controls', async ({ page }) => {
    // Generate audio
    const audioTab = page.locator('[data-testid="audio-tab"]')
    await audioTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Test play/pause
    const playPauseButton = page.locator('[data-testid="play-pause-button"]')
    await expect(playPauseButton).toBeVisible()
    await playPauseButton.click()
    await page.waitForTimeout(500)

    // Test next/previous buttons
    const nextButton = page.locator('[data-testid="next-button"]')
    await expect(nextButton).toBeVisible()

    const previousButton = page.locator('[data-testid="previous-button"]')
    await expect(previousButton).toBeVisible()

    // Test shuffle
    const shuffleButton = page.locator('[data-testid="shuffle-button"]')
    await expect(shuffleButton).toBeVisible()
    await shuffleButton.click()
    await page.waitForTimeout(300)

    // Test repeat
    const repeatButton = page.locator('[data-testid="repeat-button"]')
    await expect(repeatButton).toBeVisible()
    await repeatButton.click()
    await page.waitForTimeout(300)

    await page.screenshot({
      path: 'frontend/tests/screenshots/audio-controls.png',
      fullPage: true
    })
  })
})
