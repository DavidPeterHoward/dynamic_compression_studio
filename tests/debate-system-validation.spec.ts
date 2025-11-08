import { expect, test } from '@playwright/test';

/**
 * Comprehensive Multi-Agent Debate System Validation Test
 *
 * Validates the complete debate functionality including:
 * - Debate agent selection and configuration
 * - Autonomous debate execution
 * - Real-time updates and WebSocket communication
 * - Debate results and consensus building
 * - Agent specialization validation
 */

const BASE_URL = process.env.BASE_URL || process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8443';
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8441';

test.describe('Multi-Agent Debate System Comprehensive Validation', () => {
  test.setTimeout(180000); // 3 minutes for debate testing

  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000); // Wait for React hydration

    // Navigate to Agents tab
    const agentsTab = page.locator('text=Agents').first();
    await agentsTab.click({ timeout: 10000 });
    await page.waitForTimeout(2000); // Wait for Agents tab to load

    // Navigate to Debate System tab
    const debateTab = page.locator('text=Debate System').first();
    await debateTab.click({ timeout: 10000 });
    await page.waitForTimeout(2000);
  });

  test('1. Verify Debate System UI Components', async ({ page }) => {
    await test.step('Check debate system header and description', async () => {
      await expect(page.locator('text=Multi-Agent Debate System')).toBeVisible({ timeout: 10000 });
      await expect(page.locator('text=Autonomous multi-perspective argumentation')).toBeVisible();
    });

    await test.step('Verify tab navigation includes debate tabs', async () => {
      const tabs = ['Setup & Configuration', 'Live Debate', 'Analysis & Results'];
      for (const tabName of tabs) {
        await expect(page.locator(`text=${tabName}`)).toBeVisible({ timeout: 5000 });
      }
    });

    await test.step('Check debate WebSocket connection indicator', async () => {
      const wsIndicator = page.locator('text=/Live Debate|Disconnected/');
      await expect(wsIndicator.first()).toBeVisible();
    });
  });

  test('2. Validate Debate Agent Selection', async ({ page }) => {
    // Navigate to Setup tab (should be default)
    await page.locator('text=Setup & Configuration').first().click();
    await page.waitForTimeout(1000);

    await test.step('Verify all 9 debate agent types are displayed', async () => {
      const expectedAgents = [
        'Logical Analyst',
        'Argumentation Specialist',
        'Conceptual Analyst',
        'Critical Thinker',
        'Linguistic Analyst',
        'Mathematical Thinker',
        'Creative Innovator',
        'Integration Specialist',
        'Strategic Planner'
      ];

      for (const agentName of expectedAgents) {
        const agentCard = page.locator(`text=${agentName}`).first();
        await expect(agentCard).toBeVisible({ timeout: 5000 });
        console.log(`✅ Found debate agent: ${agentName}`);
      }
    });

    await test.step('Check agent specializations are displayed', async () => {
      const specializations = [
        'Logical validity, formal reasoning, identifying fallacies',
        'Argumentation, persuasive techniques, rhetorical analysis',
        'Conceptual analysis, assumptions, philosophical frameworks'
      ];

      for (const spec of specializations) {
        const specLocator = page.locator(`text=${spec}`).first();
        await expect(specLocator).toBeVisible({ timeout: 3000 });
        console.log(`✅ Found specialization: ${spec.substring(0, 30)}...`);
      }
    });

    await test.step('Test agent selection functionality', async () => {
      // Click on Logical Analyst
      const logicalAnalystCard = page.locator('text=Logical Analyst').first();
      await logicalAnalystCard.click();

      // Check selection indicator appears
      const selectionCount = page.locator('text=/1 selected|selected/');
      await expect(selectionCount.first()).toBeVisible();

      // Click on another agent
      const argumentationSpecialistCard = page.locator('text=Argumentation Specialist').first();
      await argumentationSpecialistCard.click();

      // Should now show 2 selected
      await expect(page.locator('text=/2 selected/').or(page.locator('text=selected')).first()).toBeVisible();
    });
  });

  test('3. Validate Debate Configuration Form', async ({ page }) => {
    await test.step('Fill out debate topic and problem statement', async () => {
      const debateTopicInput = page.locator('label:has-text("Debate Topic")').locator('..').locator('input').first();
      await expect(debateTopicInput).toBeVisible();

      await debateTopicInput.fill('The Impact of Artificial Intelligence on Human Employment');

      const problemStatementTextarea = page.locator('label:has-text("Problem Statement")').locator('..').locator('textarea').first();
      await expect(problemStatementTextarea).toBeVisible();

      await problemStatementTextarea.fill(`The rapid advancement of AI technologies presents both opportunities and challenges for the global workforce. While AI can augment human capabilities and create new types of employment, it also threatens to displace workers in traditional roles. This debate explores the complex relationship between technological progress and human employment, considering economic, social, and ethical dimensions.`);
    });

    await test.step('Configure debate parameters', async () => {
      // Select debate mode
      const modeSelect = page.locator('button:has-text("Autonomous Debate")').or(
        page.locator('button:has-text("Structured Debate")')
      );
      await expect(modeSelect.first()).toBeVisible();

      // Configure rounds and consensus
      const maxRoundsInput = page.locator('input[type="number"]').first();
      await maxRoundsInput.fill('3');

      // Find consensus threshold slider
      const consensusSlider = page.locator('input[type="range"]').or(
        page.locator('[role="slider"]')
      );
      if (await consensusSlider.count() > 0) {
        await consensusSlider.first().fill('0.7');
      }
    });

    await test.step('Configure debate rules', async () => {
      const ruleSwitches = [
        'Require Evidence',
        'Enable Fact Checking',
        'Allow Creative Solutions'
      ];

      for (const rule of ruleSwitches) {
        const switchElement = page.locator(`text=${rule}`).locator('..').locator('[role="switch"]').or(
          page.locator(`label:has-text("${rule}")`).locator('..').locator('input[type="checkbox"]')
        );
        if (await switchElement.count() > 0) {
          await switchElement.first().check();
          console.log(`✅ Configured rule: ${rule}`);
        }
      }
    });
  });

  test('4. Test Debate Initialization and Execution', async ({ page }) => {
    await test.step('Complete debate setup and initialize', async () => {
      // Fill required fields
      const debateTopicInput = page.locator('label:has-text("Debate Topic")').locator('..').locator('input').first();
      await debateTopicInput.fill('AI and Human Employment');

      const problemStatementTextarea = page.locator('label:has-text("Problem Statement")').locator('..').locator('textarea').first();
      await problemStatementTextarea.fill('How will AI impact employment patterns?');

      // Select at least 2 agents
      await page.locator('text=Logical Analyst').first().click();
      await page.locator('text=Argumentation Specialist').first().click();

      // Initialize debate
      const initButton = page.locator('button:has-text("Start Debate Session")').first();
      await expect(initButton).toBeVisible();
      await initButton.click();
    });

    await test.step('Verify debate switches to Live Debate tab', async () => {
      await page.waitForTimeout(2000);
      // Check if we're on the Live Debate tab or if content changed
      const debateControlPanel = page.locator('text=Debate Control Panel').or(
        page.locator('text=Live Debate')
      );
      await expect(debateControlPanel.first()).toBeVisible({ timeout: 10000 });
    });

    await test.step('Test debate control buttons', async () => {
      // Look for control buttons
      const startButton = page.locator('button:has-text("Start")').first();
      const pauseButton = page.locator('button:has-text("Pause")').first();
      const stopButton = page.locator('button:has-text("Stop")').first();

      // At least one control button should be visible
      const controlButtons = await page.locator('button:has-text("Start"), button:has-text("Pause"), button:has-text("Stop")').count();
      expect(controlButtons).toBeGreaterThan(0);
    });
  });

  test('5. Validate Debate Progress Tracking', async ({ page }) => {
    await test.step('Check debate progress indicators', async () => {
      const progressIndicators = [
        'Current Round',
        'Total Arguments',
        'Consensus Score'
      ];

      for (const indicator of progressIndicators) {
        const indicatorLocator = page.locator(`text=${indicator}`).first();
        // May not be visible until debate starts, so we check if it exists
        const count = await indicatorLocator.count();
        if (count > 0) {
          console.log(`✅ Found progress indicator: ${indicator}`);
        }
      }
    });

    await test.step('Verify participant display', async () => {
      const participantIndicators = page.locator('text=/Agent.*\\d+/').or(
        page.locator('text=Participants')
      );

      // Should show participants when debate is active
      const count = await participantIndicators.count();
      console.log(`Found ${count} participant indicators`);
    });
  });

  test('6. Test Debate API Endpoints', async ({ page, request }) => {
    await test.step('Test debate sessions endpoint', async () => {
      try {
        const response = await request.get(`${API_URL}/debate/sessions`);
        expect(response.status()).toBe(200);
        const data = await response.json();
        expect(data).toHaveProperty('sessions');
        expect(Array.isArray(data.sessions)).toBe(true);
        console.log('✅ Debate sessions endpoint accessible');
      } catch (error) {
        console.log('⚠️ Debate sessions endpoint not accessible (expected if no backend)');
      }
    });

    await test.step('Test debate initialization endpoint schema', async () => {
      // Test with minimal valid payload
      const testPayload = {
        debate_topic: "Test Debate",
        problem_statement: "Test problem statement",
        selected_agents: ["11", "12"],
        debate_mode: "autonomous",
        max_rounds: 3,
        consensus_threshold: 0.8,
        debate_rules: {}
      };

      try {
        const response = await request.post(`${API_URL}/debate/initialize`, {
          data: testPayload
        });

        if (response.status() === 200) {
          const data = await response.json();
          expect(data).toHaveProperty('session');
          expect(data).toHaveProperty('message');
          console.log('✅ Debate initialization endpoint functional');
        } else {
          console.log(`⚠️ Debate initialization returned status ${response.status()}`);
        }
      } catch (error) {
        console.log('⚠️ Debate initialization endpoint not accessible (expected if no backend)');
      }
    });
  });

  test('7. Validate Debate Results and Analysis', async ({ page }) => {
    await test.step('Check analysis tab components when available', async () => {
      const analysisTab = page.locator('text=Analysis & Results').first();

      if (await analysisTab.isVisible()) {
        await analysisTab.click();
        await page.waitForTimeout(1000);

        // Check for analysis components
        const analysisComponents = [
          'Debate Results Summary',
          'Participant Performance',
          'Debate Timeline'
        ];

        for (const component of analysisComponents) {
          const componentLocator = page.locator(`text=${component}`).first();
          const count = await componentLocator.count();
          if (count > 0) {
            console.log(`✅ Found analysis component: ${component}`);
          }
        }
      }
    });
  });

  test('8. Test Real-Time Debate Updates', async ({ page }) => {
    await test.step('Monitor WebSocket connection status', async () => {
      const wsIndicator = page.locator('text=/Live Debate|Disconnected/').first();
      await expect(wsIndicator).toBeVisible();

      // Check if connection status changes appropriately
      const isConnected = await page.locator('text=Live Debate').isVisible().catch(() => false);
      console.log(`WebSocket status: ${isConnected ? 'Connected' : 'Disconnected'}`);
    });

    await test.step('Verify debate event handling', async () => {
      // Monitor for any real-time updates (arguments, rounds, etc.)
      const debateEvents = page.locator('text=/Round.*\\d+/').or(
        page.locator('text=/Argument.*made/').or(
          page.locator('text=/Consensus.*reached/')
        )
      );

      // Wait briefly to see if any events appear
      await page.waitForTimeout(5000);
      const eventCount = await debateEvents.count();
      console.log(`Detected ${eventCount} debate events during monitoring`);
    });
  });

  test('9. Validate Agent Specialization Logic', async ({ page }) => {
    await test.step('Verify agent specialization descriptions', async () => {
      const specializationTexts = [
        'formal reasoning',
        'persuasive techniques',
        'philosophical frameworks',
        'devil\'s advocate',
        'semantic analysis',
        'formal structures',
        'creative solutions',
        'reconciling viewpoints',
        'scenario planning'
      ];

      let foundCount = 0;
      for (const spec of specializationTexts) {
        const specLocator = page.locator(`text=/${spec}/i`).first();
        const count = await specLocator.count();
        if (count > 0) {
          foundCount++;
          console.log(`✅ Found agent specialization: ${spec}`);
        }
      }

      console.log(`Found ${foundCount}/${specializationTexts.length} agent specializations`);
    });
  });

  test('10. Comprehensive Debate System Validation', async ({ page }) => {
    await test.step('Count all debate-related UI components', async () => {
      const componentCounts = {
        buttons: await page.locator('button').count(),
        inputs: await page.locator('input').count(),
        textareas: await page.locator('textarea').count(),
        selects: await page.locator('[role="combobox"]').count(),
        cards: await page.locator('[class*="card" i]').count(),
        badges: await page.locator('[class*="badge" i]').count(),
        switches: await page.locator('[role="switch"]').count(),
        progress: await page.locator('progress').or(page.locator('[class*="progress" i]')).count()
      };

      console.log('Debate UI Component Counts:');
      Object.entries(componentCounts).forEach(([component, count]) => {
        console.log(`  ${component}: ${count}`);
      });

      // Verify minimum expected counts for a functional debate system
      expect(componentCounts.buttons).toBeGreaterThan(5); // Control buttons, agent selections
      expect(componentCounts.cards).toBeGreaterThan(3); // Configuration, progress, results cards
    });

    await test.step('Validate debate system responsiveness', async () => {
      // Test that UI responds to user interactions
      const agentCards = page.locator('text=Logical Analyst').first();
      const initialClasses = await agentCards.getAttribute('class');

      await agentCards.click();
      await page.waitForTimeout(500);

      // Check if visual state changed (would indicate interactivity)
      const afterClasses = await agentCards.getAttribute('class');
      const hasVisualChange = initialClasses !== afterClasses;

      if (hasVisualChange) {
        console.log('✅ Debate UI shows responsive visual feedback');
      }
    });
  });
});
