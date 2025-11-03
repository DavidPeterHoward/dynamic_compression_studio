/**
 * E2E Test: Synthetic Image Batch Generation
 * Tests batch image generation, gallery views, and lightbox navigation
 */

import { test, expect } from '@playwright/test'

test.describe('Synthetic Image Batch Generation E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Mock batch image API
    await page.route('**/api/v1/synthetic/image/generate', async (route) => {
      // Generate mock images
      const images = Array.from({ length: 10 }, (_, i) => ({
        id: `img_test_${i}`,
        image_url: `/media/images/test_${i}.png`,
        thumbnail_url: `/media/thumbnails/test_${i}.png`,
        metadata: {
          width: 512,
          height: 512,
          format: 'png',
          fileSize: 204800 + (i * 10000),
          colorSpace: 'rgb'
        },
        analysis: {
          complexity: {
            kolmogorov: 0.5 + (i * 0.05),
            structural: 0.55 + (i * 0.04)
          },
          entropy: {
            shannon: 0.7 - (i * 0.02),
            spatial: 0.65 - (i * 0.015)
          },
          redundancy: {
            overall: 0.3 + (i * 0.01),
            patterns: []
          },
          compressibility: {
            ratio: 2.0 + (i * 0.1),
            algorithm: 'png',
            efficiency: 0.82
          },
          steganography: {
            isSuspicious: false,
            confidence: 0.03,
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
            avg_complexity: 0.725,
            avg_entropy: 0.61,
            avg_compressibility: 2.45
          },
          processing_time: 12.45
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

  test('should generate and display batch of images', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Navigate to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(500)

    // Generate images
    const generateButton = page.locator('[data-testid="generate-button"]')
    await expect(generateButton).toBeEnabled()
    await generateButton.click()

    // Wait for generation to complete
    await page.waitForTimeout(2000)

    // Verify gallery is visible
    const imageGallery = page.locator('[data-testid="image-gallery-section"]')
    await expect(imageGallery).toBeVisible({ timeout: 5000 })

    // Verify image grid
    const imageGrid = page.locator('[data-testid="gallery-grid"]')
    await expect(imageGrid).toBeVisible()

    // Verify image count
    const imageCount = page.locator('[data-testid="image-count"]')
    await expect(imageCount).toContainText('10 images')

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/image-batch-generated.png',
      fullPage: true
    })
  })

  test('should switch between grid and list views', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate images
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Verify grid view is default
    const gridView = page.locator('[data-testid="gallery-grid"]')
    await expect(gridView).toBeVisible({ timeout: 5000 })

    // Switch to list view
    const listViewButton = page.locator('[data-testid="view-list-button"]')
    await expect(listViewButton).toBeVisible()
    await listViewButton.click()
    await page.waitForTimeout(500)

    const listView = page.locator('[data-testid="gallery-list"]')
    await expect(listView).toBeVisible()
    await expect(gridView).not.toBeVisible()

    // Switch back to grid
    const gridViewButton = page.locator('[data-testid="view-grid-button"]')
    await gridViewButton.click()
    await page.waitForTimeout(500)

    await expect(gridView).toBeVisible()
    await expect(listView).not.toBeVisible()

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/image-view-modes.png',
      fullPage: true
    })
  })

  test('should sort images by different criteria', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate images
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for gallery
    await page.waitForSelector('[data-testid="gallery-controls"]', { timeout: 5000 })

    const sortSelect = page.locator('[data-testid="sort-select"]')
    await expect(sortSelect).toBeVisible()

    // Test sorting by date (default)
    await sortSelect.selectOption('date')
    await page.waitForTimeout(300)

    // Test sorting by size
    await sortSelect.selectOption('size')
    await page.waitForTimeout(300)

    // Test sorting by complexity
    await sortSelect.selectOption('complexity')
    await page.waitForTimeout(300)

    // Verify images are still visible after sorting
    const imageCards = page.locator('[data-testid^="image-card-"]')
    await expect(imageCards.first()).toBeVisible()
  })

  test('should support batch selection and operations', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate images
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for images to load
    await page.waitForSelector('[data-testid="image-card-0"]', { timeout: 5000 })

    // Select multiple images by clicking on them
    // Note: Images are selected via checkbox in the component
    const firstImage = page.locator('[data-testid="image-card-0"]')
    const secondImage = page.locator('[data-testid="image-card-1"]')
    const thirdImage = page.locator('[data-testid="image-card-2"]')

    // Click on checkbox inside each image card
    await firstImage.locator('input[type="checkbox"]').check()
    await page.waitForTimeout(200)

    await secondImage.locator('input[type="checkbox"]').check()
    await page.waitForTimeout(200)

    await thirdImage.locator('input[type="checkbox"]').check()
    await page.waitForTimeout(200)

    // Verify batch actions appear
    const batchActions = page.locator('[data-testid="batch-actions"]')
    await expect(batchActions).toBeVisible()

    // Verify selection count
    const selectionCount = page.locator('[data-testid="selection-count"]')
    await expect(selectionCount).toContainText('3 selected')

    // Verify batch delete button is visible
    const batchDeleteButton = page.locator('[data-testid="batch-delete-button"]')
    await expect(batchDeleteButton).toBeEnabled()

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/image-batch-selection.png',
      fullPage: true
    })

    // Test deselect all
    const deselectButton = page.locator('[data-testid="deselect-all-button"]')
    await deselectButton.click()
    await page.waitForTimeout(500)

    // Verify batch actions are hidden
    await expect(batchActions).not.toBeVisible()
  })

  test('should open and navigate lightbox', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate images
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Wait for first image
    await page.waitForSelector('[data-testid="image-card-0"]', { timeout: 5000 })

    // Click first image to open lightbox
    const firstImage = page.locator('[data-testid="image-card-0"]')
    await firstImage.click()
    await page.waitForTimeout(500)

    // Verify lightbox is open
    const lightbox = page.locator('[data-testid="image-lightbox"]')
    await expect(lightbox).toBeVisible()

    // Verify lightbox image
    const lightboxImage = page.locator('[data-testid="lightbox-image"]')
    await expect(lightboxImage).toBeVisible()

    // Verify lightbox title
    const lightboxTitle = page.locator('[data-testid="lightbox-title"]')
    await expect(lightboxTitle).toContainText('Image 1 of 10')

    // Take screenshot
    await page.screenshot({
      path: 'frontend/tests/screenshots/image-lightbox-open.png',
      fullPage: true
    })

    // Navigate next
    const nextButton = page.locator('[data-testid="lightbox-next"]')
    await expect(nextButton).toBeVisible()
    await nextButton.click()
    await page.waitForTimeout(500)

    // Verify title updated
    await expect(lightboxTitle).toContainText('Image 2 of 10')

    // Navigate previous
    const prevButton = page.locator('[data-testid="lightbox-prev"]')
    await expect(prevButton).toBeVisible()
    await prevButton.click()
    await page.waitForTimeout(500)

    // Verify title back to 1
    await expect(lightboxTitle).toContainText('Image 1 of 10')

    // Close lightbox
    const closeButton = page.locator('[data-testid="lightbox-close"]')
    await expect(closeButton).toBeVisible()
    await closeButton.click()
    await page.waitForTimeout(500)

    // Verify lightbox is closed
    await expect(lightbox).not.toBeVisible()
  })

  test('should display image metadata in lightbox', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate images
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Open lightbox
    await page.waitForSelector('[data-testid="image-card-0"]', { timeout: 5000 })
    await page.locator('[data-testid="image-card-0"]').click()
    await page.waitForTimeout(500)

    // Verify lightbox info panel
    const lightboxInfo = page.locator('[data-testid="lightbox-info"]')
    await expect(lightboxInfo).toBeVisible()

    // Verify details
    const lightboxDetails = page.locator('[data-testid="lightbox-details"]')
    await expect(lightboxDetails).toBeVisible()
    await expect(lightboxDetails).toContainText('512x512')
  })

  test('should handle empty image state', async ({ page }) => {
    // Override to return empty batch
    await page.route('**/api/v1/synthetic/image/generate', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          images: [],
          batch_analysis: {
            avg_complexity: 0,
            avg_entropy: 0,
            avg_compressibility: 0
          },
          processing_time: 0
        })
      })
    })

    await page.goto('http://localhost:8449', { waitUntil: 'domcontentloaded' })
    // Wait removed - using domcontentloaded
    // Tab content already loaded by beforeEach

    // Navigate to image tab
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(500)

    // Verify empty state message
    const imageGallery = page.locator('[data-testid="image-gallery-section"]')
    await expect(imageGallery).toBeVisible()

    const emptyMessage = imageGallery.locator('text=No images generated yet')
    await expect(emptyMessage).toBeVisible()
  })

  test('should delete batch of selected images', async ({ page }) => {
    // Tab content already loaded by beforeEach

    // Generate images
    const imageTab = page.locator('[data-testid="image-tab"]')
    await imageTab.click()
    await page.waitForTimeout(300)

    const generateButton = page.locator('[data-testid="generate-button"]')
    await generateButton.click()
    await page.waitForTimeout(2000)

    // Select images
    await page.waitForSelector('[data-testid="image-card-0"]', { timeout: 5000 })
    await page.locator('[data-testid="image-card-0"]').locator('input[type="checkbox"]').check()
    await page.waitForTimeout(200)
    await page.locator('[data-testid="image-card-1"]').locator('input[type="checkbox"]').check()
    await page.waitForTimeout(200)

    // Verify image count before delete
    let imageCount = page.locator('[data-testid="image-count"]')
    await expect(imageCount).toContainText('10 images')

    // Click batch delete
    const batchDeleteButton = page.locator('[data-testid="batch-delete-button"]')
    await batchDeleteButton.click()
    await page.waitForTimeout(500)

    // Verify image count decreased
    imageCount = page.locator('[data-testid="image-count"]')
    await expect(imageCount).toContainText('8 images')

    // Verify batch actions hidden
    const batchActions = page.locator('[data-testid="batch-actions"]')
    await expect(batchActions).not.toBeVisible()
  })
})
