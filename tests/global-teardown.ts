/**
 * Global Teardown for Playwright Tests
 *
 * Cleans up the test environment after all tests complete.
 * Stops services, cleans up test data, and generates reports.
 */

import { execSync } from 'child_process'
import * as fs from 'fs'
import * as path from 'path'

async function globalTeardown() {
  console.log('🧹 Starting global test teardown...')

  // Stop frontend service if we started it
  if (!process.env.CI && process.env.START_FRONTEND !== 'false') {
    try {
      console.log('🛑 Stopping frontend service...')

      // Find and kill Next.js processes
      try {
        execSync('pkill -f "next dev" || true', { stdio: 'pipe' })
        console.log('✅ Frontend service stopped')
      } catch {
        console.log('ℹ️  Frontend service was not running')
      }
    } catch (error) {
      console.warn('⚠️  Error stopping frontend service:', error.message)
    }
  }

  // Stop backend service if we started it
  if (!process.env.CI && process.env.START_BACKEND !== 'false') {
    try {
      console.log('🛑 Stopping backend service...')

      // Find and kill uvicorn processes
      try {
        execSync('pkill -f "uvicorn.*app.main:app" || true', { stdio: 'pipe' })
        console.log('✅ Backend service stopped')
      } catch {
        console.log('ℹ️  Backend service was not running')
      }
    } catch (error) {
      console.warn('⚠️  Error stopping backend service:', error.message)
    }
  }

  // Stop Ollama service if we started it
  if (!process.env.CI && process.env.START_OLLAMA !== 'false') {
    try {
      console.log('🛑 Stopping Ollama service...')

      // Find and kill Ollama processes
      try {
        execSync('pkill -f "ollama serve" || true', { stdio: 'pipe' })
        console.log('✅ Ollama service stopped')
      } catch {
        console.log('ℹ️  Ollama service was not running')
      }
    } catch (error) {
      console.warn('⚠️  Error stopping Ollama service:', error.message)
    }
  }

  // Clean up test database
  if (process.env.CLEANUP_TEST_DB === 'true') {
    try {
      console.log('🗑️  Cleaning up test database...')

      // Run database cleanup
      execSync('cd backend && python -c "from app.database import cleanup_test_data; cleanup_test_data()"', {
        stdio: 'pipe'
      })

      console.log('✅ Test database cleanup completed')
    } catch (error) {
      console.warn('⚠️  Error cleaning up test database:', error.message)
    }
  }

  // Generate test summary report
  try {
    console.log('📊 Generating test summary report...')

    const resultsDir = path.join(process.cwd(), 'test-results')
    const summaryPath = path.join(resultsDir, 'test-summary.json')

    // Read test results if available
    let summary = {
      timestamp: new Date().toISOString(),
      environment: {
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch,
        ci: !!process.env.CI,
      },
      services: {
        backend: false,
        frontend: false,
        ollama: false,
      },
      cleanup: {
        database: false,
        files: false,
      },
    }

    // Check which services were running
    try {
      execSync('curl -s http://localhost:8443/docs > /dev/null', { stdio: 'pipe' })
      summary.services.backend = true
    } catch {}

    try {
      execSync('curl -s http://localhost:3000 > /dev/null', { stdio: 'pipe' })
      summary.services.frontend = true
    } catch {}

    try {
      execSync('curl -s http://localhost:11434/api/tags > /dev/null', { stdio: 'pipe' })
      summary.services.ollama = true
    } catch {}

    // Write summary
    fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2))
    console.log('✅ Test summary report generated')
  } catch (error) {
    console.warn('⚠️  Error generating test summary:', error.message)
  }

  // Clean up temporary files
  try {
    console.log('🧽 Cleaning up temporary files...')

    const tempDirs = [
      path.join(process.cwd(), 'test-results', 'temp'),
      path.join(process.cwd(), 'test-snapshots', 'temp'),
      path.join(process.cwd(), '.next', 'test-cache'),
    ]

    for (const dir of tempDirs) {
      if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true })
      }
    }

    console.log('✅ Temporary files cleaned up')
  } catch (error) {
    console.warn('⚠️  Error cleaning up temporary files:', error.message)
  }

  // Archive test artifacts if in CI
  if (process.env.CI && process.env.ARCHIVE_TEST_ARTIFACTS === 'true') {
    try {
      console.log('📦 Archiving test artifacts...')

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      const archiveName = `test-artifacts-${timestamp}.tar.gz`
      const archivePath = path.join(process.cwd(), archiveName)

      // Create archive of test results
      execSync(`tar -czf ${archivePath} test-results/ test-snapshots/ playwright-report/`, {
        stdio: 'pipe'
      })

      console.log(`✅ Test artifacts archived to ${archiveName}`)
    } catch (error) {
      console.warn('⚠️  Error archiving test artifacts:', error.message)
    }
  }

  console.log('✅ Global test teardown completed successfully!')
}

export default globalTeardown
