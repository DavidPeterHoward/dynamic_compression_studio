import { Activity, Brain, Cpu, Database, Users, Wifi, WifiOff, Zap } from 'lucide-react';
import React, { useEffect, useState } from 'react';

interface AgentStatus {
  agent_id: string;
  agent_type: string;
  status: string;
  capabilities: string[];
  task_count: number;
  success_count: number;
  error_count: number;
  success_rate: number;
  avg_task_duration?: number;
  created_at: string;
  last_active_at?: string;
  uptime_seconds?: number;
}

interface SystemStatus {
  system_status: string;
  agents: Record<string, AgentStatus>;
  api_metrics: {
    total_requests: number;
    websocket_connections: number;
  };
  timestamp: string;
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

const AgentStatusDashboard: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [recentTasks, setRecentTasks] = useState<TaskResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Connect to native WebSocket (not Socket.io)
    const wsUrl = process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000';
    const socketInstance = new WebSocket(`${wsUrl}/ws/agent-updates`);

    socketInstance.onopen = () => {
      setIsConnected(true);
      console.log('Connected to agent updates');
    };

    socketInstance.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from agent updates');
    };

    socketInstance.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.event_type === 'system_status') {
          setSystemStatus(message.data as SystemStatus);
          setIsLoading(false);
        } else if (message.event_type === 'status_update') {
          setSystemStatus(message.data as SystemStatus);
        } else if (message.event_type === 'task_completed') {
          console.log('Task completed:', message.data);
          setRecentTasks(prev => [message.data as TaskResult, ...prev.slice(0, 9)]);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    socketInstance.onerror = (error) => {
      console.error('WebSocket connection error:', error);
      setIsConnected(false);
      setIsLoading(false);
    };

    setSocket(socketInstance);

    // Fetch initial status via HTTP
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/system/status`)
      .then(res => res.json())
      .then(data => {
        setSystemStatus(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching initial status:', error);
        setIsLoading(false);
      });

    return () => {
      if (socketInstance.readyState === WebSocket.OPEN) {
        socketInstance.close();
      }
    };
  }, []);

  const getAgentIcon = (agentType: string) => {
    switch (agentType) {
      case 'infrastructure':
        return <Activity className="w-6 h-6" />;
      case 'database':
        return <Database className="w-6 h-6" />;
      case 'core_engine':
        return <Cpu className="w-6 h-6" />;
      case 'meta_learner':
        return <Brain className="w-6 h-6" />;
      case 'api_layer':
        return <Zap className="w-6 h-6" />;
      default:
        return <Zap className="w-6 h-6" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
      case 'idle':
      case 'running':
        return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'working':
      case 'busy':
        return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'error':
      case 'failed':
        return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'initializing':
        return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      default:
        return 'text-gray-400 bg-gray-400/10 border-gray-400/20';
    }
  };

  const formatUptime = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white p-6">
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-slate-400">Connecting to Meta-Recursive Multi-Agent System...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Meta-Recursive Multi-Agent System
            </h1>
            <p className="text-slate-400 mt-2">
              Real-time agent orchestration and monitoring dashboard
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg border ${
              isConnected ? 'bg-green-400/10 text-green-400 border-green-400/20' : 'bg-red-400/10 text-red-400 border-red-400/20'
            }`}>
              {isConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              <span className="text-sm font-medium">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            <div className="bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-600/50">
              <div className="text-sm text-slate-400">System Status</div>
              <div className={`text-lg font-semibold capitalize ${
                systemStatus?.system_status === 'operational' ? 'text-green-400' : 'text-yellow-400'
              }`}>
                {systemStatus?.system_status || 'Unknown'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-600/50">
          <div className="flex items-center space-x-3 mb-4">
            <Users className="w-8 h-8 text-blue-400" />
            <div>
              <div className="text-sm text-slate-400">Active Agents</div>
              <div className="text-2xl font-bold">{Object.keys(systemStatus?.agents || {}).length}</div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-600/50">
          <div className="flex items-center space-x-3 mb-4">
            <Activity className="w-8 h-8 text-green-400" />
            <div>
              <div className="text-sm text-slate-400">API Requests</div>
              <div className="text-2xl font-bold">{systemStatus?.api_metrics?.total_requests || 0}</div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-600/50">
          <div className="flex items-center space-x-3 mb-4">
            <Zap className="w-8 h-8 text-purple-400" />
            <div>
              <div className="text-sm text-slate-400">WebSocket Clients</div>
              <div className="text-2xl font-bold">{systemStatus?.api_metrics?.websocket_connections || 0}</div>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-600/50">
          <div className="flex items-center space-x-3 mb-4">
            <Brain className="w-8 h-8 text-orange-400" />
            <div>
              <div className="text-sm text-slate-400">Recent Tasks</div>
              <div className="text-2xl font-bold">{recentTasks.length}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {systemStatus && Object.entries(systemStatus.agents).map(([agentId, agent]) => (
          <div key={agentId} className="bg-slate-800/50 rounded-lg p-6 border border-slate-600/50 hover:bg-slate-800/70 transition-colors">
            <div className="flex items-center space-x-3 mb-4">
              {getAgentIcon(agent.agent_type)}
              <div>
                <div className="font-semibold">Agent {agentId}</div>
                <div className="text-sm text-slate-400 capitalize">{agent.agent_type.replace('_', ' ')}</div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Status</span>
                <span className={`px-2 py-1 rounded text-xs font-medium capitalize ${getStatusColor(agent.status)}`}>
                  {agent.status}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Capabilities</span>
                <span className="text-sm font-medium">{agent.capabilities?.length || 0}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Uptime</span>
                <span className="text-sm font-medium">{formatUptime(agent.uptime_seconds)}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Tasks</span>
                <span className="text-sm font-medium">{agent.task_count || 0}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Success Rate</span>
                <span className="text-sm font-medium">{((agent.success_rate || 0) * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Tasks */}
      {recentTasks.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-600/50">
          <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
            <Activity className="w-5 h-5" />
            <span>Recent Task Executions</span>
          </h3>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {recentTasks.map((task, index) => (
              <div key={`${task.task_id}-${index}`} className="bg-slate-900/50 rounded-lg p-4 border border-slate-600/30">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-mono text-slate-400">Task {task.task_id.slice(-8)}</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium capitalize ${
                      task.status === 'completed' ? 'bg-green-400/10 text-green-400' : 'bg-red-400/10 text-red-400'
                    }`}>
                      {task.status}
                    </span>
                  </div>
                  <span className="text-xs text-slate-500">{formatTimestamp(task.timestamp)}</span>
                </div>

                {task.agent_used && (
                  <div className="text-sm text-slate-400 mb-2">
                    Executed by: Agent {task.agent_used}
                  </div>
                )}

                {task.execution_time_seconds && (
                  <div className="text-sm text-slate-400">
                    Execution time: {task.execution_time_seconds.toFixed(2)}s
                  </div>
                )}

                {task.error && (
                  <div className="text-sm text-red-400 mt-2 p-2 bg-red-400/10 rounded border border-red-400/20">
                    Error: {task.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Real-time Updates Indicator */}
      <div className="mt-8 text-center">
        <div className="inline-flex items-center space-x-2 text-slate-400">
          <div className={`w-2 h-2 rounded-full animate-pulse ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
          <span className="text-sm">
            {isConnected ? 'Real-time updates active' : 'Connection lost - attempting to reconnect...'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AgentStatusDashboard;
