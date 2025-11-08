/**
 * Playwright Configuration for Agent Debate Construction E2E Tests
 *
 * Comprehensive configuration for testing the agent debate construction workflow
 * across multiple browsers and environments.
 */

import { defineConfig, devices } from '@playwright/test'

const config = defineConfig({
  testDir: './tests',
  outputDir: './test-results',
  snapshotDir: './test-snapshots',

  // Global test timeout (60 seconds)
  timeout: 60000,

  // Expect timeout for assertions
  expect: {
    timeout: 10000,
  },

  // Run tests in files in parallel
  fullyParallel: false, // Sequential execution for state-dependent tests

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Reporter to use
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['github'],
    ['list'],
  ],

  // Shared settings for all the projects below
  use: {
    // Base URL for all tests
    baseURL: process.env.TEST_BASE_URL || 'http://localhost:8449',

    // API URL for backend calls
    extraHTTPHeaders: {
      'X-API-URL': process.env.TEST_API_URL || 'http://localhost:8443',
    },

    // Collect trace when retrying the failed test
    trace: 'on-first-retry',

    // Take screenshot only when test fails
    screenshot: 'only-on-failure',

    // Record video for failed tests
    video: 'retain-on-failure',

    // Browser context options
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,

    // Action timeout
    actionTimeout: 10000,

    // Navigation timeout
    navigationTimeout: 30000,
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
    },

    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
    },

    {
      name: 'webkit',
      use: {
        ...devices['Desktop Safari'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
    },

    // Mobile testing
    {
      name: 'Mobile Chrome',
      use: {
        ...devices['Pixel 5'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
    },

    {
      name: 'Mobile Safari',
      use: {
        ...devices['iPhone 12'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
    },

    // Accessibility testing project
    {
      name: 'accessibility',
      use: {
        ...devices['Desktop Chrome'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
      testMatch: '**/*.accessibility.spec.ts',
    },

    // Performance testing project
    {
      name: 'performance',
      use: {
        ...devices['Desktop Chrome'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
      testMatch: '**/*.performance.spec.ts',
    },

    // Visual regression testing
    {
      name: 'visual',
      use: {
        ...devices['Desktop Chrome'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
      testMatch: '**/*.visual.spec.ts',
    },
  ],

  // Global setup and teardown
  globalSetup: require.resolve('./tests/global-setup'),
  globalTeardown: require.resolve('./tests/global-teardown'),

  // Test metadata
  metadata: {
    'test-type': 'e2e',
    'application': 'agent-debate-system',
    'version': process.env.npm_package_version || '1.0.0',
  },

  // WebServer configuration for local development
  webServer: [
    {
      command: 'cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8443 --reload',
      port: 8443,
      timeout: 120000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'cd frontend && npm run dev',
      port: 3000,
      timeout: 120000,
      reuseExistingServer: !process.env.CI,
    },
  ],

  // Configure test groups
  testIgnore: [
    '**/node_modules/**',
    '**/.next/**',
    '**/build/**',
    '**/dist/**',
  ],

  testMatch: [
    '**/*.spec.ts',
    '**/*.test.ts',
  ],
})

export default config
