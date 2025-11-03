import { AlertCircle, CheckCircle, Loader, Send, XCircle } from 'lucide-react';
import React, { useState } from 'react';

interface TaskRequest {
  task_id?: string;
  operation: string;
  parameters: Record<string, any>;
  priority?: string;
  timeout_seconds?: number;
}

interface TaskResult {
  task_id: string;
  status: string;
  result?: any;
  error?: string;
  agent_used?: string;
  timestamp: string;
  execution_time_seconds?: number;
}

interface TaskSubmissionFormProps {
  onTaskSubmit?: (task: TaskRequest) => Promise<TaskResult>;
  agents: string[];
}

const TaskSubmissionForm: React.FC<TaskSubmissionFormProps> = ({ onTaskSubmit, agents }) => {
  const [selectedAgent, setSelectedAgent] = useState('');
  const [taskType, setTaskType] = useState('');
  const [taskData, setTaskData] = useState('{}');
  const [priority, setPriority] = useState('normal');
  const [timeout, setTimeout] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<TaskResult | null>(null);
  const [validationError, setValidationError] = useState<string>('');

  // Predefined task templates
  const taskTemplates = {
    compression: {
      operation: 'compression',
      parameters: {
        algorithm: 'gzip',
        data: 'Sample text for compression testing'
      }
    },
    health_check: {
      operation: 'health_check',
      parameters: {
        test: true,
        include_metrics: true
      }
    },
    analysis: {
      operation: 'analysis',
      parameters: {
        target: 'system_performance',
        metrics: ['cpu', 'memory', 'throughput']
      }
    },
    learning: {
      operation: 'learn_from_experience',
      parameters: {
        experience_type: 'performance_data',
        iterations: 10
      }
    }
  };

  const handleTemplateSelect = (template: string) => {
    if (template in taskTemplates) {
      const tpl = taskTemplates[template as keyof typeof taskTemplates];
      setTaskType(tpl.operation);
      setTaskData(JSON.stringify(tpl.parameters, null, 2));
    }
  };

  const validateTaskData = (data: string): boolean => {
    try {
      JSON.parse(data);
      setValidationError('');
      return true;
    } catch (e) {
      setValidationError('Invalid JSON format');
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedAgent || !taskType) {
      setValidationError('Please select an agent and task type');
      return;
    }

    if (!validateTaskData(taskData)) {
      return;
    }

    setIsSubmitting(true);
    setResult(null);
    setValidationError('');

    try {
      let parsedData = {};
      if (taskData.trim()) {
        parsedData = JSON.parse(taskData);
      }

      const task: TaskRequest = {
        task_id: `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        operation: taskType,
        parameters: parsedData,
        priority,
        timeout_seconds: timeout ? parseInt(timeout) : undefined
      };

      if (onTaskSubmit) {
        const result = await onTaskSubmit(task);
        setResult(result);
      } else {
        // If no submit handler, simulate success for UI testing
        const mockResult: TaskResult = {
          task_id: task.task_id!,
          status: 'completed',
          result: { message: 'Task submitted successfully (simulation)' },
          agent_used: selectedAgent,
          timestamp: new Date().toISOString(),
          execution_time_seconds: Math.random() * 2
        };
        setResult(mockResult);
      }
    } catch (error) {
      const errorResult: TaskResult = {
        task_id: `task_${Date.now()}`,
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      };
      setResult(errorResult);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
    }
  };

  const taskTypes = [
    'compression',
    'decompression',
    'analysis',
    'health_check',
    'status',
    'learn_from_experience',
    'generate_insights',
    'adapt_strategy',
    'optimize_parameters',
    'validate_configuration'
  ];

  return (
    <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-600/50">
      <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
        <Send className="w-5 h-5" />
        <span>Submit Task to Agent</span>
      </h3>

      {/* Task Templates */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Quick Templates
        </label>
        <div className="flex flex-wrap gap-2">
          {Object.keys(taskTemplates).map(template => (
            <button
              key={template}
              onClick={() => handleTemplateSelect(template)}
              className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm rounded-lg transition-colors"
            >
              {template.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Target Agent
            </label>
            <select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Select Agent...</option>
              {agents.map(agent => (
                <option key={agent} value={agent}>Agent {agent}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Task Type
            </label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="">Select Task Type...</option>
              {taskTypes.map(type => (
                <option key={type} value={type}>{type.replace('_', ' ').toUpperCase()}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="low">Low</option>
              <option value="normal">Normal</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Timeout (seconds)
            </label>
            <input
              type="number"
              value={timeout}
              onChange={(e) => setTimeout(e.target.value)}
              placeholder="Optional"
              min="1"
              max="3600"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Task Parameters (JSON)
          </label>
          <textarea
            value={taskData}
            onChange={(e) => {
              setTaskData(e.target.value);
              validateTaskData(e.target.value);
            }}
            placeholder='{"algorithm": "gzip", "data": "sample"}'
            className={`w-full bg-slate-700 border rounded-lg px-3 py-2 text-white font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              validationError ? 'border-red-500' : 'border-slate-600'
            }`}
            rows={6}
          />
          {validationError && (
            <div className="text-red-400 text-sm mt-1">{validationError}</div>
          )}
          <div className="text-xs text-slate-400 mt-1">
            Enter task parameters as valid JSON. Use templates above for quick setup.
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting || !selectedAgent || !taskType || !!validationError}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              <span>Submitting Task...</span>
            </>
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Submit Task</span>
            </>
          )}
        </button>
      </form>

      {/* Task Result */}
      {result && (
        <div className="mt-6">
          <h4 className="text-md font-semibold mb-3 flex items-center space-x-2">
            {getStatusIcon(result.status)}
            <span>Task Result: {result.task_id.slice(-8)}</span>
          </h4>
          <div className={`rounded-lg p-4 border ${
            result.status === 'completed'
              ? 'bg-green-400/10 border-green-400/20'
              : 'bg-red-400/10 border-red-400/20'
          }`}>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Status:</span>
                <span className={`font-medium capitalize ${
                  result.status === 'completed' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {result.status}
                </span>
              </div>

              {result.agent_used && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Agent:</span>
                  <span className="text-slate-300">Agent {result.agent_used}</span>
                </div>
              )}

              {result.execution_time_seconds && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Execution Time:</span>
                  <span className="text-slate-300">{result.execution_time_seconds.toFixed(2)}s</span>
                </div>
              )}

              <div className="flex justify-between">
                <span className="text-slate-400">Timestamp:</span>
                <span className="text-slate-300">{new Date(result.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>

            {result.result && (
              <div className="mt-4">
                <div className="text-slate-400 text-sm mb-2">Result:</div>
                <pre className="text-sm text-slate-300 whitespace-pre-wrap overflow-x-auto bg-slate-900/50 p-2 rounded border border-slate-600/30">
                  {JSON.stringify(result.result, null, 2)}
                </pre>
              </div>
            )}

            {result.error && (
              <div className="mt-4">
                <div className="text-red-400 text-sm mb-2">Error:</div>
                <div className="text-red-300 bg-red-400/10 p-2 rounded border border-red-400/20">
                  {result.error}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TaskSubmissionForm;
