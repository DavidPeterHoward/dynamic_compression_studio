"""
Tests for Master Orchestrator Agent.

Tests cover:
- Agent monitoring and status tracking
- Integration coordination
- Conflict resolution
- Timeline management
- Report generation
- Bootstrap validation
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from app.agents.master_orchestrator import (
    MasterOrchestrator,
    AgentStatus,
    IntegrationStatus,
    AgentInfo
)


@pytest.fixture
def moa():
    """Create Master Orchestrator Agent for testing"""
    return MasterOrchestrator()


@pytest.fixture
def mock_agent():
    """Create mock agent info"""
    return AgentInfo(
        agent_id="03",
        name="Core Engine",
        status=AgentStatus.READY_FOR_INTEGRATION,
        progress=85.0,
        tests_total=50,
        tests_passing=45,
        branch_name="agent-03-core-engine"
    )


@pytest.mark.asyncio
async def test_moa_initialization(moa):
    """Test MOA initializes with correct agent registry"""
    assert len(moa.agents) == 12
    assert "01" in moa.agents
    assert "12" in moa.agents
    assert moa.agents["01"].name == "Infrastructure"
    assert moa.agents["02"].name == "Database"


@pytest.mark.asyncio
async def test_moa_bootstrap_validation_success(moa):
    """Test successful bootstrap validation"""
    # Mock all the checks to return success
    with patch.object(moa, '_check_git_status', return_value=True), \
         patch.object(moa, '_check_agent_branches', return_value=True), \
         patch.object(moa, '_check_project_structure', return_value=True):

        result = await moa.bootstrap_and_validate()

        assert result.success is True
        assert result.validations["git_repository"] is True
        assert result.validations["agent_branches"] is True
        assert result.validations["project_structure"] is True
        assert result.validations["agents_initialized"] is True


@pytest.mark.asyncio
async def test_moa_bootstrap_validation_failure(moa):
    """Test bootstrap validation with failures"""
    with patch.object(moa, '_check_git_status', return_value=False), \
         patch.object(moa, '_check_agent_branches', return_value=True), \
         patch.object(moa, '_check_project_structure', return_value=False):

        result = await moa.bootstrap_and_validate()

        assert result.success is False
        assert result.validations["git_repository"] is False
        assert result.validations["project_structure"] is False


@pytest.mark.asyncio
async def test_moa_monitor_agents(moa):
    """Test monitoring all agents"""
    # Mock the individual agent status checks
    with patch.object(moa, '_check_agent_status') as mock_check:
        mock_check.return_value = {
            "agent_id": "01",
            "status": AgentStatus.IN_PROGRESS,
            "progress": 60.0,
            "recent_commits": 5
        }

        result = await moa._monitor_all_agents()

        assert result["success"] is True
        assert len(result["agent_statuses"]) == 12
        assert "timestamp" in result

        # Verify agent status was updated
        assert moa.agents["01"].status == AgentStatus.IN_PROGRESS
        assert moa.agents["01"].progress == 60.0


@pytest.mark.asyncio
async def test_moa_check_agent_status_ready(moa):
    """Test checking agent status when ready"""
    with patch.object(moa, '_check_branch_exists', return_value=True), \
         patch.object(moa, '_count_recent_commits', return_value=15), \
         patch.object(moa, '_check_tests_exist', return_value=True):

        result = await moa._check_agent_status("03")

        assert result["agent_id"] == "03"
        assert result["status"] == AgentStatus.READY_FOR_INTEGRATION
        assert result["progress"] > 70.0
        assert result["recent_commits"] == 15
        assert result["tests_exist"] is True


@pytest.mark.asyncio
async def test_moa_check_agent_status_not_started(moa):
    """Test checking agent status when not started"""
    with patch.object(moa, '_check_branch_exists', return_value=False), \
         patch.object(moa, '_count_recent_commits', return_value=0), \
         patch.object(moa, '_check_tests_exist', return_value=False):

        result = await moa._check_agent_status("12")

        assert result["agent_id"] == "12"
        assert result["status"] == AgentStatus.NOT_STARTED
        assert result["progress"] == 0.0
        assert result["branch_exists"] is False


@pytest.mark.asyncio
async def test_moa_coordinate_integration_success(moa):
    """Test successful integration coordination"""
    # Set up agent as ready
    agent = moa.agents["03"]
    agent.status = AgentStatus.READY_FOR_INTEGRATION
    agent.dependencies = ["01", "02"]

    # Mock dependencies as completed
    moa.agents["01"].status = AgentStatus.INTEGRATED
    moa.agents["02"].status = AgentStatus.INTEGRATED

    with patch.object(moa, '_run_integration_tests', return_value={"passed": True, "total": 10, "passed_count": 10}), \
         patch.object(moa, '_merge_to_develop', return_value={"success": True, "branch": "agent-03-core-engine"}):

        result = await moa._coordinate_integration("03")

        assert result["success"] is True
        assert "successfully integrated" in result["message"]
        assert agent.status == AgentStatus.INTEGRATED


@pytest.mark.asyncio
async def test_moa_coordinate_integration_not_ready(moa):
    """Test integration coordination when agent not ready"""
    agent = moa.agents["03"]
    agent.status = AgentStatus.IN_PROGRESS  # Not ready

    result = await moa._coordinate_integration("03")

    assert result["success"] is False
    assert "not ready for integration" in result["error"]


@pytest.mark.asyncio
async def test_moa_coordinate_integration_dependencies_unmet(moa):
    """Test integration coordination with unmet dependencies"""
    agent = moa.agents["03"]
    agent.status = AgentStatus.READY_FOR_INTEGRATION
    agent.dependencies = ["01", "02"]

    # Agent 02 not completed
    moa.agents["01"].status = AgentStatus.INTEGRATED
    moa.agents["02"].status = AgentStatus.IN_PROGRESS

    result = await moa._coordinate_integration("03")

    assert result["success"] is False
    assert "unmet dependencies" in result["error"]
    assert "02" in result["dependencies"]


@pytest.mark.asyncio
async def test_moa_resolve_conflicts_no_conflicts(moa):
    """Test conflict resolution when no conflicts exist"""
    with patch.object(moa, '_detect_conflicts', return_value=[]):
        result = await moa._resolve_conflicts("03", "04")

        assert result["success"] is True
        assert result["message"] == "No conflicts detected"


@pytest.mark.asyncio
async def test_moa_resolve_conflicts_auto_resolved(moa):
    """Test conflict resolution with auto-resolution"""
    conflicts = [{
        "type": "resource_conflict",
        "severity": "low",
        "description": "Port overlap detected"
    }]

    with patch.object(moa, '_detect_conflicts', return_value=conflicts), \
         patch.object(moa, '_attempt_auto_resolution', return_value=[{"resolution": "ports_adjusted"}]):

        result = await moa._resolve_conflicts("03", "04")

        assert result["success"] is True
        assert result["total_conflicts"] == 1
        assert result["auto_resolved"] == 1
        assert result["manual_needed"] == 0


@pytest.mark.asyncio
async def test_moa_generate_status_report(moa):
    """Test status report generation"""
    # Set up some test data
    moa.agents["01"].status = AgentStatus.COMPLETED
    moa.agents["02"].status = AgentStatus.IN_PROGRESS
    moa.agents["03"].status = AgentStatus.READY_FOR_INTEGRATION

    result = await moa._generate_status_report()

    assert "timestamp" in result
    assert "project_overview" in result
    assert "agent_status" in result
    assert "integration_status" in result
    assert "critical_items" in result
    assert "timeline" in result

    # Verify agent statuses in report
    assert result["agent_status"]["01"]["status"] == "completed"
    assert result["agent_status"]["02"]["status"] == "in_progress"
    assert result["agent_status"]["03"]["status"] == "ready_for_integration"

    # Verify report was stored
    assert len(moa.reports) == 1


@pytest.mark.asyncio
async def test_moa_check_project_timeline(moa):
    """Test project timeline checking"""
    # Set current week
    moa.timeline.current_week = 3
    moa.timeline.total_weeks = 11

    # Mark some agents as completed
    moa.agents["01"].status = AgentStatus.COMPLETED
    moa.agents["02"].status = AgentStatus.COMPLETED
    moa.agents["03"].status = AgentStatus.COMPLETED

    result = await moa._check_project_timeline()

    assert result["current_week"] == 3
    assert result["total_weeks"] == 11
    assert result["completed_agents"] == 3
    assert result["total_agents"] == 12
    assert "expected_progress" in result
    assert "actual_progress" in result
    assert "on_track" in result


@pytest.mark.asyncio
async def test_moa_self_evaluation(moa):
    """Test MOA self-evaluation"""
    # Set up some test state
    moa.agents["01"].status = AgentStatus.INTEGRATED
    moa.agents["02"].status = AgentStatus.INTEGRATED

    evaluation = await moa.self_evaluate()

    assert evaluation["agent_id"] == "MOA"
    assert evaluation["agent_type"] == "master_orchestrator"
    assert "performance_score" in evaluation
    assert "metrics" in evaluation
    assert "strengths" in evaluation
    assert "weaknesses" in evaluation
    assert "improvement_suggestions" in evaluation

    # Performance score should be integrated_agents / total_agents
    expected_score = 2 / 12  # 2 integrated out of 12 total
    assert evaluation["performance_score"] == expected_score


@pytest.mark.asyncio
async def test_moa_report_metrics(moa):
    """Test metrics reporting"""
    metrics = await moa.report_metrics()

    assert metrics["agent_id"] == "MOA"
    assert metrics["agent_type"] == "master_orchestrator"
    assert metrics["total_agents"] == 12
    assert "integrated_agents" in metrics
    assert "active_conflicts" in metrics
    assert "timeline_on_track" in metrics
    assert "overall_progress" in metrics


def test_moa_generate_daily_report(moa):
    """Test daily report generation"""
    # Set up test data
    moa.agents["01"].status = AgentStatus.COMPLETED
    moa.agents["02"].status = AgentStatus.INTEGRATION_FAILED
    moa.agents["02"].blockers = ["Database connection issue"]

    report = moa.generate_daily_report()

    assert "DAILY AGENT STATUS REPORT" in report
    assert "Overall Progress:" in report
    assert "Agent 01:" in report
    assert "Agent 02:" in report
    assert "Critical Items:" in report
    assert "Database connection issue" in report


def test_moa_get_dashboard_data(moa):
    """Test dashboard data generation"""
    dashboard = moa.get_dashboard_data()

    assert "overview" in dashboard
    assert "agents" in dashboard
    assert "integration" in dashboard
    assert "timeline" in dashboard
    assert "alerts" in dashboard

    # Check overview data
    overview = dashboard["overview"]
    assert overview["total_agents"] == 12
    assert "overall_progress" in overview
    assert "health_status" in overview

    # Check agents data
    agents = dashboard["agents"]
    assert len(agents) == 12
    assert "01" in agents
    assert "name" in agents["01"]
    assert "status" in agents["01"]


@pytest.mark.asyncio
async def test_moa_calculate_overall_progress(moa):
    """Test overall progress calculation"""
    # Set specific progress values
    moa.agents["01"].progress = 100.0
    moa.agents["02"].progress = 50.0
    moa.agents["03"].progress = 25.0
    # Others remain at 0.0

    progress = moa._calculate_overall_progress()
    expected = (100.0 + 50.0 + 25.0) / 12  # 175.0 / 12

    assert progress == pytest.approx(expected, rel=1e-2)


# Integration test - requires actual system
@pytest.mark.asyncio
@pytest.mark.integration
async def test_moa_full_lifecycle():
    """
    Full lifecycle test of MOA.

    Requires actual system setup.
    """
    pytest.skip("Integration test - requires full system setup")

    moa = MasterOrchestrator()

    # Bootstrap
    result = await moa.bootstrap_and_validate()
    assert result.success is True

    # Monitor agents
    monitor_result = await moa._monitor_all_agents()
    assert monitor_result["success"] is True

    # Generate report
    report = await moa._generate_status_report()
    assert "project_overview" in report

    # Self-evaluate
    evaluation = await moa.self_evaluate()
    assert evaluation["performance_score"] >= 0.0

    # Shutdown
    await moa.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
