"""
Prompt and Template Seeding Service

Ensures default prompts and templates are saved to the database on startup.
Persists across Docker restarts.
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.connection import AsyncSessionLocal
from app.models.prompts import Prompt, PromptTemplate, PromptType, PromptCategory

logger = logging.getLogger(__name__)


class PromptSeedService:
    """Service to seed default prompts and templates into the database."""
    
    def __init__(self):
        self.default_prompts: List[Dict[str, Any]] = []
        self.default_templates: List[Dict[str, Any]] = []
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize default prompts and templates."""
        # Default prompts for agent communication
        self.default_prompts = [
            {
                "name": "agent_ping_prompt",
                "description": "Default ping prompt for agent health checks",
                "content": "Respond with pong and your agent status.",
                "prompt_type": PromptType.SYSTEM,
                "category": PromptCategory.CUSTOM,
                "tags": ["agent", "health", "ping"],
                "keywords": ["ping", "health", "status"],
                "is_template": False,
                "is_active": True
            },
            {
                "name": "agent_task_delegation_prompt",
                "description": "Prompt for task delegation between agents",
                "content": "Execute the following task: {task_description}. Return results with status and metrics.",
                "prompt_type": PromptType.SYSTEM,
                "category": PromptCategory.WORKFLOW,
                "tags": ["agent", "delegation", "task"],
                "keywords": ["task", "delegation", "execution"],
                "is_template": True,
                "is_active": True
            },
            {
                "name": "agent_collaboration_prompt",
                "description": "Prompt for agent collaboration tasks",
                "content": "Collaborate on the following task: {task_description}. Work with {collaborator_agent} to complete this task.",
                "prompt_type": PromptType.SYSTEM,
                "category": PromptCategory.WORKFLOW,
                "tags": ["agent", "collaboration"],
                "keywords": ["collaboration", "teamwork"],
                "is_template": True,
                "is_active": True
            },
            {
                "name": "compression_analysis_prompt",
                "description": "Prompt for compression algorithm analysis",
                "content": "Analyze the compression results for algorithm {algorithm} with level {level}. Provide detailed metrics and recommendations.",
                "prompt_type": PromptType.SYSTEM,
                "category": PromptCategory.COMPRESSION,
                "tags": ["compression", "analysis"],
                "keywords": ["compression", "analysis", "metrics"],
                "is_template": True,
                "is_active": True
            },
            {
                "name": "data_pipeline_prompt",
                "description": "Prompt for data pipeline execution",
                "content": "Execute data pipeline: Extract from {source}, Transform using {method}, Load to {destination}.",
                "prompt_type": PromptType.SYSTEM,
                "category": PromptCategory.WORKFLOW,
                "tags": ["data", "pipeline", "etl"],
                "keywords": ["pipeline", "etl", "data"],
                "is_template": True,
                "is_active": True
            }
        ]
        
        # Default templates
        self.default_templates = [
            {
                "name": "agent_communication_template",
                "description": "Template for agent-to-agent communication",
                "template_content": "Agent {sender_id} requests {action} from Agent {target_id}. Context: {context}",
                "parameters": {
                    "sender_id": {"type": "string", "required": True},
                    "target_id": {"type": "string", "required": True},
                    "action": {"type": "string", "required": True},
                    "context": {"type": "object", "required": False}
                },
                "default_values": {
                    "context": {}
                },
                "category": PromptCategory.WORKFLOW,
                "tags": ["agent", "communication"],
                "is_public": True
            },
            {
                "name": "task_execution_template",
                "description": "Template for task execution prompts",
                "template_content": "Execute task: {task_type} with parameters: {parameters}. Expected output: {expected_output}",
                "parameters": {
                    "task_type": {"type": "string", "required": True},
                    "parameters": {"type": "object", "required": True},
                    "expected_output": {"type": "string", "required": False}
                },
                "default_values": {
                    "expected_output": "Task completion status and results"
                },
                "category": PromptCategory.WORKFLOW,
                "tags": ["task", "execution"],
                "is_public": True
            },
            {
                "name": "compression_optimization_template",
                "description": "Template for compression optimization prompts",
                "template_content": "Optimize compression for content type: {content_type}. Target: {target_metric} = {target_value}",
                "parameters": {
                    "content_type": {"type": "string", "required": True},
                    "target_metric": {"type": "string", "required": True},
                    "target_value": {"type": "number", "required": True}
                },
                "default_values": {
                    "target_metric": "compression_ratio"
                },
                "category": PromptCategory.OPTIMIZATION,
                "tags": ["compression", "optimization"],
                "is_public": True
            }
        ]
    
    async def seed_prompts(self, db: AsyncSession) -> Dict[str, Any]:
        """Seed default prompts into the database."""
        seeded = 0
        skipped = 0
        errors = []
        
        for prompt_data in self.default_prompts:
            try:
                # Check if prompt already exists
                result = await db.execute(
                    select(Prompt).where(Prompt.name == prompt_data["name"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    skipped += 1
                    logger.debug(f"Prompt '{prompt_data['name']}' already exists, skipping")
                    continue
                
                # Create new prompt
                prompt = Prompt(**prompt_data)
                db.add(prompt)
                seeded += 1
                logger.debug(f"Seeded prompt: {prompt_data['name']}")
                
            except Exception as e:
                error_msg = f"Error seeding prompt '{prompt_data.get('name', 'unknown')}': {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        await db.commit()
        
        return {
            "seeded": seeded,
            "skipped": skipped,
            "errors": errors,
            "total": len(self.default_prompts)
        }
    
    async def seed_templates(self, db: AsyncSession) -> Dict[str, Any]:
        """Seed default templates into the database."""
        seeded = 0
        skipped = 0
        errors = []
        
        for template_data in self.default_templates:
            try:
                # Check if template already exists
                result = await db.execute(
                    select(PromptTemplate).where(PromptTemplate.name == template_data["name"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    skipped += 1
                    logger.debug(f"Template '{template_data['name']}' already exists, skipping")
                    continue
                
                # Create new template
                template = PromptTemplate(**template_data)
                db.add(template)
                seeded += 1
                logger.debug(f"Seeded template: {template_data['name']}")
                
            except Exception as e:
                error_msg = f"Error seeding template '{template_data.get('name', 'unknown')}': {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        await db.commit()
        
        return {
            "seeded": seeded,
            "skipped": skipped,
            "errors": errors,
            "total": len(self.default_templates)
        }
    
    async def seed_all(self, db: AsyncSession) -> Dict[str, Any]:
        """Seed all prompts and templates."""
        logger.info("Starting prompt and template seeding...")
        
        prompts_result = await self.seed_prompts(db)
        templates_result = await self.seed_templates(db)
        
        total_seeded = prompts_result["seeded"] + templates_result["seeded"]
        total_skipped = prompts_result["skipped"] + templates_result["skipped"]
        all_errors = prompts_result["errors"] + templates_result["errors"]
        
        result = {
            "prompts": prompts_result,
            "templates": templates_result,
            "total_seeded": total_seeded,
            "total_skipped": total_skipped,
            "total_errors": len(all_errors),
            "errors": all_errors
        }
        
        if all_errors:
            logger.warning(f"Seeding completed with {len(all_errors)} errors")
        else:
            logger.info(f"Seeding completed: {total_seeded} seeded, {total_skipped} skipped")
        
        return result


# Global instance
_seed_service = None

def get_prompt_seed_service() -> PromptSeedService:
    """Get or create the global prompt seed service."""
    global _seed_service
    if _seed_service is None:
        _seed_service = PromptSeedService()
    return _seed_service

