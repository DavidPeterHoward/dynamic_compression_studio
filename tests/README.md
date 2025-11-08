# Agent Debate Construction E2E Tests

Comprehensive end-to-end testing suite for the Agent Debate Construction system using Playwright.

## 📋 Overview

This test suite validates the complete workflow of constructing and executing debates between AI agents powered by Ollama models. The tests cover:

- Agent creation and management
- Ollama integration and model management
- Debate configuration and initialization
- Real-time debate execution
- Performance and accessibility validation

## 🏗️ Architecture

### Test Structure

```
tests/
├── agent-debate-construction.spec.ts    # Main E2E test suite
├── helpers/
│   └── agent-debate-test-helper.ts      # Test utilities and helpers
├── global-setup.ts                      # Test environment setup
├── global-teardown.ts                   # Test environment cleanup
└── README.md                           # This file
```

### Test Categories

1. **Agent Management Tests**
   - Agent creation workflows
   - Agent configuration and validation
   - Agent health monitoring
   - Agent deletion and cleanup

2. **Ollama Integration Tests**
   - Model availability and loading
   - Chat functionality verification
   - Streaming response handling
   - Error handling and fallbacks

3. **Debate Construction Tests**
   - Debate topic and configuration setup
   - Agent selection and assignment
   - Debate rules configuration
   - Debate initialization validation

4. **Debate Execution Tests**
   - Real-time debate progression
   - Agent interaction validation
   - Consensus tracking and metrics
   - Debate completion and results

5. **Performance Tests**
   - Load time validation
   - Concurrent operation handling
   - Memory usage monitoring
   - Network latency simulation

6. **Accessibility Tests**
   - Keyboard navigation
   - Screen reader support
   - ARIA compliance
   - Focus management

## 🚀 Running Tests

### Prerequisites

1. **Node.js** (v16+)
2. **Ollama** installed and running
3. **Required Ollama models**:
   - `llama2:13b`
   - `mistral:7b`
   - `codellama:13b`

### Installation

```bash
# Install dependencies
npm install

# Install Playwright browsers
npx playwright install
```

### Environment Setup

Create a `.env.test` file:

```bash
# Test environment configuration
TEST_BASE_URL=http://localhost:3000
TEST_API_URL=http://localhost:8443
OLLAMA_BASE_URL=http://localhost:11434

# Service control (set to 'false' to disable auto-start)
START_OLLAMA=true
START_BACKEND=true
START_FRONTEND=true

# Test configuration
SETUP_TEST_DB=true
CLEANUP_TEST_DB=true
ARCHIVE_TEST_ARTIFACTS=false
```

### Running Tests

```bash
# Run all tests
npm run test:e2e

# Run specific test file
npx playwright test agent-debate-construction.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium

# Run tests with UI mode
npx playwright test --ui

# Run tests in debug mode
npx playwright test --debug

# Run performance tests only
npx playwright test --project=performance

# Run accessibility tests only
npx playwright test --project=accessibility
```

### Test Configuration Options

```bash
# Run tests in parallel (default: sequential for state-dependent tests)
npx playwright test --workers=4

# Set timeout for individual tests
npx playwright test --timeout=120000

# Generate HTML report
npx playwright test --reporter=html

# Run tests in headed mode (visible browser)
npx playwright test --headed

# Record video for all tests
npx playwright test --video=retain-on-failure
```

## 🧪 Test Scenarios

### Agent Creation Workflow

```typescript
test('should create a logical analyst agent successfully', async ({ page }) => {
  const testHelper = new AgentDebateTestHelper(page)

  await testHelper.navigateToAgentsTab()

  const agentId = await testHelper.createAgent({
    type: 'logical_analyst',
    name: 'Test Logical Analyst',
    capabilities: ['ANALYSIS', 'LOGIC'],
    parameters: {
      reasoning_depth: 3,
      evidence_threshold: 0.8
    }
  })

  // Verify agent creation
  await testHelper.verifyAgentExists(agentId)
  await testHelper.verifyAgentHealth(agentId)
})
```

### Debate Construction and Execution

```typescript
test('should execute debate rounds with agent interactions', async ({ page }) => {
  const testHelper = new AgentDebateTestHelper(page)

  // Setup debate
  await testHelper.setupDebateConfiguration({
    topic: 'AI Impact on Employment',
    mode: 'structured',
    maxRounds: 3,
    rules: {
      require_evidence: true,
      enable_fact_checking: true,
      allow_creativity: true
    }
  })

  // Select agents
  await testHelper.selectDebateAgents(['agent1', 'agent2'])

  // Initialize and execute debate
  await testHelper.initializeDebate()
  await page.click('[data-testid="start-debate-btn"]')

  // Verify debate execution
  await page.waitForSelector('[data-testid="round-1-complete"]')
  const metrics = await testHelper.captureDebateMetrics()

  expect(metrics.argumentsCount).toBeGreaterThan(0)
  expect(metrics.consensusScore).toBeGreaterThan('0.00')
})
```

## 🔧 Test Helpers

### AgentDebateTestHelper

Comprehensive helper class providing:

- **Navigation**: `navigateToAgentsTab()`, `navigateToDebateSystem()`
- **Agent Management**: `createAgent()`, `deleteAgent()`, `verifyAgentHealth()`
- **Debate Setup**: `setupDebateConfiguration()`, `selectDebateAgents()`, `initializeDebate()`
- **Validation**: `captureDebateMetrics()`, `verifyDebateRulesApplied()`
- **Mocking**: `mockApiResponse()`, `mockOllamaFailure()`
- **Performance**: `measurePageLoadTime()`, `getMemoryUsage()`

### Utility Functions

```typescript
import { createTestAgent, createTestDebate, waitForCondition } from './helpers/agent-debate-test-helper'

// Create test fixtures
const agent = createTestAgent({ name: 'Test Agent', type: 'creative_innovator' })
const debate = createTestDebate({ topic: 'Test Topic', maxRounds: 2 })

// Wait for conditions
await waitForCondition(async () => {
  const metrics = await testHelper.captureDebateMetrics()
  return metrics.roundNumber === '2'
})
```

## 📊 Test Reporting

### HTML Report

```bash
npx playwright show-report
```

### JSON Results

```bash
# View results
cat test-results/results.json

# JUnit for CI/CD
cat test-results/junit.xml
```

### Performance Metrics

Tests automatically capture:
- Page load times
- Memory usage
- Network request times
- Debate execution metrics

## 🐛 Debugging Tests

### Debug Mode

```bash
# Run test in debug mode
npx playwright test --debug agent-debate-construction.spec.ts

# Use Playwright Inspector
npx playwright test --headed --timeout=0
```

### Screenshots and Videos

Failed tests automatically capture:
- Screenshots of failure points
- Videos of test execution
- Network logs and console output

### Common Debugging Techniques

```typescript
// Add debug logging
await page.pause() // Interactive debugging

// Inspect page state
const content = await page.textContent('[data-testid="debate-status"]')
console.log('Debate status:', content)

// Network interception
await page.route('**/api/**', route => {
  console.log('API call:', route.request().url())
  route.continue()
})
```

## 🚨 Error Handling

### Test Timeouts

```typescript
// Increase timeout for slow operations
test.setTimeout(120000)

// Wait for specific conditions
await page.waitForSelector('[data-testid="debate-complete"]', {
  timeout: 60000,
  state: 'visible'
})
```

### Flaky Tests

```typescript
// Retry failed tests
test.describe.configure({ retries: 3 })

// Conditional logic for unstable elements
const element = page.locator('[data-testid="dynamic-element"]')
if (await element.isVisible({ timeout: 1000 })) {
  await element.click()
}
```

## 🔒 Security Testing

### API Security

```typescript
test('should handle authentication failures', async ({ page }) => {
  // Mock unauthorized response
  await page.route('**/api/**', route => {
    route.fulfill({
      status: 401,
      body: JSON.stringify({ error: 'Unauthorized' })
    })
  })

  // Verify error handling
  await page.waitForSelector('[data-testid="auth-error"]')
})
```

### Input Validation

```typescript
test('should validate debate topic input', async ({ page }) => {
  // Test XSS prevention
  await page.fill('[data-testid="debate-topic-input"]', '<script>alert("xss")</script>')
  await page.click('[data-testid="initialize-debate-btn"]')

  // Verify input sanitization
  const topic = await page.inputValue('[data-testid="debate-topic-input"]')
  expect(topic).not.toContain('<script>')
})
```

## 📈 Performance Benchmarks

### Target Metrics

- **Page Load**: < 3 seconds
- **Agent Creation**: < 5 seconds
- **Debate Initialization**: < 10 seconds
- **Debate Round**: < 25 seconds
- **Memory Usage**: < 100MB

### Performance Testing

```typescript
test('should maintain smooth debate execution performance', async ({ page }) => {
  const startTime = Date.now()
  await testHelper.initializeDebate()

  // Measure round completion time
  await page.waitForSelector('[data-testid="round-1-complete"]', { timeout: 30000 })
  const roundTime = Date.now() - startTime

  expect(roundTime).toBeLessThan(25000) // 25 second target
})
```

## 🎯 Best Practices

### Test Organization

1. **Descriptive Test Names**: Clear, actionable test descriptions
2. **Independent Tests**: Each test should be self-contained
3. **Data Isolation**: Use unique test data to avoid conflicts
4. **Cleanup**: Always clean up test data and state

### Test Data Management

```typescript
// Use factories for test data
const testAgent = createTestAgent({
  name: `Test Agent ${Date.now()}`,
  type: 'logical_analyst'
})

// Cleanup in teardown
test.afterEach(async ({ page }) => {
  const testHelper = new AgentDebateTestHelper(page)
  await testHelper.cleanupTestData()
})
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run E2E Tests
  run: |
    npm run test:e2e
  env:
    CI: true
    TEST_BASE_URL: ${{ secrets.TEST_BASE_URL }}
    TEST_API_URL: ${{ secrets.TEST_API_URL }}
```

## 🤝 Contributing

### Adding New Tests

1. Create test file in `tests/` directory
2. Use descriptive naming: `*.spec.ts` or `*.test.ts`
3. Follow existing patterns and helpers
4. Add appropriate test categories and tags

### Test Helper Extensions

```typescript
// Extend AgentDebateTestHelper for new functionality
export class ExtendedTestHelper extends AgentDebateTestHelper {
  async customWorkflow() {
    // Custom test logic
  }
}
```

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Testing Best Practices](https://playwright.dev/docs/best-practices)
- [E2E Testing Guide](https://web.dev/e2e-testing/)
- [Accessibility Testing](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## 🆘 Troubleshooting

### Common Issues

**Tests timing out**
```bash
# Increase timeout
npx playwright test --timeout=120000
```

**Element not found**
```bash
# Use more specific selectors
await page.waitForSelector('[data-testid="specific-element"]', { timeout: 10000 })
```

**Flaky network requests**
```bash
# Add retry logic
await page.reload({ waitUntil: 'networkidle' })
```

### Getting Help

1. Check test logs in `test-results/`
2. Review screenshots and videos
3. Use `--debug` mode for step-by-step execution
4. Check network tab for failed API calls

---

**Test Coverage**: Agent creation, Ollama integration, debate construction, real-time execution, performance, accessibility
**Browsers**: Chrome, Firefox, Safari, Mobile Chrome, Mobile Safari
**Environments**: Local development, CI/CD, Staging, Production
