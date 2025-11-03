"""
Master Orchestrator Agent Command Line Interface

Provides human operators with tools to monitor and control the multi-agent development process.
"""

import asyncio
import json
import sys
import argparse
from datetime import datetime
from typing import Optional, Dict, Any

from master_orchestrator import MasterOrchestrator


class MasterOrchestratorCLI:
    """
    Command-line interface for the Master Orchestrator Agent.

    Provides commands for:
    - Monitoring agent status
    - Coordinating integration
    - Resolving conflicts
    - Managing timeline
    - Generating reports
    """

    def __init__(self):
        self.moa: Optional[MasterOrchestrator] = None

    async def initialize(self):
        """Initialize the MOA"""
        self.moa = MasterOrchestrator()
        await self.moa.initialize()

    async def run_command(self, args):
        """Run a command based on parsed arguments"""
        if not self.moa:
            await self.initialize()

        command = args.command

        try:
            if command == "status":
                await self.cmd_status(args.agent_id)
            elif command == "monitor":
                await self.cmd_monitor()
            elif command == "integrate":
                await self.cmd_integrate(args.agent_id)
            elif command == "resolve":
                await self.cmd_resolve(args.agent1, args.agent2)
            elif command == "timeline":
                await self.cmd_timeline()
            elif command == "report":
                await self.cmd_report()
            elif command == "dashboard":
                await self.cmd_dashboard()
            elif command == "alerts":
                await self.cmd_alerts()
            elif command == "bootstrap":
                await self.cmd_bootstrap()
            else:
                print(f"❌ Unknown command: {command}")
                self.show_help()

        except Exception as e:
            print(f"❌ Error executing command '{command}': {e}")
            sys.exit(1)

    async def cmd_status(self, agent_id: Optional[str]):
        """Show status of agents"""
        if agent_id:
            if agent_id not in self.moa.agents:
                print(f"❌ Unknown agent: {agent_id}")
                return

            status = await self.moa._check_agent_status(agent_id)
            print(json.dumps(status, indent=2))
        else:
            # Show all agents status
            print(self.moa.generate_daily_report())

    async def cmd_monitor(self):
        """Monitor all agents and update status"""
        print("🔍 Monitoring all agents...")
        result = await self.moa._monitor_all_agents()

        print("✅ Monitoring complete")
        print(f"📊 Monitored {len(result['agent_statuses'])} agents")
        print(f"🕒 Timestamp: {result['timestamp']}")

        # Show summary
        statuses = {}
        for agent_id, status in result['agent_statuses'].items():
            status_name = status['status'].value if hasattr(status['status'], 'value') else str(status['status'])
            statuses[status_name] = statuses.get(status_name, 0) + 1

        print("\n📈 Status Summary:")
        for status, count in statuses.items():
            print(f"   {status}: {count} agents")

    async def cmd_integrate(self, agent_id: str):
        """Integrate an agent's work"""
        if agent_id not in self.moa.agents:
            print(f"❌ Unknown agent: {agent_id}")
            return

        print(f"🔗 Coordinating integration for Agent {agent_id}...")

        result = await self.moa._coordinate_integration(agent_id)

        if result["success"]:
            print("✅ Integration successful!")
            print(f"📝 {result['message']}")

            if "tests" in result:
                tests = result["tests"]
                print(f"🧪 Tests: {tests.get('passed_count', 0)}/{tests.get('total', 0)} passed")

            if "merge" in result and result["merge"]["success"]:
                merge = result["merge"]
                print(f"🔀 Merged to: {merge['target']}")
        else:
            print("❌ Integration failed!")
            print(f"📝 Error: {result.get('error', 'Unknown error')}")

            if "test_failures" in result:
                print(f"🧪 Test failures: {len(result['test_failures'])}")

    async def cmd_resolve(self, agent1: str, agent2: str):
        """Resolve conflicts between two agents"""
        print(f"⚖️  Resolving conflicts between Agent {agent1} and Agent {agent2}...")

        result = await self.moa._resolve_conflicts(agent1, agent2)

        if result["success"]:
            print("✅ Conflict resolution successful!")
            if result["auto_resolved"] > 0:
                print(f"🤖 Auto-resolved: {result['auto_resolved']} conflicts")
            if result["manual_needed"] == 0:
                print("✨ No manual intervention needed")
        else:
            print("⚠️  Manual resolution may be needed")
            print(f"📊 Total conflicts: {result['total_conflicts']}")
            print(f"🤖 Auto-resolved: {result['auto_resolved']}")
            print(f"👤 Manual needed: {result['manual_needed']}")

            if result["manual_needed"] > 0:
                print("\n📋 Conflicts requiring manual resolution:")
                for conflict in result.get("conflicts", []):
                    if conflict not in result.get("auto_resolutions", []):
                        print(f"   • {conflict.get('description', 'Unknown conflict')}")

    async def cmd_timeline(self):
        """Show project timeline status"""
        result = await self.moa._check_project_timeline()

        print("📅 Project Timeline Status")
        print("=" * 40)
        print(f"Current Week: {result['current_week']}/{result['total_weeks']}")
        print(".1f")
        print(".1f")
        print(f"On Track: {'✅' if result['on_track'] else '❌'}")
        print(f"Completed Agents: {result['completed_agents']}/{result['total_agents']}")
        print(f"Weeks Remaining: {result['weeks_remaining']}")

        if not result['on_track']:
            print("\n⚠️  Project is behind schedule!")
            print("Consider reallocating resources to accelerate development.")

    async def cmd_report(self):
        """Generate comprehensive status report"""
        print("📊 Generating comprehensive status report...")

        report = await self.moa._generate_status_report()

        print("📋 Project Status Report")
        print("=" * 50)
        print(f"Generated: {report['timestamp']}")
        print()

        # Project overview
        overview = report['project_overview']
        print("🎯 Project Overview:")
        print(f"   Name: {overview['name']}")
        print(f"   Total Agents: {overview['total_agents']}")
        print(f"   Progress: {overview['progress_percentage']:.1f}%")
        print(f"   Week: {overview['current_week']}/{overview['total_weeks']}")
        print()

        # Integration status
        integration = report['integration_status']
        print("🔗 Integration Status:")
        print(f"   Ready Branches: {integration['ready_branches']}")
        print(f"   Tests Passing: {integration['tests_passing']}/{integration['tests_total']}")
        print(".1f")
        if integration['last_integration']:
            print(f"   Last Integration: {integration['last_integration']}")
        print()

        # Critical items
        critical = report['critical_items']
        print("🚨 Critical Items:")
        print(f"   Blockers: {len(critical['blockers'])}")
        print(f"   Conflicts: {critical['conflicts']}")
        print(f"   Failing Agents: {len(critical['failing_agents'])}")
        print()

        # Timeline
        timeline = report['timeline']
        print("⏰ Timeline:")
        print(f"   Weeks Remaining: {timeline['weeks_remaining']}")
        print(f"   On Track: {'✅' if timeline['on_track'] else '❌'}")

    async def cmd_dashboard(self):
        """Show dashboard data"""
        dashboard = self.moa.get_dashboard_data()

        print("📊 Master Orchestrator Dashboard")
        print("=" * 45)

        # Overview
        overview = dashboard['overview']
        print("🎯 Overview:")
        print(f"   Project: {overview['project_name']}")
        print(f"   Agents: {overview['total_agents']}")
        print(f"   Progress: {overview['overall_progress']:.1f}%")
        print(f"   Health: {overview['health_status']}")
        print()

        # Agent summary
        agents = dashboard['agents']
        completed = sum(1 for a in agents.values() if a['status'] == 'integrated')
        in_progress = sum(1 for a in agents.values() if a['status'] == 'in_progress')
        ready = sum(1 for a in agents.values() if a['status'] == 'ready_for_integration')

        print("🤖 Agents Summary:")
        print(f"   Completed: {completed}")
        print(f"   In Progress: {in_progress}")
        print(f"   Ready for Integration: {ready}")
        print(f"   Not Started: {len(agents) - completed - in_progress - ready}")
        print()

        # Alerts
        alerts = dashboard['alerts']
        if alerts:
            print("🚨 Active Alerts:")
            for alert in alerts:
                emoji = "⚠️" if alert['type'] == 'warning' else "❌"
                print(f"   {emoji} {alert['title']}: {alert['message']}")
        else:
            print("✅ No active alerts")

    async def cmd_alerts(self):
        """Show active alerts"""
        dashboard = self.moa.get_dashboard_data()
        alerts = dashboard['alerts']

        if not alerts:
            print("✅ No active alerts")
            return

        print("🚨 Active Alerts")
        print("=" * 30)

        for i, alert in enumerate(alerts, 1):
            emoji = "⚠️" if alert['type'] == 'warning' else "❌"
            print(f"{i}. {emoji} {alert['title']}")
            print(f"   {alert['message']}")
            print(f"   🕒 {alert['timestamp']}")
            print()

    async def cmd_bootstrap(self):
        """Run bootstrap validation"""
        print("🔍 Running bootstrap validation...")

        result = await self.moa.bootstrap_and_validate()

        print("📋 Bootstrap Validation Results")
        print("=" * 40)

        if result.success:
            print("✅ Bootstrap successful!")
        else:
            print("❌ Bootstrap failed!")

        print("\nValidation Checks:")
        for check_name, check_result in result.validations.items():
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name.replace('_', ' ').title()}")

        if not result.success:
            print("
❌ Failed checks:")
            for check_name, check_result in result.validations.items():
                if not check_result:
                    print(f"   • {check_name}")

    def show_help(self):
        """Show help information"""
        help_text = """
Master Orchestrator Agent (MOA) CLI

MONITORING COMMANDS:
  status [agent_id]    Show agent status (all or specific agent)
  monitor              Update status of all agents
  timeline             Show project timeline status
  alerts               Show active alerts
  dashboard            Show full dashboard

COORDINATION COMMANDS:
  integrate <agent_id> Integrate agent's work into main codebase
  resolve <agent1> <agent2> Resolve conflicts between two agents

REPORTING COMMANDS:
  report               Generate comprehensive status report

SYSTEM COMMANDS:
  bootstrap            Run bootstrap validation checks

EXAMPLES:
  python moa_cli.py status              # Show all agents status
  python moa_cli.py status 03           # Show Agent 03 status
  python moa_cli.py integrate 03        # Integrate Agent 03
  python moa_cli.py resolve 03 04       # Resolve conflicts between 03 and 04
  python moa_cli.py timeline            # Check project timeline
  python moa_cli.py dashboard           # Show dashboard
  python moa_cli.py bootstrap           # Validate system bootstrap

For more information, see agent-implementation-modules/00-MASTER-ORCHESTRATION/
"""
        print(help_text)


def create_argument_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Master Orchestrator Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status              # Show all agents status
  %(prog)s status 03           # Show Agent 03 status
  %(prog)s integrate 03        # Integrate Agent 03
  %(prog)s resolve 03 04       # Resolve conflicts between 03 and 04
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show agent status')
    status_parser.add_argument('agent_id', nargs='?', help='Specific agent ID (optional)')

    # Monitor command
    subparsers.add_parser('monitor', help='Monitor all agents')

    # Integrate command
    integrate_parser = subparsers.add_parser('integrate', help='Integrate agent work')
    integrate_parser.add_argument('agent_id', help='Agent ID to integrate')

    # Resolve command
    resolve_parser = subparsers.add_parser('resolve', help='Resolve conflicts between agents')
    resolve_parser.add_argument('agent1', help='First agent ID')
    resolve_parser.add_argument('agent2', help='Second agent ID')

    # Timeline command
    subparsers.add_parser('timeline', help='Show project timeline')

    # Report command
    subparsers.add_parser('report', help='Generate status report')

    # Dashboard command
    subparsers.add_parser('dashboard', help='Show dashboard')

    # Alerts command
    subparsers.add_parser('alerts', help='Show active alerts')

    # Bootstrap command
    subparsers.add_parser('bootstrap', help='Run bootstrap validation')

    return parser


async def main():
    """Main CLI entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = MasterOrchestratorCLI()

    try:
        await cli.run_command(args)
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
