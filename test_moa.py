#!/usr/bin/env python3
"""
Test script for Master Orchestrator Agent
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.master_orchestrator import MasterOrchestrator

async def test_moa():
    print('🧪 Testing Master Orchestrator Agent...')

    try:
        # Initialize MOA
        moa = MasterOrchestrator()
        print('✅ MOA initialized successfully')

        # Test agent registry
        assert len(moa.agents) == 12, f'Expected 12 agents, got {len(moa.agents)}'
        print('✅ Agent registry loaded (12 agents)')

        # Test agent details
        agent_01 = moa.agents['01']
        assert agent_01.name == 'Infrastructure'
        assert agent_01.agent_id == '01'
        print('✅ Agent details correct')

        # Test bootstrap validation
        result = await moa.bootstrap_and_validate()
        print(f'✅ Bootstrap validation completed (success: {result.success})')

        # Test status generation
        report = await moa._generate_status_report()
        assert 'project_overview' in report
        assert 'agent_status' in report
        assert len(report['agent_status']) == 12
        print('✅ Status report generation working')

        # Test self-evaluation
        evaluation = await moa.self_evaluate()
        assert evaluation['agent_id'] == 'MOA'
        assert 'performance_score' in evaluation
        print('✅ Self-evaluation working')

        # Test daily report
        daily_report = moa.generate_daily_report()
        assert 'DAILY AGENT STATUS REPORT' in daily_report
        assert 'Overall Progress:' in daily_report
        print('✅ Daily report generation working')

        # Test dashboard data
        dashboard = moa.get_dashboard_data()
        assert 'overview' in dashboard
        assert 'agents' in dashboard
        assert len(dashboard['agents']) == 12
        print('✅ Dashboard data generation working')

        print('🎉 All MOA tests passed!')
        return True

    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(test_moa())
    sys.exit(0 if success else 1)
