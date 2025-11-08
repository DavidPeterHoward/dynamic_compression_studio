import { expect, Page, test } from '@playwright/test'

// Helpers
async function getAverageColorFromElement(page: Page, selector: string) {
  return await page.evaluate(async (sel) => {
    const el = document.querySelector(sel) as HTMLElement | null
    if (!el) return null

    // Try to find <img> or <video> inside the element
    const img = el.querySelector('img') as HTMLImageElement | null
    const video = el.querySelector('video') as HTMLVideoElement | null

    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')!

    function avgFromImage(image: HTMLImageElement) {
      const w = Math.min(image.naturalWidth || 0, 320)
      const h = Math.min(image.naturalHeight || 0, 180)
      if (!w || !h) return null
      canvas.width = w
      canvas.height = h
      ctx.drawImage(image, 0, 0, w, h)
      const data = ctx.getImageData(0, 0, w, h).data
      let r = 0, g = 0, b = 0, count = 0
      for (let i = 0; i < data.length; i += 4) {
        r += data[i]
        g += data[i + 1]
        b += data[i + 2]
        count++
      }
      return { r: Math.round(r / count), g: Math.round(g / count), b: Math.round(b / count) }
    }

    function avgFromVideo(vid: HTMLVideoElement) {
      const w = Math.min(vid.videoWidth || 0, 320)
      const h = Math.min(vid.videoHeight || 0, 180)
      if (!w || !h) return null
      canvas.width = w
      canvas.height = h
      // draw current frame
      // Note: requires same-origin media; otherwise will be tainted
      try {
        ctx.drawImage(vid, 0, 0, w, h)
      } catch {
        return null
      }
      const data = ctx.getImageData(0, 0, w, h).data
      let r = 0, g = 0, b = 0, count = 0
      for (let i = 0; i < data.length; i += 4) {
        r += data[i]
        g += data[i + 1]
        b += data[i + 2]
        count++
      }
      return { r: Math.round(r / count), g: Math.round(g / count), b: Math.round(b / count) }
    }

    if (img && (img.complete || img.naturalWidth > 0)) {
      return avgFromImage(img)
    }
    if (video && !video.paused) {
      return avgFromVideo(video)
    }
    return null
  }, selector)
}

test.describe('Experiments > Synthetic Data - UI and media coverage', () => {
  test.beforeEach(async ({ page }) => {
    // Base URL should be configured in playwright config; fallback to localhost
    await page.goto('/')
    await expect(page.getByText('Synthetic')).toBeVisible()

    // Open Experiments tab if needed
    // Assuming main page has tabs or navigation to Experiments view
    const experimentsTab = page.getByRole('button', { name: /Experiments/i })
    if (await experimentsTab.isVisible()) {
      await experimentsTab.click()
    }

    // Switch to Synthetic Data sub-tab if required
    const syntheticDataTab = page.getByRole('button', { name: /Synthetic Data/i })
    if (await syntheticDataTab.isVisible()) {
      await syntheticDataTab.click()
    }

    await expect(page.getByText('Synthetic Content Generation').or(page.getByText('Synthetic Data Generation'))).toBeVisible()
  })

  test('Media type tabs render and switch with counters', async ({ page }) => {
    const dataBtn = page.getByRole('button', { name: /Data Files/i })
    const videoBtn = page.getByRole('button', { name: /^Video$/i })
    const imageBtn = page.getByRole('button', { name: /^Images$/i })
    const audioBtn = page.getByRole('button', { name: /^Audio$/i })

    await expect(dataBtn).toBeVisible()
    await expect(videoBtn).toBeVisible()
    await expect(imageBtn).toBeVisible()
    await expect(audioBtn).toBeVisible()

    await videoBtn.click()
    await imageBtn.click()
    await audioBtn.click()
    await dataBtn.click()
  })

  test('Data: pattern grid and file extensions filter work', async ({ page }) => {
    // Ensure on Data tab
    await page.getByRole('button', { name: /Data Files/i }).click()

    // Toggle at least one pattern button
    const anyPattern = page.locator('button', { hasText: /Data|Text|CSV|JSON|Log|Source|Markdown/i }).first()
    if (await anyPattern.count()) {
      await anyPattern.click()
    }

    // Filter by a category and toggle an extension card
    const filterButtons = page.locator('button', { hasText: /(All|Text|Data|Code|Binary|Archive)/ })
    const count = await filterButtons.count()
    for (let i = 0; i < count; i++) {
      await filterButtons.nth(i).click()
    }

    const anyExtension = page.locator('button').filter({ hasText: '.' }).first()
    if (await anyExtension.count()) {
      await anyExtension.click()
    }
  })

  test('Image: iterate all pattern and format dropdown options', async ({ page }) => {
    await page.getByRole('button', { name: /^Images$/i }).click()

    // Pattern Type dropdown
    const patternSelect = page.getByLabel('Pattern Type')
    await expect(patternSelect).toBeVisible()
    await patternSelect.click()

    // Grab all options dynamically and select each
    const options = page.locator('select:has(>option) >> option')
    const totalOptions = await options.count()
    for (let i = 0; i < totalOptions; i++) {
      const value = await options.nth(i).getAttribute('value')
      if (value) {
        await patternSelect.selectOption(value)
      }
    }

    // Format dropdown
    const formatSelect = page.getByLabel('Format')
    await expect(formatSelect).toBeVisible()
    await formatSelect.selectOption('png')
    await formatSelect.selectOption('jpg')
    await formatSelect.selectOption('webp')
  })

  test('Audio: iterate waveform dropdown and numeric controls', async ({ page }) => {
    await page.getByRole('button', { name: /^Audio$/i }).click()

    const waveformSelect = page.getByLabel('Waveform')
    await expect(waveformSelect).toBeVisible()
    await waveformSelect.selectOption('sine')
    await waveformSelect.selectOption('square')
    await waveformSelect.selectOption('sawtooth')
    await waveformSelect.selectOption('triangle')

    const frequencyInput = page.getByLabel('Frequency (Hz)')
    await frequencyInput.fill('440')
    await expect(frequencyInput).toHaveValue('440')

    const durationInput = page.getByLabel('Duration (seconds)')
    await durationInput.fill('5')
    await expect(durationInput).toHaveValue('5')
  })

  test('Video: resolution and frame rate inputs respond', async ({ page }) => {
    await page.getByRole('button', { name: /^Video$/i }).click()

    const width = page.getByLabel('Resolution').locator('input').first()
    const height = page.getByLabel('Resolution').locator('input').nth(1)
    await width.fill('640')
    await height.fill('480')

    const duration = page.getByLabel('Duration (seconds)')
    await duration.fill('5')

    const frameRate = page.getByLabel('Frame Rate')
    await frameRate.fill('30')
  })

  test('Generated content listing displays and optional color recognition works', async ({ page }) => {
    // The page loads previously generated media on mount; if present, validate
    const gridCards = page.locator('.glass-dark').filter({ has: page.locator('button[title="View Details"]') })
    const count = await gridCards.count()
    if (count === 0) test.skip(true, 'No generated media available to validate visuals')

    // Open first card
    await gridCards.first().click()

    // If modal has image/video, compute average color and assert brightness > 0
    const modal = page.locator('.glass').last()
    await expect(modal).toBeVisible()

    // Prefer image first
    const avg = await getAverageColorFromElement(page, '.glass img, .glass video')
    if (avg) {
      const brightness = Math.round((avg.r + avg.g + avg.b) / 3)
      expect(brightness).toBeGreaterThan(1)
    }

    // Close modal
    const closeBtn = page.getByRole('button').filter({ hasText: 'X' }).first()
    if (await closeBtn.isVisible()) await closeBtn.click()
  })
})









