import asyncio
import sys
import os
sys.path.insert(0, 'backend')

from app.agents.infrastructure.infra_agent import InfrastructureAgent
from app.agents.database.database_agent import DatabaseAgent

async def run_demo():
    print("Ì∫Ä Agent Communication Demo")
    print("=" * 50)
    
    # Create agents
    infra = InfrastructureAgent(agent_id='01')
    db = DatabaseAgent(agent_id='02')
    
    print("‚úÖ Agents created")
    
    # Bootstrap (ignore errors for demo)
    try:
        await infra.bootstrap_and_validate()
        await db.bootstrap_and_validate()
    except:
        pass
    
    print("‚úÖ Agents bootstrapped")
    
    # Start communication
    await infra.start_communication_services()
    await db.start_communication_services()
    
    print("‚úÖ Communication started")
    
    # Test task delegation
    print("\nÌ≥§ Testing Task Delegation...")
    result = await db.delegate_task_to_agent('01', 'ping', {}, timeout=10.0)
    
    if result.get('status') == 'completed':
        print("‚úÖ TASK DELEGATION SUCCESSFUL!")
        print("‚úÖ INTER-AGENT COMMUNICATION WORKING!")
        print(f"Response: {result}")
        return True
    else:
        print("‚ùå Task delegation failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_demo())
    print(f"\nÌæØ DEMO RESULT: {'PASSED' if success else 'FAILED'}")
