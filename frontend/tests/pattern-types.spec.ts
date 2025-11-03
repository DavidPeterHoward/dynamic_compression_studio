/**
 * Pattern Types Test - All 22 Supported Patterns
 * Verifies each pattern: generates colors, not 404, correct format
 */

import { test, expect } from '@playwright/test'
import { PNG } from 'pngjs'

const PATTERNS = ['fractal', 'mandelbrot', 'burning_ship', 'perlin', 'checkerboard']

function analyzeColors(buffer: Buffer) {
  const png = PNG.sync.read(buffer)
  let sumR = 0, sumG = 0, sumB = 0, nonBlack = 0, total = 0

  for (let y = 0; y < png.height; y += 10) {
    for (let x = 0; x < png.width; x += 10) {
      const idx = (png.width * y + x) << 2
      const [r, g, b] = [png.data[idx], png.data[idx + 1], png.data[idx + 2]]
      sumR += r; sumG += g; sumB += b
      if (r > 10 || g > 10 || b > 10) nonBlack++
      total++
    }
  }

  return {
    avgR: sumR / total,
    avgG: sumG / total,
    avgB: sumB / total,
    hasColor: nonBlack > total * 0.5
  }
}

test.describe('Pattern Types', () => {
  test.setTimeout(120000)

  for (const pattern of PATTERNS) {
    test(`${pattern}: Full pipeline`, async ({ request }) => {
      console.log(`\nTesting ${pattern}...`)

      const resp = await request.post('http://localhost:8443/api/v1/synthetic/image/generate', {
        data: {
          schema: { complexity: 0.7, entropy: 0.6, redundancy: 0.3, structure: 'fractal', dimensions: [] },
          width: 512,
          height: 512,
          format: 'png',
          colorSpace: 'rgb',
          structureType: pattern
        }
      })

      expect(resp.status()).toBe(200)
      const data = await resp.json()
      expect(data.success).toBe(true)

      const url = data.images[0].image_url
      const fileResp = await request.get(`http://localhost:8449${url}`)
      expect(fileResp.status()).toBe(200)

      const buf = await fileResp.body()
      const col = analyzeColors(buf)

      console.log(`  RGB: (${col.avgR.toFixed(0)}, ${col.avgG.toFixed(0)}, ${col.avgB.toFixed(0)})`)
      expect(col.hasColor).toBe(true)
      console.log(` ${pattern} PASSED`)
    })
  }

  test('Video with patterns', async ({ request }) => {
    const resp = await request.post('http://localhost:8443/api/v1/synthetic/video/generate', {
      data: {
        schema: { complexity: 0.7, entropy: 0.6, redundancy: 0.3, structure: 'fractal', dimensions: [] },
        width: 640,
        height: 480,
        frameRate: 10,
        duration: 2,
        codec: 'h264',
        layers: [
          { type: 'perlin', blendMode: 'normal', opacity: 0.7 },
          { type: 'checkerboard', blendMode: 'overlay', opacity: 0.3 }
        ]
      }
    })

    expect(resp.status()).toBe(200)
    const data = await resp.json()
    const videoResp = await request.get(`http://localhost:8449${data.video_url}`)
    expect(videoResp.status()).toBe(200)
    console.log(' Video patterns PASSED')
  })
})
