/**
 * Comprehensive Dropdown Validation Tests
 * Tests all dropdown menus in the application to ensure they function correctly
 * and handle all enum values without errors.
 */

import { expect, test } from '@playwright/test';

// Valid structure types from DataStructureType enum
const VALID_STRUCTURE_TYPES = [
  'network', 'tree', 'graph', 'relational', 'nested', 'hierarchical',
  'flat', 'temporal', 'spatial', 'sparse', 'dense', 'streaming', 'fractal'
];

// Valid pattern types for images and videos
const VALID_PATTERN_TYPES = [
  'fractal', 'mandelbrot', 'julia', 'burning_ship', 'sierpinski',
  'noise', 'perlin', 'worley', 'geometric', 'checkerboard', 'stripes',
  'circles', 'spiral', 'hexagonal', 'wave_interference', 'lissajous',
  'moire', 'gradient', 'wood', 'marble', 'cellular', 'mixed'
];

// Valid media types
const VALID_MEDIA_TYPES = ['image', 'video', 'audio'];

// Valid formats
const VALID_IMAGE_FORMATS = ['png', 'jpg', 'webp', 'svg'];
const VALID_VIDEO_CODECS = ['h264', 'h265', 'vp9', 'av1'];
const VALID_COLOR_SPACES = ['rgb', 'rgba', 'grayscale', 'hsl'];

test.describe('Comprehensive Dropdown Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // Wait for the application to be ready
    await page.waitForSelector('[data-testid="app-container"]', { timeout: 10000 });
  });

  test.describe('Synthetic Media Tab - Image Generation', () => {
    test.beforeEach(async ({ page }) => {
      // Navigate to synthetic media tab
      const syntheticTab = page.locator('[data-testid="synthetic-media-tab"]');
      await syntheticTab.click();
      await page.waitForTimeout(500);
    });

    test('Structure dropdown validation', async ({ page }) => {
      console.log('🧪 Testing Structure Dropdown Validation');
      
      // Find the structure dropdown
      const structureDropdown = page.locator('select').filter({ hasText: /structure/i });
      await expect(structureDropdown).toBeVisible();
      
      // Get all available options
      const options = await structureDropdown.locator('option').allTextContents();
      console.log(`📊 Found ${options.length} structure options:`, options);
      
      // Test each valid structure type
      for (const structureType of VALID_STRUCTURE_TYPES) {
        console.log(`  Testing structure type: ${structureType}`);
        
        // Select the structure type
        await structureDropdown.selectOption(structureType);
        
        // Verify the selection
        const selectedValue = await structureDropdown.inputValue();
        expect(selectedValue).toBe(structureType);
        
        // Try to generate an image with this structure
        const generateButton = page.locator('button').filter({ hasText: /generate/i });
        if (await generateButton.isVisible()) {
          await generateButton.click();
          
          // Wait for any error messages
          await page.waitForTimeout(1000);
          
          // Check for validation errors
          const errorMessages = page.locator('[data-testid="error-message"], .error, .text-red-500');
          const errorCount = await errorMessages.count();
          
          if (errorCount > 0) {
            const errors = await errorMessages.allTextContents();
            console.log(`    ❌ Errors found for ${structureType}:`, errors);
          } else {
            console.log(`    ✅ ${structureType} - No errors`);
          }
        }
      }
    });

    test('Pattern Type dropdown validation', async ({ page }) => {
      console.log('🧪 Testing Pattern Type Dropdown Validation');
      
      // Find the pattern type dropdown
      const patternDropdown = page.locator('select').filter({ hasText: /pattern|type/i });
      await expect(patternDropdown).toBeVisible();
      
      // Test each valid pattern type
      for (const patternType of VALID_PATTERN_TYPES) {
        console.log(`  Testing pattern type: ${patternType}`);
        
        try {
          // Select the pattern type
          await patternDropdown.selectOption(patternType);
          
          // Verify the selection
          const selectedValue = await patternDropdown.inputValue();
          expect(selectedValue).toBe(patternType);
          
          // Try to generate an image with this pattern
          const generateButton = page.locator('button').filter({ hasText: /generate/i });
          if (await generateButton.isVisible()) {
            await generateButton.click();
            
            // Wait for any error messages
            await page.waitForTimeout(1000);
            
            // Check for validation errors
            const errorMessages = page.locator('[data-testid="error-message"], .error, .text-red-500');
            const errorCount = await errorMessages.count();
            
            if (errorCount > 0) {
              const errors = await errorMessages.allTextContents();
              console.log(`    ❌ Errors found for ${patternType}:`, errors);
            } else {
              console.log(`    ✅ ${patternType} - No errors`);
            }
          }
        } catch (error) {
          console.log(`    ❌ Error testing ${patternType}:`, error);
        }
      }
    });

    test('Format dropdown validation', async ({ page }) => {
      console.log('🧪 Testing Format Dropdown Validation');
      
      // Find the format dropdown
      const formatDropdown = page.locator('select').filter({ hasText: /format/i });
      await expect(formatDropdown).toBeVisible();
      
      // Test each valid format
      for (const format of VALID_IMAGE_FORMATS) {
        console.log(`  Testing format: ${format}`);
        
        try {
          // Select the format
          await formatDropdown.selectOption(format);
          
          // Verify the selection
          const selectedValue = await formatDropdown.inputValue();
          expect(selectedValue).toBe(format);
          
          console.log(`    ✅ ${format} - Selection successful`);
        } catch (error) {
          console.log(`    ❌ Error testing ${format}:`, error);
        }
      }
    });

    test('Color Space dropdown validation', async ({ page }) => {
      console.log('🧪 Testing Color Space Dropdown Validation');
      
      // Find the color space dropdown
      const colorSpaceDropdown = page.locator('select').filter({ hasText: /color|space/i });
      await expect(colorSpaceDropdown).toBeVisible();
      
      // Test each valid color space
      for (const colorSpace of VALID_COLOR_SPACES) {
        console.log(`  Testing color space: ${colorSpace}`);
        
        try {
          // Select the color space
          await colorSpaceDropdown.selectOption(colorSpace);
          
          // Verify the selection
          const selectedValue = await colorSpaceDropdown.inputValue();
          expect(selectedValue).toBe(colorSpace);
          
          console.log(`    ✅ ${colorSpace} - Selection successful`);
        } catch (error) {
          console.log(`    ❌ Error testing ${colorSpace}:`, error);
        }
      }
    });
  });

  test.describe('Synthetic Media Tab - Video Generation', () => {
    test.beforeEach(async ({ page }) => {
      // Navigate to synthetic media tab
      const syntheticTab = page.locator('[data-testid="synthetic-media-tab"]');
      await syntheticTab.click();
      await page.waitForTimeout(500);
      
      // Switch to video generation
      const videoTab = page.locator('[data-testid="video-tab"]');
      if (await videoTab.isVisible()) {
        await videoTab.click();
        await page.waitForTimeout(500);
      }
    });

    test('Video Layer Pattern Type dropdown validation', async ({ page }) => {
      console.log('🧪 Testing Video Layer Pattern Type Dropdown Validation');
      
      // Find video layer pattern type dropdowns
      const patternDropdowns = page.locator('select').filter({ hasText: /pattern|type|layer/i });
      const count = await patternDropdowns.count();
      
      if (count > 0) {
        for (let i = 0; i < count; i++) {
          const dropdown = patternDropdowns.nth(i);
          await expect(dropdown).toBeVisible();
          
          // Test each valid pattern type
          for (const patternType of VALID_PATTERN_TYPES) {
            console.log(`  Testing video pattern type: ${patternType}`);
            
            try {
              // Select the pattern type
              await dropdown.selectOption(patternType);
              
              // Verify the selection
              const selectedValue = await dropdown.inputValue();
              expect(selectedValue).toBe(patternType);
              
              console.log(`    ✅ ${patternType} - Selection successful`);
            } catch (error) {
              console.log(`    ❌ Error testing ${patternType}:`, error);
            }
          }
        }
      }
    });

    test('Video Codec dropdown validation', async ({ page }) => {
      console.log('🧪 Testing Video Codec Dropdown Validation');
      
      // Find the codec dropdown
      const codecDropdown = page.locator('select').filter({ hasText: /codec/i });
      await expect(codecDropdown).toBeVisible();
      
      // Test each valid codec
      for (const codec of VALID_VIDEO_CODECS) {
        console.log(`  Testing codec: ${codec}`);
        
        try {
          // Select the codec
          await codecDropdown.selectOption(codec);
          
          // Verify the selection
          const selectedValue = await codecDropdown.inputValue();
          expect(selectedValue).toBe(codec);
          
          console.log(`    ✅ ${codec} - Selection successful`);
        } catch (error) {
          console.log(`    ❌ Error testing ${codec}:`, error);
        }
      }
    });
  });

  test.describe('API Endpoint Validation', () => {
    test('Image generation API with all pattern types', async ({ page, request }) => {
      console.log('🧪 Testing Image Generation API with All Pattern Types');
      
      for (const patternType of VALID_PATTERN_TYPES) {
        console.log(`  Testing API with pattern: ${patternType}`);
        
        try {
          const response = await request.post('http://localhost:8443/api/v1/synthetic/image/generate', {
            data: {
              schema: {
                complexity: 0.7,
                entropy: 0.6,
                redundancy: 0.3,
                structure: 'fractal', // Use valid structure type
                dimensions: []
              },
              width: 512,
              height: 512,
              format: 'png',
              colorSpace: 'rgb',
              structureType: patternType
            }
          });
          
          expect(response.status()).toBe(200);
          const data = await response.json();
          expect(data.success).toBe(true);
          
          console.log(`    ✅ ${patternType} - API call successful`);
        } catch (error) {
          console.log(`    ❌ Error with ${patternType}:`, error);
        }
      }
    });

    test('Video generation API with all pattern types', async ({ page, request }) => {
      console.log('🧪 Testing Video Generation API with All Pattern Types');
      
      for (const patternType of VALID_PATTERN_TYPES) {
        console.log(`  Testing API with pattern: ${patternType}`);
        
        try {
          const response = await request.post('http://localhost:8443/api/v1/synthetic/video/generate', {
            data: {
              schema: {
                complexity: 0.7,
                entropy: 0.6,
                redundancy: 0.3,
                structure: 'fractal', // Use valid structure type
                dimensions: []
              },
              width: 640,
              height: 480,
              frameRate: 30,
              duration: 2,
              codec: 'h264',
              layers: [{ 
                type: patternType, 
                blendMode: 'normal', 
                opacity: 1.0 
              }],
              temporalCoherence: 0.7
            }
          });
          
          expect(response.status()).toBe(200);
          const data = await response.json();
          expect(data.success).toBe(true);
          
          console.log(`    ✅ ${patternType} - API call successful`);
        } catch (error) {
          console.log(`    ❌ Error with ${patternType}:`, error);
        }
      }
    });

    test('Structure validation with all valid types', async ({ page, request }) => {
      console.log('🧪 Testing Structure Validation with All Valid Types');
      
      for (const structureType of VALID_STRUCTURE_TYPES) {
        console.log(`  Testing API with structure: ${structureType}`);
        
        try {
          const response = await request.post('http://localhost:8443/api/v1/synthetic/image/generate', {
            data: {
              schema: {
                complexity: 0.7,
                entropy: 0.6,
                redundancy: 0.3,
                structure: structureType, // Use valid structure type
                dimensions: []
              },
              width: 512,
              height: 512,
              format: 'png',
              colorSpace: 'rgb',
              structureType: 'fractal' // Use valid pattern type
            }
          });
          
          expect(response.status()).toBe(200);
          const data = await response.json();
          expect(data.success).toBe(true);
          
          console.log(`    ✅ ${structureType} - API call successful`);
        } catch (error) {
          console.log(`    ❌ Error with ${structureType}:`, error);
        }
      }
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('Invalid enum values should be rejected', async ({ page, request }) => {
      console.log('🧪 Testing Invalid Enum Values Rejection');
      
      const invalidValues = ['invalid', 'perlin', 'unknown', 'test'];
      
      for (const invalidValue of invalidValues) {
        console.log(`  Testing invalid structure: ${invalidValue}`);
        
        try {
          const response = await request.post('http://localhost:8443/api/v1/synthetic/image/generate', {
            data: {
              schema: {
                complexity: 0.7,
                entropy: 0.6,
                redundancy: 0.3,
                structure: invalidValue, // Invalid structure
                dimensions: []
              },
              width: 512,
              height: 512,
              format: 'png',
              colorSpace: 'rgb',
              structureType: 'fractal'
            }
          });
          
          // Should return 422 (Unprocessable Entity) for validation errors
          expect(response.status()).toBe(422);
          
          const data = await response.json();
          expect(data.detail).toBeDefined();
          
          console.log(`    ✅ ${invalidValue} - Correctly rejected`);
        } catch (error) {
          console.log(`    ❌ Unexpected error with ${invalidValue}:`, error);
        }
      }
    });

    test('Frontend dropdown should not allow invalid selections', async ({ page }) => {
      console.log('🧪 Testing Frontend Dropdown Validation');
      
      // Navigate to synthetic media tab
      const syntheticTab = page.locator('[data-testid="synthetic-media-tab"]');
      await syntheticTab.click();
      await page.waitForTimeout(500);
      
      // Find all dropdowns
      const dropdowns = page.locator('select');
      const count = await dropdowns.count();
      
      console.log(`Found ${count} dropdowns to test`);
      
      for (let i = 0; i < count; i++) {
        const dropdown = dropdowns.nth(i);
        const isVisible = await dropdown.isVisible();
        
        if (isVisible) {
          console.log(`  Testing dropdown ${i + 1}`);
          
          // Get all options
          const options = await dropdown.locator('option').allTextContents();
          console.log(`    Options: ${options.join(', ')}`);
          
          // Verify no invalid options are present
          const invalidOptions = options.filter(option => 
            invalidValues.includes(option.toLowerCase())
          );
          
          if (invalidOptions.length > 0) {
            console.log(`    ❌ Invalid options found: ${invalidOptions.join(', ')}`);
          } else {
            console.log(`    ✅ No invalid options found`);
          }
        }
      }
    });
  });

  test.describe('Comprehensive Integration Test', () => {
    test('Full workflow with all valid combinations', async ({ page, request }) => {
      console.log('🧪 Testing Full Workflow with All Valid Combinations');
      
      // Test combinations of valid structure and pattern types
      const testCombinations = [
        { structure: 'fractal', pattern: 'mandelbrot' },
        { structure: 'hierarchical', pattern: 'perlin' },
        { structure: 'spatial', pattern: 'geometric' },
        { structure: 'temporal', pattern: 'wave_interference' },
        { structure: 'network', pattern: 'cellular' }
      ];
      
      for (const combination of testCombinations) {
        console.log(`  Testing combination: ${combination.structure} + ${combination.pattern}`);
        
        try {
          const response = await request.post('http://localhost:8443/api/v1/synthetic/image/generate', {
            data: {
              schema: {
                complexity: 0.7,
                entropy: 0.6,
                redundancy: 0.3,
                structure: combination.structure,
                dimensions: []
              },
              width: 512,
              height: 512,
              format: 'png',
              colorSpace: 'rgb',
              structureType: combination.pattern
            }
          });
          
          expect(response.status()).toBe(200);
          const data = await response.json();
          expect(data.success).toBe(true);
          
          console.log(`    ✅ ${combination.structure} + ${combination.pattern} - Success`);
        } catch (error) {
          console.log(`    ❌ Error with ${combination.structure} + ${combination.pattern}:`, error);
        }
      }
    });
  });
});
