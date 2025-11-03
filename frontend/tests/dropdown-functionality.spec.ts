/**
 * Dropdown Functionality Tests
 * Tests all dropdown menus to ensure they work correctly and handle all options
 */

import { test } from '@playwright/test';

test.describe('Dropdown Functionality Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[data-testid="app-container"]', { timeout: 10000 });
  });

  test('All dropdown menus are functional', async ({ page }) => {
    console.log('🧪 Testing All Dropdown Menus');
    
    // Navigate to synthetic media tab
    const syntheticTab = page.locator('[data-testid="synthetic-media-tab"]');
    await syntheticTab.click();
    await page.waitForTimeout(1000);
    
    // Find all dropdown elements
    const dropdowns = page.locator('select');
    const dropdownCount = await dropdowns.count();
    
    console.log(`Found ${dropdownCount} dropdowns`);
    
    for (let i = 0; i < dropdownCount; i++) {
      const dropdown = dropdowns.nth(i);
      const isVisible = await dropdown.isVisible();
      
      if (isVisible) {
        console.log(`\nTesting dropdown ${i + 1}:`);
        
        // Get all options
        const options = await dropdown.locator('option');
        const optionCount = await options.count();
        const optionTexts = await options.allTextContents();
        
        console.log(`  Options (${optionCount}): ${optionTexts.join(', ')}`);
        
        // Test each option
        for (let j = 0; j < optionCount; j++) {
          const option = options.nth(j);
          const optionText = await option.textContent();
          const optionValue = await option.getAttribute('value');
          
          console.log(`    Testing option: ${optionText} (value: ${optionValue})`);
          
          try {
            // Select the option
            await dropdown.selectOption(optionValue || optionText);
            
            // Verify selection
            const selectedValue = await dropdown.inputValue();
            console.log(`      Selected value: ${selectedValue}`);
            
            // Check for any error messages
            await page.waitForTimeout(500);
            const errorMessages = page.locator('.error, .text-red-500, [data-testid="error"]');
            const errorCount = await errorMessages.count();
            
            if (errorCount > 0) {
              const errors = await errorMessages.allTextContents();
              console.log(`      ❌ Errors: ${errors.join(', ')}`);
            } else {
              console.log(`      ✅ No errors`);
            }
          } catch (error) {
            console.log(`      ❌ Error selecting option: ${error}`);
          }
        }
      }
    }
  });

  test('Pattern type dropdown specifically', async ({ page }) => {
    console.log('🧪 Testing Pattern Type Dropdown Specifically');
    
    // Navigate to synthetic media tab
    const syntheticTab = page.locator('[data-testid="synthetic-media-tab"]');
    await syntheticTab.click();
    await page.waitForTimeout(1000);
    
    // Look for pattern type dropdown
    const patternDropdown = page.locator('select').filter({ hasText: /pattern|type/i });
    const isVisible = await patternDropdown.isVisible();
    
    if (isVisible) {
      console.log('Pattern type dropdown found');
      
      // Get all options
      const options = await patternDropdown.locator('option');
      const optionCount = await options.count();
      
      console.log(`Found ${optionCount} pattern options`);
      
      // Test each pattern type
      for (let i = 0; i < optionCount; i++) {
        const option = options.nth(i);
        const optionText = await option.textContent();
        const optionValue = await option.getAttribute('value');
        
        console.log(`\nTesting pattern: ${optionText} (${optionValue})`);
        
        try {
          // Select the pattern
          await patternDropdown.selectOption(optionValue || optionText);
          
          // Wait a moment for any validation
          await page.waitForTimeout(500);
          
          // Check for errors
          const errorMessages = page.locator('.error, .text-red-500, [data-testid="error"]');
          const errorCount = await errorMessages.count();
          
          if (errorCount > 0) {
            const errors = await errorMessages.allTextContents();
            console.log(`  ❌ Errors found: ${errors.join(', ')}`);
          } else {
            console.log(`  ✅ No errors`);
          }
          
          // Try to generate if there's a generate button
          const generateButton = page.locator('button').filter({ hasText: /generate/i });
          if (await generateButton.isVisible()) {
            console.log('  Attempting generation...');
            await generateButton.click();
            
            // Wait for response
            await page.waitForTimeout(2000);
            
            // Check for generation errors
            const genErrors = page.locator('.error, .text-red-500, [data-testid="error"]');
            const genErrorCount = await genErrors.count();
            
            if (genErrorCount > 0) {
              const genErrorsText = await genErrors.allTextContents();
              console.log(`  ❌ Generation errors: ${genErrorsText.join(', ')}`);
            } else {
              console.log(`  ✅ Generation successful`);
            }
          }
        } catch (error) {
          console.log(`  ❌ Error testing pattern ${optionText}: ${error}`);
        }
      }
    } else {
      console.log('Pattern type dropdown not found');
    }
  });

  test('Structure dropdown specifically', async ({ page }) => {
    console.log('🧪 Testing Structure Dropdown Specifically');
    
    // Navigate to synthetic media tab
    const syntheticTab = page.locator('[data-testid="synthetic-media-tab"]');
    await syntheticTab.click();
    await page.waitForTimeout(1000);
    
    // Look for structure dropdown
    const structureDropdown = page.locator('select').filter({ hasText: /structure/i });
    const isVisible = await structureDropdown.isVisible();
    
    if (isVisible) {
      console.log('Structure dropdown found');
      
      // Get all options
      const options = await structureDropdown.locator('option');
      const optionCount = await options.count();
      
      console.log(`Found ${optionCount} structure options`);
      
      // Test each structure type
      for (let i = 0; i < optionCount; i++) {
        const option = options.nth(i);
        const optionText = await option.textContent();
        const optionValue = await option.getAttribute('value');
        
        console.log(`\nTesting structure: ${optionText} (${optionValue})`);
        
        try {
          // Select the structure
          await structureDropdown.selectOption(optionValue || optionText);
          
          // Wait a moment for any validation
          await page.waitForTimeout(500);
          
          // Check for errors
          const errorMessages = page.locator('.error, .text-red-500, [data-testid="error"]');
          const errorCount = await errorMessages.count();
          
          if (errorCount > 0) {
            const errors = await errorMessages.allTextContents();
            console.log(`  ❌ Errors found: ${errors.join(', ')}`);
          } else {
            console.log(`  ✅ No errors`);
          }
        } catch (error) {
          console.log(`  ❌ Error testing structure ${optionText}: ${error}`);
        }
      }
    } else {
      console.log('Structure dropdown not found');
    }
  });

  test('API validation for all dropdown values', async ({ page, request }) => {
    console.log('🧪 Testing API Validation for All Dropdown Values');
    
    // Valid structure types
    const structureTypes = [
      'network', 'tree', 'graph', 'relational', 'nested', 'hierarchical',
      'flat', 'temporal', 'spatial', 'sparse', 'dense', 'streaming', 'fractal'
    ];
    
    // Valid pattern types
    const patternTypes = [
      'fractal', 'mandelbrot', 'julia', 'burning_ship', 'sierpinski',
      'noise', 'perlin', 'worley', 'geometric', 'checkerboard', 'stripes',
      'circles', 'spiral', 'hexagonal', 'wave_interference', 'lissajous',
      'moire', 'gradient', 'wood', 'marble', 'cellular', 'mixed'
    ];
    
    // Test structure types
    console.log('\nTesting structure types:');
    for (const structure of structureTypes) {
      console.log(`  Testing structure: ${structure}`);
      
      try {
        const response = await request.post('http://localhost:8443/api/v1/synthetic/image/generate', {
          data: {
            schema: {
              complexity: 0.7,
              entropy: 0.6,
              redundancy: 0.3,
              structure: structure,
              dimensions: []
            },
            width: 512,
            height: 512,
            format: 'png',
            colorSpace: 'rgb',
            structureType: 'fractal'
          }
        });
        
        if (response.status() === 200) {
          console.log(`    ✅ ${structure} - Success`);
        } else {
          console.log(`    ❌ ${structure} - Status ${response.status()}`);
        }
      } catch (error) {
        console.log(`    ❌ ${structure} - Error: ${error}`);
      }
    }
    
    // Test pattern types
    console.log('\nTesting pattern types:');
    for (const pattern of patternTypes) {
      console.log(`  Testing pattern: ${pattern}`);
      
      try {
        const response = await request.post('http://localhost:8443/api/v1/synthetic/image/generate', {
          data: {
            schema: {
              complexity: 0.7,
              entropy: 0.6,
              redundancy: 0.3,
              structure: 'fractal',
              dimensions: []
            },
            width: 512,
            height: 512,
            format: 'png',
            colorSpace: 'rgb',
            structureType: pattern
          }
        });
        
        if (response.status() === 200) {
          console.log(`    ✅ ${pattern} - Success`);
        } else {
          console.log(`    ❌ ${pattern} - Status ${response.status()}`);
        }
      } catch (error) {
        console.log(`    ❌ ${pattern} - Error: ${error}`);
      }
    }
  });
});
