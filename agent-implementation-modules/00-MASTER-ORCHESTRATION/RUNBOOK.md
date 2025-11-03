# Master Orchestrator Agent Runbook

## Overview

The Master Orchestrator Agent (MOA) is the central coordination system for the Meta-Recursive Multi-Agent Orchestration project. Unlike other agents that implement specific functionality, the MOA monitors, coordinates, and manages the entire development process.

**Key Responsibilities:**
- Monitor all 12 development agents
- Coordinate integration of agent work
- Resolve conflicts between agents
- Track project timeline and progress
- Generate reports and dashboards
- Make final decisions about integration

## Quick Start

### 1. Initialize MOA

```bash
# Navigate to backend directory
cd backend

# Run bootstrap validation
python -m app.agents.master_orchestrator_cli bootstrap
```

### 2. Check System Status

```bash
# Get daily status report
python -m app.agents.master_orchestrator_cli status

# Monitor all agents
python -m app.agents.master_orchestrator_cli monitor
```

### 3. Coordinate Integration

```bash
# Check if agent is ready for integration
python -m app.agents.master_orchestrator_cli status 03

# Integrate agent's work
python -m app.agents.master_orchestrator_cli integrate 03
```

## Command Reference

### Monitoring Commands

#### `status [agent_id]`
Show status of all agents or a specific agent.

```bash
# Show all agents status
python -m app.agents.master_orchestrator_cli status

# Show specific agent status
python -m app.agents.master_orchestrator_cli status 03
```

**Output:**
```
📊 DAILY AGENT STATUS REPORT
Date: 2025-10-30
Week: 3/11

🎯 Overall Progress: 25.0%

🤖 Agent Status:
   ✅ Agent 01: Infrastructure (completed, 100.0%)
   🔄 Agent 02: Database (in_progress, 75.0%)
   🔨 Agent 03: Core Engine (in_progress, 60.0%)
   ...
```

#### `monitor`
Update status of all agents by checking their branches and activity.

```bash
python -m app.agents.master_orchestrator_cli monitor
```

**Output:**
```
🔍 Monitoring all agents...
✅ Monitoring complete
📊 Monitored 12 agents
🕒 Timestamp: 2025-10-30T10:30:00

📈 Status Summary:
   in_progress: 5 agents
   ready_for_integration: 2 agents
   completed: 3 agents
   not_started: 2 agents
```

#### `timeline`
Show project timeline status and progress.

```bash
python -m app.agents.master_orchestrator_cli timeline
```

**Output:**
```
📅 Project Timeline Status
========================================
Current Week: 3/11
Expected Progress: 27.3%
Actual Progress: 25.0%
On Track: ✅
Completed Agents: 3/12
Weeks Remaining: 8
```

### Coordination Commands

#### `integrate <agent_id>`
Coordinate integration of an agent's work into the main codebase.

```bash
# Integrate Agent 03
python -m app.agents.master_orchestrator_cli integrate 03
```

**Success Output:**
```
🔗 Coordinating integration for Agent 03...
✅ Integration successful!
📝 Agent 03 successfully integrated
🧪 Tests: 45/50 passed
🔀 Merged to: develop
```

**Failure Output:**
```
🔗 Coordinating integration for Agent 03...
❌ Integration failed!
📝 Error: Integration tests failed
🧪 Test failures: 3
```

#### `resolve <agent1> <agent2>`
Resolve conflicts between two agents.

```bash
# Resolve conflicts between Agent 03 and 04
python -m app.agents.master_orchestrator_cli resolve 03 04
```

**Output:**
```
⚖️  Resolving conflicts between Agent 03 and Agent 04...
✅ Conflict resolution successful!
📊 Total conflicts: 1
🤖 Auto-resolved: 1
👤 Manual needed: 0
```

### Reporting Commands

#### `report`
Generate comprehensive status report.

```bash
python -m app.agents.master_orchestrator_cli report
```

**Output:**
```
📋 Project Status Report
==================================================

Generated: 2025-10-30T10:30:00

🎯 Project Overview:
   Name: Meta-Recursive Multi-Agent Orchestration
   Total Agents: 12
   Progress: 25.0%
   Week: 3/11

🔗 Integration Status:
   Ready Branches: 2
   Tests Passing: 180/200
   Coverage: 87.5%
   Last Integration: 2025-10-30T09:15:00

🚨 Critical Items:
   Blockers: 1
   Conflicts: 0
   Failing Agents: 0
```

#### `dashboard`
Show full dashboard data (JSON format).

```bash
python -m app.agents.master_orchestrator_cli dashboard
```

#### `alerts`
Show active alerts.

```bash
python -m app.agents.master_orchestrator_cli alerts
```

**Output:**
```
🚨 Active Alerts
==============================
1. ⚠️ 1 Active Blockers
   Agents have blockers that need resolution
   🕒 2025-10-30T10:30:00
```

### System Commands

#### `bootstrap`
Run bootstrap validation to ensure MOA is properly configured.

```bash
python -m app.agents.master_orchestrator_cli bootstrap
```

**Output:**
```
🔍 Running bootstrap validation...
📋 Bootstrap Validation Results
========================================
✅ Bootstrap successful!

Validation Checks:
   ✅ Git Repository
   ✅ Agent Branches
   ✅ Project Structure
   ✅ Agents Initialized
```

## Agent Lifecycle Management

### 1. Agent Development Phase

During development, agents work in isolation:

```bash
# Agent creates feature branch
git checkout -b agent-XX-feature-name

# Agent develops and tests in isolation
# Tests run with: AGENT_ID=XX pytest tests/agentXX/

# Agent requests integration
# MOA checks status
python -m app.agents.master_orchestrator_cli status XX
```

### 2. Integration Phase

When agent is ready for integration:

```bash
# MOA validates agent readiness
python -m app.agents.master_orchestrator_cli integrate XX

# If successful, agent work is merged to develop
# If failed, agent fixes issues and tries again
```

### 3. Conflict Resolution Phase

If conflicts arise between agents:

```bash
# MOA detects conflicts during integration
python -m app.agents.master_orchestrator_cli resolve XX YY

# MOA attempts auto-resolution
# If manual resolution needed, MOA provides guidance
```

## Monitoring and Alerts

### Automatic Monitoring

The MOA continuously monitors:

- **Agent Activity**: Git commits, test runs, branch status
- **Test Results**: Pass/fail rates, coverage metrics
- **Integration Status**: Ready branches, merge conflicts
- **Timeline Adherence**: Progress vs. schedule
- **System Health**: Database connections, service availability

### Alert Types

- **🚨 Critical**: Agent integration failures, system outages
- **⚠️ Warning**: Timeline delays, test failures, resource conflicts
- **ℹ️ Info**: Milestone completions, status updates

### Daily Report

The MOA generates a daily status report that includes:

- Overall project progress
- Individual agent statuses
- Critical blockers and issues
- Timeline status
- Next action recommendations

## Troubleshooting

### Common Issues

#### MOA Won't Start
```bash
# Check Python environment
python --version
pip list | grep fastapi

# Check project structure
ls -la agent-implementation-modules/
ls -la backend/app/agents/
```

#### Agent Status Not Updating
```bash
# Force refresh of all agent statuses
python -m app.agents.master_orchestrator_cli monitor

# Check specific agent
python -m app.agents.master_orchestrator_cli status XX
```

#### Integration Failing
```bash
# Check agent readiness
python -m app.agents.master_orchestrator_cli status XX

# Review test failures
# Check agent branch for issues
git log agent-XX-name --oneline -10
```

#### Bootstrap Validation Failing
```bash
# Check Git repository
git status
git branch -a

# Check project structure
find . -name "*.py" | head -10

# Check agent branches
git branch | grep agent-
```

### Recovery Procedures

#### Recover from Failed Integration
```bash
# Identify failed agent
python -m app.agents.master_orchestrator_cli status

# Check error details
python -m app.agents.master_orchestrator_cli integrate XX  # Shows detailed errors

# Agent fixes issues in their branch
git checkout agent-XX-name
# Fix issues...

# Try integration again
python -m app.agents.master_orchestrator_cli integrate XX
```

#### Reset MOA State
```bash
# Stop MOA
pkill -f master_orchestrator

# Clear any cached state
rm -rf /tmp/moa_*

# Restart with fresh state
python -m app.agents.master_orchestrator_cli bootstrap
```

## Configuration

### Environment Variables

```bash
# MOA Configuration
MOA_LOG_LEVEL=INFO
MOA_REPORT_INTERVAL=3600  # Seconds
MOA_AUTO_RESOLVE=true

# Git Configuration
GIT_REMOTE=origin
GIT_DEVELOP_BRANCH=develop
GIT_MAIN_BRANCH=main

# Agent Configuration
AGENT_TIMEOUT=300  # Integration timeout
AGENT_TEST_THRESHOLD=90  # Minimum coverage %
```

### Configuration File

Create `config/moa_config.yaml`:

```yaml
moa:
  log_level: INFO
  report_interval: 3600
  auto_resolve: true

git:
  remote: origin
  develop_branch: develop
  main_branch: main

agents:
  timeout: 300
  test_threshold: 90
  max_parallel_integrations: 3

monitoring:
  health_check_interval: 60
  alert_email: alerts@company.com
```

## API Reference

### Programmatic Interface

```python
from app.agents.master_orchestrator import MasterOrchestrator

# Initialize MOA
moa = MasterOrchestrator()

# Check agent status
status = await moa._check_agent_status("03")

# Coordinate integration
result = await moa._coordinate_integration("03")

# Generate report
report = await moa._generate_status_report()

# Get dashboard data
dashboard = moa.get_dashboard_data()
```

### REST API (Future)

The MOA will expose a REST API for web dashboard integration:

```
GET  /api/v1/status          # Get all agent statuses
GET  /api/v1/status/{id}     # Get specific agent status
POST /api/v1/integrate/{id}  # Trigger integration
GET  /api/v1/timeline        # Get timeline status
GET  /api/v1/dashboard       # Get dashboard data
GET  /api/v1/alerts          # Get active alerts
```

## Performance Metrics

### MOA Performance Targets

- **Integration Time**: <2 hours average
- **Conflict Resolution**: <4 hours average
- **Status Update**: <30 seconds
- **Report Generation**: <10 seconds
- **Uptime**: 99.9%

### Monitoring MOA Performance

```bash
# Check MOA performance metrics
python -c "
from app.agents.master_orchestrator import MasterOrchestrator
import asyncio

async def check_moa():
    moa = MasterOrchestrator()
    metrics = await moa.report_metrics()
    print('MOA Performance:', metrics)

asyncio.run(check_moa())
"
```

## Integration with CI/CD

### GitHub Actions Integration

```yaml
# .github/workflows/moa-integration.yml
name: MOA Integration Checks

on:
  pull_request:
    branches: [ develop ]

jobs:
  moa-validation:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run MOA validation
        run: |
          python -m app.agents.master_orchestrator_cli bootstrap
          python -m app.agents.master_orchestrator_cli monitor
      
      - name: Generate MOA report
        run: python -m app.agents.master_orchestrator_cli report > moa_report.txt
      
      - name: Upload MOA report
        uses: actions/upload-artifact@v3
        with:
          name: moa-report
          path: moa_report.txt
```

### Automated Integration

```bash
#!/bin/bash
# scripts/auto-integrate.sh

# Run by CI/CD when agent branches are ready

AGENT_ID=$1

if [ -z "$AGENT_ID" ]; then
    echo "Usage: ./scripts/auto-integrate.sh <agent_id>"
    exit 1
fi

echo "🤖 MOA: Starting automated integration for Agent $AGENT_ID"

# Check if agent is ready
python -m app.agents.master_orchestrator_cli status $AGENT_ID > status.json

if grep -q '"status": "ready_for_integration"' status.json; then
    echo "✅ Agent $AGENT_ID is ready for integration"
    
    # Attempt integration
    if python -m app.agents.master_orchestrator_cli integrate $AGENT_ID; then
        echo "🎉 Integration successful!"
        exit 0
    else
        echo "❌ Integration failed"
        exit 1
    fi
else
    echo "⏳ Agent $AGENT_ID is not ready for integration yet"
    exit 1
fi
```

## Best Practices

### For Agent Developers

1. **Keep MOA Informed**: Update agent status regularly
2. **Test Thoroughly**: Ensure >90% coverage before integration
3. **Document Changes**: Clear commit messages and PR descriptions
4. **Resolve Conflicts Quickly**: Don't let conflicts fester
5. **Monitor Integration**: Check MOA status after pushing changes

### For MOA Operators

1. **Daily Monitoring**: Run status checks every morning
2. **Proactive Integration**: Integrate ready agents promptly
3. **Conflict Prevention**: Monitor for potential conflicts early
4. **Clear Communication**: Keep all agents informed of status
5. **Data-Driven Decisions**: Use metrics to guide prioritization

### For Project Managers

1. **Trust the MOA**: Let it coordinate the technical integration
2. **Focus on Blockers**: Use MOA alerts to identify issues
3. **Timeline Awareness**: Monitor timeline adherence
4. **Resource Allocation**: Use MOA data to allocate resources
5. **Success Metrics**: Track integration success rates

## FAQ

### Q: How does MOA differ from a traditional project manager?

A: MOA is a technical coordination system that monitors code, runs tests, and manages integrations automatically. It handles the technical coordination while human project managers focus on business aspects.

### Q: Can MOA integrate work automatically?

A: MOA can automatically integrate work that passes all tests and has no conflicts. Manual intervention is required for test failures or complex conflicts.

### Q: What happens if agents work on conflicting features?

A: MOA detects conflicts during integration attempts and attempts auto-resolution. If auto-resolution fails, MOA provides detailed conflict information for manual resolution.

### Q: How often should I check MOA status?

A: Run `status` daily for overall project view. Run `monitor` when you need fresh data on all agents. Integration attempts trigger automatic monitoring.

### Q: Can MOA be customized for different projects?

A: Yes, MOA is configurable via environment variables and config files. The agent registry, timeline, and integration rules can all be customized.

### Q: What if MOA itself fails?

A: MOA is designed with fail-safes. Individual agent monitoring failures don't stop the system. Bootstrap validation ensures MOA starts in a known good state.

---

## 📞 Support

For MOA issues:
1. Check this runbook first
2. Run bootstrap validation: `moa bootstrap`
3. Check logs in `logs/moa.log`
4. Contact the MOA development team

## 📈 Success Metrics

Track these metrics to ensure MOA effectiveness:

- **Integration Success Rate**: Target >95%
- **Average Integration Time**: Target <2 hours
- **Conflict Resolution Time**: Target <4 hours
- **False Positive Alerts**: Target <5%
- **Agent Satisfaction**: Target >90% (survey)

---

**Document Version:** 1.0  
**Date:** 2025-10-30  
**Status:** MASTER ORCHESTRATOR OPERATIONAL  
**Next:** Integration with CI/CD pipeline

**🎯 MOA READY TO COORDINATE ALL AGENTS**
