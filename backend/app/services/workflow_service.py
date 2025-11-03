"""
Workflow Pipeline Service

Comprehensive service for managing and executing workflow pipelines,
scripts, and helper functions with in-memory storage.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import time
import traceback
import uuid

from app.models.workflow import (
    PipelineStatus, ExecutionStatus, ExecutionTrigger, StepType, LogLevel,
    PipelineCreate, PipelineUpdate, PipelineStepCreate, ExecuteRequest,
    PipelineResponse, ExecutionResponse, ScriptCreate, ScriptResponse,
    HelperCreate, HelperResponse, LogEntry, ExecutionLogsResponse
)


class WorkflowService:
    """Service for workflow pipeline management and execution."""
    
    def __init__(self):
        """Initialize the workflow service with in-memory storage."""
        self.pipelines: Dict[str, Dict[str, Any]] = {}
        self.steps: Dict[str, List[Dict[str, Any]]] = {}  # pipeline_id -> steps
        self.scripts: Dict[str, Dict[str, Any]] = {}
        self.helpers: Dict[str, Dict[str, Any]] = {}
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.execution_logs: Dict[str, List[Dict[str, Any]]] = {}  # execution_id -> logs
        self.step_results: Dict[str, Dict[str, Dict[str, Any]]] = {}  # execution_id -> step_id -> result
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample pipelines, scripts, and helpers."""
        # Sample pipelines
        sample_pipelines = [
            {
                'id': '1',
                'name': 'Advanced Code Analysis Pipeline',
                'description': 'Comprehensive codebase analysis with LLM integration',
                'category': 'codebase',
                'status': 'active',
                'configuration': {},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'version': 1,
                'total_executions': 150,
                'successful_executions': 143,
                'failed_executions': 7,
                'avg_execution_time': 2.3,
                'avg_compression_ratio': 0.75
            },
            {
                'id': '2',
                'name': 'Intelligent Error Compression Pipeline',
                'description': 'Smart error log compression with pattern recognition',
                'category': 'errors',
                'status': 'inactive',
                'configuration': {},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'version': 1,
                'total_executions': 85,
                'successful_executions': 75,
                'failed_executions': 10,
                'avg_execution_time': 1.8,
                'avg_compression_ratio': 0.68
            },
            {
                'id': '3',
                'name': 'Test Optimization & Analysis Pipeline',
                'description': 'Advanced test result compression and analysis',
                'category': 'testing',
                'status': 'active',
                'configuration': {},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'version': 1,
                'total_executions': 120,
                'successful_executions': 110,
                'failed_executions': 10,
                'avg_execution_time': 3.1,
                'avg_compression_ratio': 0.72
            },
            {
                'id': '4',
                'name': 'Multi-Log Compression Pipeline',
                'description': 'Unified log compression across multiple sources',
                'category': 'logs',
                'status': 'active',
                'configuration': {},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'version': 1,
                'total_executions': 200,
                'successful_executions': 180,
                'failed_executions': 20,
                'avg_execution_time': 1.5,
                'avg_compression_ratio': 0.65
            }
        ]
        
        for pipeline in sample_pipelines:
            self.pipelines[pipeline['id']] = pipeline
            # Add sample steps
            steps_count = [6, 4, 5, 3][int(pipeline['id']) - 1]
            self.steps[pipeline['id']] = [
                {
                    'id': f"step-{pipeline['id']}-{i+1}",
                    'pipeline_id': pipeline['id'],
                    'name': f"Step {i+1}",
                    'description': f"Pipeline step {i+1}",
                    'step_type': 'script',
                    'order_index': i,
                    'configuration': {},
                    'depends_on': [f"step-{pipeline['id']}-{i}"] if i > 0 else [],
                    'condition': None,
                    'timeout_seconds': 300,
                    'max_retries': 0
                }
                for i in range(steps_count)
            ]
        
        # Sample scripts
        self.scripts = {
            'script-1': {
                'id': 'script-1',
                'name': 'Tokenization Optimizer',
                'description': 'Dynamic script for optimizing tokenization across multiple data types',
                'language': 'python',
                'code': '''def optimize_tokenization(data, context):
    # Advanced tokenization optimization logic
    compressed_data = apply_semantic_compression(data)
    return compressed_data''',
                'parameters': ['data', 'context', 'compression_level'],
                'llm_integration': True,
                'version': 1,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_approved': True,
                'total_executions': 45,
                'successful_executions': 43,
                'failed_executions': 2
            },
            'script-2': {
                'id': 'script-2',
                'name': 'Codebase Context Extractor',
                'description': 'Intelligent codebase context extraction with LLM assistance',
                'language': 'python',
                'code': '''def extract_codebase_context(files, depth=3):
    # Extract semantic context from codebase
    context = analyze_code_structure(files, depth)
    return compress_context(context)''',
                'parameters': ['files', 'depth', 'include_metadata'],
                'llm_integration': True,
                'version': 1,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_approved': False,
                'total_executions': 12,
                'successful_executions': 12,
                'failed_executions': 0
            }
        }
        
        # Sample helpers
        self.helpers = {
            'helper-1': {
                'id': 'helper-1',
                'name': 'Semantic Compression Helper',
                'category': 'compression',
                'description': 'Advanced semantic compression utilities',
                'functions': [
                    'compress_semantic_data()',
                    'preserve_context_meaning()',
                    'optimize_token_usage()',
                    'extract_key_patterns()'
                ],
                'implementation': None,
                'created_at': datetime.utcnow(),
                'total_invocations': 250
            },
            'helper-2': {
                'id': 'helper-2',
                'name': 'LLM Integration Helper',
                'category': 'llm',
                'description': 'LLM and agent integration utilities',
                'functions': [
                    'generate_compression_prompt()',
                    'analyze_llm_response()',
                    'optimize_agent_communication()',
                    'extract_agent_insights()'
                ],
                'implementation': None,
                'created_at': datetime.utcnow(),
                'total_invocations': 180
            },
            'helper-3': {
                'id': 'helper-3',
                'name': 'Codebase Analysis Helper',
                'category': 'codebase',
                'description': 'Codebase analysis and context extraction utilities',
                'functions': [
                    'analyze_code_structure()',
                    'extract_dependencies()',
                    'identify_patterns()',
                    'compress_code_context()'
                ],
                'implementation': None,
                'created_at': datetime.utcnow(),
                'total_invocations': 320
            }
        }
    
    # ========================================================================
    # PIPELINE CRUD OPERATIONS
    # ========================================================================
    
    async def create_pipeline(self, pipeline_create: PipelineCreate) -> PipelineResponse:
        """Create a new workflow pipeline."""
        pipeline_id = str(uuid.uuid4())
        pipeline = {
            'id': pipeline_id,
            'name': pipeline_create.name,
            'description': pipeline_create.description,
            'category': pipeline_create.category.value,
            'status': pipeline_create.status.value,
            'configuration': pipeline_create.configuration,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'version': 1,
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'avg_execution_time': 0.0,
            'avg_compression_ratio': None
        }
        
        self.pipelines[pipeline_id] = pipeline
        self.steps[pipeline_id] = []
        
        return PipelineResponse(**pipeline)
    
    async def get_pipeline(self, pipeline_id: str) -> Optional[PipelineResponse]:
        """Get a pipeline by ID."""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
        
        return PipelineResponse(**pipeline)
    
    async def list_pipelines(
        self,
        status: Optional[PipelineStatus] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PipelineResponse]:
        """List all pipelines with optional filtering."""
        pipelines = list(self.pipelines.values())
        
        if status:
            pipelines = [p for p in pipelines if p['status'] == status.value]
        
        if category:
            pipelines = [p for p in pipelines if p['category'] == category]
        
        # Sort by updated_at desc
        pipelines.sort(key=lambda x: x['updated_at'], reverse=True)
        
        # Apply pagination
        pipelines = pipelines[offset:offset + limit]
        
        return [PipelineResponse(**p) for p in pipelines]
    
    async def update_pipeline(
        self,
        pipeline_id: str,
        pipeline_update: PipelineUpdate
    ) -> Optional[PipelineResponse]:
        """Update a pipeline."""
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return None
        
        # Update fields
        update_data = pipeline_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['category', 'status'] and value:
                pipeline[field] = value.value
            elif value is not None:
                pipeline[field] = value
        
        pipeline['updated_at'] = datetime.utcnow()
        pipeline['version'] += 1
        
        return PipelineResponse(**pipeline)
    
    async def delete_pipeline(self, pipeline_id: str) -> bool:
        """Delete a pipeline."""
        if pipeline_id not in self.pipelines:
            return False
        
        del self.pipelines[pipeline_id]
        if pipeline_id in self.steps:
            del self.steps[pipeline_id]
        
        return True
    
    # ========================================================================
    # PIPELINE STEP OPERATIONS
    # ========================================================================
    
    async def add_step(
        self,
        pipeline_id: str,
        step_create: PipelineStepCreate
    ) -> Optional[Dict[str, Any]]:
        """Add a step to a pipeline."""
        if pipeline_id not in self.pipelines:
            return None
        
        step_id = str(uuid.uuid4())
        step = {
            'id': step_id,
            'pipeline_id': pipeline_id,
            'name': step_create.name,
            'description': step_create.description,
            'step_type': step_create.step_type.value,
            'order_index': step_create.order_index,
            'configuration': step_create.configuration,
            'depends_on': step_create.depends_on,
            'condition': step_create.condition,
            'timeout_seconds': step_create.timeout_seconds,
            'max_retries': step_create.max_retries,
            'retry_delay_seconds': step_create.retry_delay_seconds
        }
        
        if pipeline_id not in self.steps:
            self.steps[pipeline_id] = []
        
        self.steps[pipeline_id].append(step)
        self.pipelines[pipeline_id]['updated_at'] = datetime.utcnow()
        
        return {
            'id': step['id'],
            'pipeline_id': step['pipeline_id'],
            'name': step['name'],
            'step_type': step['step_type'],
            'order_index': step['order_index']
        }
    
    async def get_pipeline_steps(self, pipeline_id: str) -> List[Dict[str, Any]]:
        """Get all steps for a pipeline."""
        steps = self.steps.get(pipeline_id, [])
        steps.sort(key=lambda x: x['order_index'])
        return steps
    
    # ========================================================================
    # PIPELINE EXECUTION
    # ========================================================================
    
    async def execute_pipeline(
        self,
        execute_request: ExecuteRequest
    ) -> ExecutionResponse:
        """Execute a pipeline asynchronously."""
        pipeline = self.pipelines.get(execute_request.pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {execute_request.pipeline_id} not found")
        
        steps = self.steps.get(execute_request.pipeline_id, [])
        steps.sort(key=lambda x: x['order_index'])
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution = {
            'id': execution_id,
            'pipeline_id': pipeline['id'],
            'status': ExecutionStatus.RUNNING.value,
            'started_at': datetime.utcnow(),
            'completed_at': None,
            'execution_time_ms': None,
            'trigger_type': execute_request.trigger_type.value,
            'total_steps': len(steps),
            'completed_steps': 0,
            'failed_steps': 0,
            'result': {},
            'error': None
        }
        
        self.executions[execution_id] = execution
        self.execution_logs[execution_id] = []
        self.step_results[execution_id] = {}
        
        # Log start
        await self._add_log(
            execution_id,
            LogLevel.INFO,
            f"Starting pipeline execution: {pipeline['name']}",
            None
        )
        
        # Execute steps
        try:
            start_time = time.time()
            results = {}
            
            for step in steps:
                # Check dependencies
                if not await self._check_dependencies(step, results):
                    await self._add_log(
                        execution_id,
                        LogLevel.WARNING,
                        f"Skipping step {step['name']} due to unmet dependencies",
                        step['id']
                    )
                    continue
                
                # Execute step
                step_result = await self._execute_step(
                    execution_id,
                    step,
                    execute_request.parameters,
                    results
                )
                
                results[step['id']] = step_result
                
                if step_result.get('status') == ExecutionStatus.COMPLETED.value:
                    execution['completed_steps'] += 1
                else:
                    execution['failed_steps'] += 1
            
            # Calculate execution time
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update execution
            execution['status'] = ExecutionStatus.COMPLETED.value
            execution['completed_at'] = datetime.utcnow()
            execution['execution_time_ms'] = execution_time
            execution['result'] = results
            
            # Update pipeline stats
            pipeline['total_executions'] += 1
            pipeline['successful_executions'] += 1
            if pipeline['avg_execution_time'] == 0:
                pipeline['avg_execution_time'] = execution_time / 1000
            else:
                pipeline['avg_execution_time'] = (
                    pipeline['avg_execution_time'] * (pipeline['total_executions'] - 1) + 
                    execution_time / 1000
                ) / pipeline['total_executions']
            
            await self._add_log(
                execution_id,
                LogLevel.INFO,
                f"Pipeline execution completed successfully in {execution_time}ms",
                None
            )
            
        except Exception as e:
            # Handle execution failure
            execution['status'] = ExecutionStatus.FAILED.value
            execution['completed_at'] = datetime.utcnow()
            execution['error'] = str(e)
            
            pipeline['total_executions'] += 1
            pipeline['failed_executions'] += 1
            
            await self._add_log(
                execution_id,
                LogLevel.ERROR,
                f"Pipeline execution failed: {str(e)}",
                None,
                {"traceback": traceback.format_exc()}
            )
        
        return ExecutionResponse(**execution)
    
    async def _execute_step(
        self,
        execution_id: str,
        step: Dict[str, Any],
        parameters: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single pipeline step."""
        await self._add_log(
            execution_id,
            LogLevel.INFO,
            f"Executing step: {step['name']}",
            step['id']
        )
        
        try:
            start_time = time.time()
            
            # Execute based on step type
            if step['step_type'] == StepType.SCRIPT.value:
                result = await self._execute_script_step(step, parameters, previous_results)
            elif step['step_type'] == StepType.API_CALL.value:
                result = await self._execute_api_call_step(step, parameters, previous_results)
            elif step['step_type'] == StepType.COMPRESSION.value:
                result = await self._execute_compression_step(step, parameters, previous_results)
            elif step['step_type'] == StepType.TRANSFORMATION.value:
                result = await self._execute_transformation_step(step, parameters, previous_results)
            else:
                result = {"message": f"Step type {step['step_type']} executed"}
            
            execution_time = int((time.time() - start_time) * 1000)
            
            await self._add_log(
                execution_id,
                LogLevel.INFO,
                f"Step {step['name']} completed in {execution_time}ms",
                step['id']
            )
            
            return {
                "status": ExecutionStatus.COMPLETED.value,
                "result": result,
                "execution_time_ms": execution_time
            }
            
        except Exception as e:
            await self._add_log(
                execution_id,
                LogLevel.ERROR,
                f"Step {step['name']} failed: {str(e)}",
                step['id'],
                {"traceback": traceback.format_exc()}
            )
            
            return {
                "status": ExecutionStatus.FAILED.value,
                "error": str(e)
            }
    
    async def _execute_script_step(
        self,
        step: Dict[str, Any],
        parameters: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a script step (simulated for now)."""
        await asyncio.sleep(0.5)  # Simulate execution time
        
        return {
            "step_type": "script",
            "script_executed": True,
            "parameters_received": len(parameters),
            "previous_results_count": len(previous_results)
        }
    
    async def _execute_api_call_step(
        self,
        step: Dict[str, Any],
        parameters: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an API call step."""
        await asyncio.sleep(0.3)  # Simulate API call
        
        return {
            "step_type": "api_call",
            "api_called": True,
            "status_code": 200
        }
    
    async def _execute_compression_step(
        self,
        step: Dict[str, Any],
        parameters: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a compression step."""
        await asyncio.sleep(0.4)  # Simulate compression
        
        return {
            "step_type": "compression",
            "compressed": True,
            "compression_ratio": 3.2,
            "original_size": 1024,
            "compressed_size": 320
        }
    
    async def _execute_transformation_step(
        self,
        step: Dict[str, Any],
        parameters: Dict[str, Any],
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a transformation step."""
        await asyncio.sleep(0.2)  # Simulate transformation
        
        return {
            "step_type": "transformation",
            "transformed": True,
            "records_processed": 100
        }
    
    async def _check_dependencies(
        self,
        step: Dict[str, Any],
        results: Dict[str, Any]
    ) -> bool:
        """Check if step dependencies are met."""
        if not step.get('depends_on'):
            return True
        
        for dep_id in step['depends_on']:
            if dep_id not in results:
                return False
            if results[dep_id].get('status') != ExecutionStatus.COMPLETED.value:
                return False
        
        return True
    
    async def _add_log(
        self,
        execution_id: str,
        level: LogLevel,
        message: str,
        step_id: Optional[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a log entry to the execution."""
        log = {
            'level': level.value,
            'message': message,
            'step_id': step_id,
            'log_metadata': metadata,
            'timestamp': datetime.utcnow()
        }
        
        if execution_id not in self.execution_logs:
            self.execution_logs[execution_id] = []
        
        self.execution_logs[execution_id].append(log)
    
    # ========================================================================
    # EXECUTION MANAGEMENT
    # ========================================================================
    
    async def get_execution(self, execution_id: str) -> Optional[ExecutionResponse]:
        """Get execution details."""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        return ExecutionResponse(**execution)
    
    async def list_executions(
        self,
        pipeline_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ExecutionResponse]:
        """List executions with optional filtering."""
        executions = list(self.executions.values())
        
        if pipeline_id:
            executions = [e for e in executions if e['pipeline_id'] == pipeline_id]
        
        if status:
            executions = [e for e in executions if e['status'] == status.value]
        
        # Sort by started_at desc
        executions.sort(key=lambda x: x['started_at'], reverse=True)
        
        # Apply pagination
        executions = executions[offset:offset + limit]
        
        return [ExecutionResponse(**e) for e in executions]
    
    async def get_execution_logs(
        self,
        execution_id: str,
        level: Optional[LogLevel] = None,
        limit: int = 1000
    ) -> ExecutionLogsResponse:
        """Get logs for an execution."""
        logs = self.execution_logs.get(execution_id, [])
        
        if level:
            logs = [log for log in logs if log['level'] == level.value]
        
        # Apply limit
        logs = logs[:limit]
        
        return ExecutionLogsResponse(
            execution_id=execution_id,
            total_logs=len(logs),
            logs=[LogEntry(**log) for log in logs]
        )
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution."""
        execution = self.executions.get(execution_id)
        if not execution or execution['status'] != ExecutionStatus.RUNNING.value:
            return False
        
        execution['status'] = ExecutionStatus.CANCELLED.value
        execution['completed_at'] = datetime.utcnow()
        
        await self._add_log(
            execution_id,
            LogLevel.WARNING,
            "Execution cancelled by user",
            None
        )
        
        return True
    
    # ========================================================================
    # SCRIPT MANAGEMENT
    # ========================================================================
    
    async def create_script(self, script_create: ScriptCreate) -> ScriptResponse:
        """Create a new dynamic script."""
        script_id = str(uuid.uuid4())
        script = {
            'id': script_id,
            'name': script_create.name,
            'description': script_create.description,
            'language': script_create.language.value,
            'code': script_create.code,
            'parameters': script_create.parameters,
            'llm_integration': script_create.llm_integration,
            'version': 1,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_approved': False,
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0
        }
        
        self.scripts[script_id] = script
        
        return ScriptResponse(**script)
    
    async def list_scripts(
        self,
        language: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ScriptResponse]:
        """List all scripts."""
        scripts = list(self.scripts.values())
        
        if language:
            scripts = [s for s in scripts if s['language'] == language]
        
        # Sort by updated_at desc
        scripts.sort(key=lambda x: x['updated_at'], reverse=True)
        
        # Apply pagination
        scripts = scripts[offset:offset + limit]
        
        return [ScriptResponse(**s) for s in scripts]
    
    # ========================================================================
    # HELPER MANAGEMENT
    # ========================================================================
    
    async def create_helper(self, helper_create: HelperCreate) -> HelperResponse:
        """Create a new helper function library."""
        helper_id = str(uuid.uuid4())
        helper = {
            'id': helper_id,
            'name': helper_create.name,
            'category': helper_create.category,
            'description': helper_create.description,
            'functions': helper_create.functions,
            'implementation': helper_create.implementation,
            'created_at': datetime.utcnow(),
            'total_invocations': 0
        }
        
        self.helpers[helper_id] = helper
        
        return HelperResponse(**helper)
    
    async def list_helpers(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[HelperResponse]:
        """List all helper functions."""
        helpers = list(self.helpers.values())
        
        if category:
            helpers = [h for h in helpers if h['category'] == category]
        
        # Sort by name
        helpers.sort(key=lambda x: x['name'])
        
        # Apply pagination
        helpers = helpers[offset:offset + limit]
        
        return [HelperResponse(**h) for h in helpers]
