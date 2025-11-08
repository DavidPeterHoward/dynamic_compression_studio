/**
 * Global Setup for Playwright Tests
 *
 * Sets up the test environment before all tests run.
 * Configures databases, starts services, and prepares test data.
 */

import { chromium, FullConfig } from '@playwright/test'
import { execSync, spawn } from 'child_process'
import * as fs from 'fs'
import * as path from 'path'

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global test setup...')

  // Create test results directory
  const resultsDir = path.join(process.cwd(), 'test-results')
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true })
  }

  // Create test snapshots directory
  const snapshotsDir = path.join(process.cwd(), 'test-snapshots')
  if (!fs.existsSync(snapshotsDir)) {
    fs.mkdirSync(snapshotsDir, { recursive: true })
  }

  // Start Ollama service if not running (for local testing)
  if (!process.env.CI && process.env.START_OLLAMA !== 'false') {
    try {
      console.log('🔍 Checking Ollama service...')
      execSync('ollama --version', { stdio: 'pipe' })

      // Check if Ollama is already running
      try {
        execSync('curl -s http://localhost:11434/api/tags > /dev/null', { stdio: 'pipe' })
        console.log('✅ Ollama service is already running')
      } catch {
        console.log('🚀 Starting Ollama service...')
        const ollamaProcess = spawn('ollama', ['serve'], {
          detached: true,
          stdio: 'ignore',
        })
        ollamaProcess.unref()

        // Wait for Ollama to start
        let retries = 0
        while (retries < 30) {
          try {
            execSync('curl -s http://localhost:11434/api/tags > /dev/null', { stdio: 'pipe' })
            console.log('✅ Ollama service started successfully')
            break
          } catch {
            await new Promise(resolve => setTimeout(resolve, 1000))
            retries++
          }
        }

        if (retries >= 30) {
          console.warn('⚠️  Ollama service failed to start within 30 seconds')
        }
      }

      // Ensure required models are available
      const requiredModels = ['llama2:13b', 'mistral:7b']
      for (const model of requiredModels) {
        try {
          execSync(`ollama show ${model}`, { stdio: 'pipe' })
          console.log(`✅ Model ${model} is available`)
        } catch {
          console.log(`📥 Pulling model ${model}...`)
          try {
            execSync(`ollama pull ${model}`, { stdio: 'inherit', timeout: 300000 })
            console.log(`✅ Successfully pulled model ${model}`)
          } catch (error) {
            console.warn(`⚠️  Failed to pull model ${model}:`, error.message)
          }
        }
      }

    } catch (error) {
      console.warn('⚠️  Ollama is not available in this environment')
      console.warn('Tests requiring Ollama will be skipped')
    }
  }

  // Start backend service if not running
  if (!process.env.CI && process.env.START_BACKEND !== 'false') {
    try {
      console.log('🔍 Checking backend service...')

      // Check if backend is already running
      try {
        execSync('curl -s http://localhost:8443/docs > /dev/null', { stdio: 'pipe' })
        console.log('✅ Backend service is already running')
      } catch {
        console.log('🚀 Starting backend service...')

        const backendProcess = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8443', '--reload'], {
          cwd: path.join(process.cwd(), 'backend'),
          detached: true,
          stdio: 'ignore',
        })
        backendProcess.unref()

        // Wait for backend to start
        let retries = 0
        while (retries < 30) {
          try {
            execSync('curl -s http://localhost:8443/docs > /dev/null', { stdio: 'pipe' })
            console.log('✅ Backend service started successfully')
            break
          } catch {
            await new Promise(resolve => setTimeout(resolve, 1000))
            retries++
          }
        }

        if (retries >= 30) {
          throw new Error('Backend service failed to start within 30 seconds')
        }
      }
    } catch (error) {
      console.error('❌ Failed to start backend service:', error.message)
      throw error
    }
  }

  // Start frontend service if not running
  if (!process.env.CI && process.env.START_FRONTEND !== 'false') {
    try {
      console.log('🔍 Checking frontend service...')

      // Check if frontend is already running
      try {
        execSync('curl -s http://localhost:3000 > /dev/null', { stdio: 'pipe' })
        console.log('✅ Frontend service is already running')
      } catch {
        console.log('🚀 Starting frontend service...')

        const frontendProcess = spawn('npm', ['run', 'dev'], {
          cwd: path.join(process.cwd(), 'frontend'),
          detached: true,
          stdio: 'ignore',
          env: {
            ...process.env,
            NODE_ENV: 'test',
            NEXT_PUBLIC_API_URL: 'http://localhost:8443',
          },
        })
        frontendProcess.unref()

        // Wait for frontend to start
        let retries = 0
        while (retries < 30) {
          try {
            execSync('curl -s http://localhost:3000 > /dev/null', { stdio: 'pipe' })
            console.log('✅ Frontend service started successfully')
            break
          } catch {
            await new Promise(resolve => setTimeout(resolve, 1000))
            retries++
          }
        }

        if (retries >= 30) {
          throw new Error('Frontend service failed to start within 30 seconds')
        }
      }
    } catch (error) {
      console.error('❌ Failed to start frontend service:', error.message)
      throw error
    }
  }

  // Setup test database if needed
  if (process.env.SETUP_TEST_DB === 'true') {
    try {
      console.log('🗄️  Setting up test database...')

      // Run database migrations or setup
      execSync('cd backend && python -c "from app.database import create_tables; create_tables()"', {
        stdio: 'inherit'
      })

      console.log('✅ Test database setup completed')
    } catch (error) {
      console.error('❌ Failed to setup test database:', error.message)
      throw error
    }
  }

  // Pre-warm the application
  try {
    console.log('🔥 Pre-warming application...')

    const browser = await chromium.launch()
    const page = await browser.newPage()

    // Navigate to the application and wait for it to load
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' })
    await page.waitForSelector('[data-testid="agents-tab"]', { timeout: 30000 })

    await browser.close()
    console.log('✅ Application pre-warmed successfully')
  } catch (error) {
    console.warn('⚠️  Application pre-warming failed:', error.message)
    // Don't fail the setup for pre-warming issues
  }

  console.log('✅ Global test setup completed successfully!')
}

export default globalSetup
