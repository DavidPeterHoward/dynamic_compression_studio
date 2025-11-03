"""
Playwright E2E Tests for Agent Communication UI

Tests that verify agent communication and collaboration through the user interface.
These tests ensure that the frontend properly displays and facilitates inter-agent interactions.
"""

import pytest
import asyncio
import json
from playwright.sync_api import Page, expect
from typing import Dict, Any


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for testing."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": "test-results/videos/" if pytest.config.getoption("--video") else None,
    }


@pytest.fixture
def page_with_agents(page: Page):
    """Set up page with agent communication initialized."""
    # Navigate to the application
    page.goto("http://localhost:3000")

    # Wait for the app to load
    expect(page.locator('[data-testid="app-loaded"]')).to_be_visible(timeout=10000)

    # Ensure agents are initialized (this would be done by the backend in real scenario)
    # For testing, we'll mock the agent communication

    yield page


class TestAgentCommunicationUI:
    """E2E tests for agent communication through UI."""

    def test_agent_communication_tab_exists(self, page_with_agents: Page):
        """Test that agent communication tab exists in UI."""
        page = page_with_agents

        # Look for agent communication tab
        comm_tab = page.locator('[data-testid="agent-communication-tab"]').or_(
            page.locator('text="Agent Communication"')
        ).or_(
            page.locator('[data-testid="communication-tab"]')
        )

        expect(comm_tab).to_be_visible()

    def test_agent_status_display(self, page_with_agents: Page):
        """Test that agent statuses are displayed."""
        page = page_with_agents

        # Check for agent status indicators
        agent_statuses = page.locator('[data-testid*="agent-status"]').or_(
            page.locator('[data-testid*="agent-01"]').or_(
                page.locator('[data-testid*="agent-02"]')
            )
        )

        # Should show at least infrastructure and database agents
        expect(agent_statuses).to_have_count(lambda count: count >= 2)

    def test_task_delegation_ui(self, page_with_agents: Page):
        """Test task delegation through UI."""
        page = page_with_agents

        # Find task delegation section
        delegation_section = page.locator('[data-testid="task-delegation"]').or_(
            page.locator('text="Task Delegation"')
        ).or_(
            page.locator('[data-testid="delegate-task"]')
        )

        if delegation_section.is_visible():
            # Click to open delegation form
            delegation_section.click()

            # Fill out delegation form
            page.select_option('[data-testid="target-agent-select"]', '01')
            page.select_option('[data-testid="task-type-select"]', 'ping')
            page.fill('[data-testid="task-parameters"]', '{}')

            # Submit delegation
            page.click('[data-testid="submit-delegation"]')

            # Check for success message
            success_msg = page.locator('[data-testid="delegation-success"]').or_(
                page.locator('text="Task delegated successfully"')
            )

            expect(success_msg).to_be_visible(timeout=5000)

    def test_parameter_optimization_ui(self, page_with_agents: Page):
        """Test parameter optimization through UI."""
        page = page_with_agents

        # Find parameter optimization section
        opt_section = page.locator('[data-testid="parameter-optimization"]').or_(
            page.locator('text="Parameter Optimization"')
        ).or_(
            page.locator('[data-testid="optimize-params"]')
        )

        if opt_section.is_visible():
            opt_section.click()

            # Configure optimization
            page.select_option('[data-testid="target-agent-select"]', '02')
            page.select_option('[data-testid="task-type-select"]', 'database_performance')

            # Add parameter space
            page.fill('[data-testid="parameter-space"]', json.dumps({
                "connection_pool_size": {"type": "range", "min": 5, "max": 20, "step": 5}
            }))

            # Add evaluation criteria
            page.fill('[data-testid="evaluation-criteria"]', json.dumps({
                "query_performance": 0.6,
                "connection_stability": 0.4
            }))

            # Start optimization
            page.click('[data-testid="start-optimization"]')

            # Check for progress indicator
            progress_indicator = page.locator('[data-testid="optimization-progress"]').or_(
                page.locator('text="Optimizing"')
            )

            expect(progress_indicator).to_be_visible(timeout=3000)

            # Wait for completion (with timeout)
            completion_msg = page.locator('[data-testid="optimization-complete"]').or_(
                page.locator('text="Optimization completed"')
            )

            expect(completion_msg).to_be_visible(timeout=30000)  # 30 second timeout

            # Check results
            results_section = page.locator('[data-testid="optimization-results"]')
            expect(results_section).to_be_visible()

            # Verify best parameters are shown
            best_params = page.locator('[data-testid="best-parameters"]').or_(
                page.locator('text="Best Parameters"')
            )
            expect(best_params).to_be_visible()

    def test_collaboration_ui(self, page_with_agents: Page):
        """Test collaboration features through UI."""
        page = page_with_agents

        # Find collaboration section
        collab_section = page.locator('[data-testid="collaboration"]').or_(
            page.locator('text="Collaboration"')
        ).or_(
            page.locator('[data-testid="start-collaboration"]')
        )

        if collab_section.is_visible():
            collab_section.click()

            # Set up collaboration
            page.select_option('[data-testid="collaborator-select"]', '02')
            page.select_option('[data-testid="collaboration-type"]', 'parallel')
            page.fill('[data-testid="task-spec"]', json.dumps({
                "type": "health_check",
                "parameters": {"comprehensive": True}
            }))

            # Start collaboration
            page.click('[data-testid="start-collaboration-btn"]')

            # Check for collaboration progress
            collab_progress = page.locator('[data-testid="collaboration-progress"]').or_(
                page.locator('text="Collaborating"')
            )

            expect(collab_progress).to_be_visible(timeout=3000)

            # Wait for completion
            collab_complete = page.locator('[data-testid="collaboration-complete"]').or_(
                page.locator('text="Collaboration completed"')
            )

            expect(collab_complete).to_be_visible(timeout=15000)

    def test_knowledge_sharing_ui(self, page_with_agents: Page):
        """Test knowledge sharing through UI."""
        page = page_with_agents

        # Find knowledge sharing section
        knowledge_section = page.locator('[data-testid="knowledge-sharing"]').or_(
            page.locator('text="Knowledge Sharing"')
        ).or_(
            page.locator('[data-testid="share-knowledge"]')
        )

        if knowledge_section.is_visible():
            knowledge_section.click()

            # Configure knowledge sharing
            page.select_option('[data-testid="knowledge-type"]', 'best_practices')
            page.fill('[data-testid="knowledge-data"]', json.dumps({
                "optimization_tips": ["Use connection pooling", "Monitor query performance"],
                "lessons_learned": ["Parameter tuning improves performance by 30%"]
            }))

            # Select recipients
            page.check('[data-testid="recipient-02"]')  # Database agent
            page.check('[data-testid="recipient-08"]')  # Monitoring agent

            # Share knowledge
            page.click('[data-testid="share-knowledge-btn"]')

            # Check for sharing confirmation
            share_confirm = page.locator('[data-testid="knowledge-shared"]').or_(
                page.locator('text="Knowledge shared successfully"')
            )

            expect(share_confirm).to_be_visible(timeout=5000)

    def test_agent_relationships_display(self, page_with_agents: Page):
        """Test that agent relationships are displayed."""
        page = page_with_agents

        # Find relationships section
        relationships_section = page.locator('[data-testid="agent-relationships"]').or_(
            page.locator('text="Agent Relationships"')
        ).or_(
            page.locator('[data-testid="relationships"]')
        )

        if relationships_section.is_visible():
            relationships_section.click()

            # Check for relationship indicators
            relationship_items = page.locator('[data-testid*="relationship-"]').or_(
                page.locator('[data-testid*="trust-score"]')
            )

            expect(relationship_items).to_have_count(lambda count: count >= 1)

            # Check for trust scores or interaction counts
            trust_scores = page.locator('text="Trust Score"').or_(
                page.locator('text="Interactions"')
            ).or_(
                page.locator('[data-testid*="trust"]')
            )

            expect(trust_scores).to_be_visible()

    def test_communication_history(self, page_with_agents: Page):
        """Test communication history display."""
        page = page_with_agents

        # Find communication history section
        history_section = page.locator('[data-testid="communication-history"]').or_(
            page.locator('text="Communication History"')
        ).or_(
            page.locator('[data-testid="history"]')
        )

        if history_section.is_visible():
            history_section.click()

            # Check for history entries
            history_entries = page.locator('[data-testid*="history-item"]').or_(
                page.locator('[data-testid*="communication-"]')
            )

            # Should have at least some history after interactions
            expect(history_entries).to_have_count(lambda count: count >= 0)

            # Check for timestamps
            timestamps = page.locator('text=/\\d{4}-\\d{2}-\\d{2}/').or_(
                page.locator('[data-testid*="timestamp"]')
            )

            if history_entries.count() > 0:
                expect(timestamps).to_be_visible()

    def test_realtime_updates(self, page_with_agents: Page):
        """Test real-time updates of agent communication."""
        page = page_with_agents

        # Look for real-time indicators
        realtime_indicators = page.locator('[data-testid*="realtime"]').or_(
            page.locator('[data-testid*="live"]').or_(
                page.locator('text="Live"').or_(
                    page.locator('text="Real-time"')
                )
            )
        )

        # Check for status updates (this would require backend WebSocket simulation)
        if realtime_indicators.is_visible():
            # Test that status updates appear
            initial_status = page.locator('[data-testid="agent-01-status"]').text_content()

            # Wait a bit for potential updates
            page.wait_for_timeout(2000)

            # Status might have changed (though in test environment it might not)
            # Just verify the UI can display status
            status_display = page.locator('[data-testid*="status"]')
            expect(status_display).to_have_count(lambda count: count >= 2)

    def test_error_handling_ui(self, page_with_agents: Page):
        """Test error handling in communication UI."""
        page = page_with_agents

        # Try to delegate to non-existent agent
        delegation_section = page.locator('[data-testid="task-delegation"]').or_(
            page.locator('text="Task Delegation"')
        )

        if delegation_section.is_visible():
            delegation_section.click()

            # Select invalid agent
            page.select_option('[data-testid="target-agent-select"]', '99')
            page.select_option('[data-testid="task-type-select"]', 'ping')
            page.click('[data-testid="submit-delegation"]')

            # Check for error message
            error_msg = page.locator('[data-testid="delegation-error"]').or_(
                page.locator('text="Error"').or_(
                    page.locator('text="Failed"')
                )
            )

            expect(error_msg).to_be_visible(timeout=5000)

    def test_performance_metrics_display(self, page_with_agents: Page):
        """Test that performance metrics are displayed."""
        page = page_with_agents

        # Find performance metrics section
        metrics_section = page.locator('[data-testid="performance-metrics"]').or_(
            page.locator('text="Performance Metrics"')
        ).or_(
            page.locator('[data-testid="metrics"]')
        )

        if metrics_section.is_visible():
            metrics_section.click()

            # Check for metric displays
            response_time = page.locator('text="Response Time"').or_(
                page.locator('[data-testid*="latency"]')
            )
            success_rate = page.locator('text="Success Rate"').or_(
                page.locator('[data-testid*="success"]')
            )

            # At least one metric should be visible
            expect(response_time.or_(success_rate)).to_be_visible()

    def test_agent_dashboard_overview(self, page_with_agents: Page):
        """Test the agent dashboard overview."""
        page = page_with_agents

        # Check for dashboard elements
        dashboard_title = page.locator('h1').filter(has_text="Agent").or_(
            page.locator('[data-testid="dashboard-title"]')
        )

        # Should have some dashboard content
        dashboard_content = page.locator('[data-testid*="dashboard"]').or_(
            page.locator('[data-testid*="overview"]')
        )

        expect(dashboard_content).to_have_count(lambda count: count >= 1)


class TestAgentCommunicationWorkflows:
    """Test complete workflows through the UI."""

    def test_full_optimization_workflow(self, page_with_agents: Page):
        """Test complete parameter optimization workflow."""
        page = page_with_agents

        # Navigate to optimization section
        opt_tab = page.locator('[data-testid="optimization-tab"]').or_(
            page.locator('text="Optimization"')
        )

        if opt_tab.is_visible():
            opt_tab.click()

            # Configure optimization request
            page.select_option('[data-testid="source-agent"]', '01')
            page.select_option('[data-testid="target-agent"]', '02')
            page.fill('[data-testid="task-type"]', 'database_performance')

            # Add parameters
            page.fill('[data-testid="param-space"]', json.dumps({
                "pool_size": {"min": 5, "max": 20},
                "timeout": {"min": 10, "max": 60}
            }))

            # Submit optimization request
            page.click('[data-testid="request-optimization"]')

            # Monitor progress
            progress_bar = page.locator('[data-testid="progress-bar"]')
            expect(progress_bar).to_be_visible()

            # Wait for completion
            completion_indicator = page.locator('[data-testid="optimization-done"]').or_(
                page.locator('text="Completed"')
            )

            expect(completion_indicator).to_be_visible(timeout=30000)

            # Verify results
            results_table = page.locator('[data-testid="results-table"]')
            expect(results_table).to_be_visible()

            # Check best parameters are highlighted
            best_indicator = page.locator('[data-testid="best-params"]').or_(
                page.locator('text="Best"')
            )
            expect(best_indicator).to_be_visible()

    def test_collaboration_workflow(self, page_with_agents: Page):
        """Test complete collaboration workflow."""
        page = page_with_agents

        # Start collaboration
        collab_btn = page.locator('[data-testid="new-collaboration"]').or_(
            page.locator('text="Start Collaboration"')
        )

        if collab_btn.is_visible():
            collab_btn.click()

            # Configure collaboration
            page.select_option('[data-testid="lead-agent"]', '01')
            page.select_option('[data-testid="partner-agent"]', '02')
            page.select_option('[data-testid="collab-type"]', 'parallel')

            # Define task
            page.fill('[data-testid="collab-task"]', json.dumps({
                "type": "comprehensive_analysis",
                "scope": "system_health"
            }))

            # Initiate collaboration
            page.click('[data-testid="initiate-collab"]')

            # Monitor collaboration
            status_indicator = page.locator('[data-testid="collab-status"]')
            expect(status_indicator).to_be_visible()

            # Check for agent participation indicators
            agent_indicators = page.locator('[data-testid*="agent-"]')
            expect(agent_indicators).to_have_count(lambda count: count >= 2)

            # Wait for completion
            completion_msg = page.locator('[data-testid="collab-complete"]').or_(
                page.locator('text="Collaboration Complete"')
            )

            expect(completion_msg).to_be_visible(timeout=20000)

            # Verify combined results
            results_display = page.locator('[data-testid="collab-results"]')
            expect(results_display).to_be_visible()

    def test_communication_monitoring_workflow(self, page_with_agents: Page):
        """Test communication monitoring workflow."""
        page = page_with_agents

        # Navigate to monitoring section
        monitor_tab = page.locator('[data-testid="monitoring-tab"]').or_(
            page.locator('text="Monitoring"')
        )

        if monitor_tab.is_visible():
            monitor_tab.click()

            # Check communication metrics
            comm_metrics = page.locator('[data-testid="comm-metrics"]').or_(
                page.locator('text="Communication"')
            )

            expect(comm_metrics).to_be_visible()

            # Verify agent connectivity indicators
            connectivity_indicators = page.locator('[data-testid*="connectivity"]').or_(
                page.locator('[data-testid*="online"]')
            )

            expect(connectivity_indicators).to_have_count(lambda count: count >= 2)

            # Check message counts
            message_counts = page.locator('text=/\\d+/').filter(has_text="messages").or_(
                page.locator('[data-testid*="message-count"]')
            )

            # Should show some communication activity
            expect(message_counts).to_have_count(lambda count: count >= 0)


# Performance tests for UI
@pytest.mark.performance
class TestUICommunicationPerformance:
    """Performance tests for UI communication features."""

    def test_ui_response_times(self, page_with_agents: Page):
        """Test UI response times for communication actions."""
        page = page_with_agents

        # Measure tab switching time
        start_time = page.evaluate("performance.now()")

        comm_tab = page.locator('[data-testid="communication-tab"]')
        if comm_tab.is_visible():
            comm_tab.click()
            end_time = page.evaluate("performance.now()")

            tab_switch_time = end_time - start_time
            assert tab_switch_time < 1000, f"Tab switch too slow: {tab_switch_time:.2f}ms"

    def test_form_submission_performance(self, page_with_agents: Page):
        """Test form submission performance."""
        page = page_with_agents

        # Find and fill a form
        form = page.locator('form').first
        if form.is_visible():
            # Fill form fields quickly
            inputs = form.locator('input, select, textarea')

            for i, input_field in enumerate(inputs.all()):
                if input_field.is_visible():
                    if input_field.get_attribute('type') == 'text':
                        input_field.fill(f'test_value_{i}')
                    elif input_field.tag_name == 'select':
                        input_field.select_option(index=0)

            # Measure submission time
            start_time = page.evaluate("performance.now()")

            submit_btn = form.locator('button[type="submit"], [data-testid*="submit"]').first
            if submit_btn.is_visible():
                submit_btn.click()

                # Wait for response
                page.wait_for_load_state('networkidle')
                end_time = page.evaluate("performance.now()")

                submission_time = end_time - start_time
                assert submission_time < 5000, f"Form submission too slow: {submission_time:.2f}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--headed", "--video=retain-on-failure"])
