'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import {
    Download,
    Eye,
    Pause,
    Play,
    Plus,
    RefreshCw,
    Trash2
} from 'lucide-react';
import React, { useEffect, useState } from 'react';

// Types
interface OptimizationStrategy {
  id: string;
  name: string;
  description: string;
  strategy_type: 'genetic' | 'gradient' | 'bayesian' | 'reinforcement' | 'hybrid';
  parameters: Record<string, any>;
  performance_metrics: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface OptimizationRun {
  id: string;
  strategy_id: string;
  prompt_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  current_iteration: number;
  total_iterations: number;
  best_score: number;
  parameters: Record<string, any>;
  results: OptimizationResult[];
  started_at: string;
  completed_at?: string;
  error_message?: string;
}

interface OptimizationResult {
  iteration: number;
  score: number;
  parameters: Record<string, any>;
  prompt_variant: string;
  evaluation_metrics: Record<string, number>;
  timestamp: string;
}

interface MetaLearningSession {
  id: string;
  name: string;
  description: string;
  learning_objective: string;
  training_data: any[];
  model_type: 'neural_network' | 'decision_tree' | 'ensemble' | 'transformer';
  hyperparameters: Record<string, any>;
  performance_history: PerformanceHistory[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface PerformanceHistory {
  epoch: number;
  loss: number;
  accuracy: number;
  validation_score: number;
  timestamp: string;
}

interface OptimizationConfig {
  id: string;
  name: string;
  description: string;
  optimization_type: 'prompt' | 'parameter' | 'workflow' | 'chain';
  target_metrics: string[];
  constraints: Record<string, any>;
  budget: number;
  time_limit: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface OptimizationMetrics {
  total_runs: number;
  successful_runs: number;
  average_improvement: number;
  best_score: number;
  total_cost: number;
  average_duration: number;
  success_rate: number;
  cost_efficiency: number;
}

const OptimizationManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState('strategies');
  const [strategies, setStrategies] = useState<OptimizationStrategy[]>([]);
  const [runs, setRuns] = useState<OptimizationRun[]>([]);
  const [sessions, setSessions] = useState<MetaLearningSession[]>([]);
  const [configs, setConfigs] = useState<OptimizationConfig[]>([]);
  const [metrics, setMetrics] = useState<OptimizationMetrics | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<OptimizationStrategy | null>(null);
  const [selectedRun, setSelectedRun] = useState<OptimizationRun | null>(null);
  const [selectedSession, setSelectedSession] = useState<MetaLearningSession | null>(null);
  const [selectedConfig, setSelectedConfig] = useState<OptimizationConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [showCreateStrategy, setShowCreateStrategy] = useState(false);
  const [showCreateSession, setShowCreateSession] = useState(false);
  const [showCreateConfig, setShowCreateConfig] = useState(false);
  const [showRunOptimization, setShowRunOptimization] = useState(false);

  // Fetch data
  const fetchStrategies = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/optimization/strategies');
      if (response.ok) {
        const data = await response.json();
        setStrategies(Array.isArray(data) ? data : []);
      } else {
        console.warn('Strategies API endpoint not available, using empty array');
        setStrategies([]);
      }
    } catch (error) {
      console.error('Error fetching strategies:', error);
      setStrategies([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/optimization/runs');
      if (response.ok) {
        const data = await response.json();
        setRuns(Array.isArray(data) ? data : []);
      } else {
        console.warn('Runs API endpoint not available, using empty array');
        setRuns([]);
      }
    } catch (error) {
      console.error('Error fetching runs:', error);
      setRuns([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/optimization/sessions');
      if (response.ok) {
        const data = await response.json();
        // Ensure data is always an array
        setSessions(Array.isArray(data) ? data : []);
      } else {
        console.warn('Sessions API endpoint not available, using empty array');
        setSessions([]);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
      setSessions([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/optimization/configs');
      if (response.ok) {
        const data = await response.json();
        setConfigs(Array.isArray(data) ? data : []);
      } else {
        console.warn('Configs API endpoint not available, using empty array');
        setConfigs([]);
      }
    } catch (error) {
      console.error('Error fetching configs:', error);
      setConfigs([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/optimization/metrics');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      } else {
        console.warn('Metrics API endpoint not available, using null');
        setMetrics(null);
      }
    } catch (error) {
      console.error('Error fetching metrics:', error);
      setMetrics(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStrategies();
    fetchRuns();
    fetchSessions();
    fetchConfigs();
    fetchMetrics();
  }, []);

  // Handlers
  const handleCreateStrategy = async (strategyData: Partial<OptimizationStrategy>) => {
    try {
      const response = await fetch('/api/optimization/strategies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(strategyData)
      });
      if (response.ok) {
        fetchStrategies();
        setShowCreateStrategy(false);
      }
    } catch (error) {
      console.error('Error creating strategy:', error);
    }
  };

  const handleCreateSession = async (sessionData: Partial<MetaLearningSession>) => {
    try {
      const response = await fetch('/api/optimization/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sessionData)
      });
      if (response.ok) {
        fetchSessions();
        setShowCreateSession(false);
      }
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const handleCreateConfig = async (configData: Partial<OptimizationConfig>) => {
    try {
      const response = await fetch('/api/optimization/configs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configData)
      });
      if (response.ok) {
        fetchConfigs();
        setShowCreateConfig(false);
      }
    } catch (error) {
      console.error('Error creating config:', error);
    }
  };

  const handleRunOptimization = async (runData: Partial<OptimizationRun>) => {
    try {
      const response = await fetch('/api/optimization/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(runData)
      });
      if (response.ok) {
        fetchRuns();
        setShowRunOptimization(false);
      }
    } catch (error) {
      console.error('Error running optimization:', error);
    }
  };

  const handleStopRun = async (runId: string) => {
    try {
      const response = await fetch(`/api/optimization/runs/${runId}/stop`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchRuns();
      }
    } catch (error) {
      console.error('Error stopping run:', error);
    }
  };

  const handleDeleteStrategy = async (strategyId: string) => {
    try {
      const response = await fetch(`/api/optimization/strategies/${strategyId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchStrategies();
      }
    } catch (error) {
      console.error('Error deleting strategy:', error);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`/api/optimization/sessions/${sessionId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchSessions();
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const handleDeleteConfig = async (configId: string) => {
    try {
      const response = await fetch(`/api/optimization/configs/${configId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchConfigs();
      }
    } catch (error) {
      console.error('Error deleting config:', error);
    }
  };

  const handleViewStrategy = (strategy: OptimizationStrategy) => {
    setSelectedStrategy(strategy);
  };

  const handleViewRun = (run: OptimizationRun) => {
    setSelectedRun(run);
  };

  const handleViewSession = (session: MetaLearningSession) => {
    setSelectedSession(session);
  };

  const handleViewConfig = (config: OptimizationConfig) => {
    setSelectedConfig(config);
  };

  const handleExportData = async (type: string) => {
    try {
      const response = await fetch(`/api/optimization/export/${type}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${type}_export.json`;
      a.click();
    } catch (error) {
      console.error('Error exporting data:', error);
    }
  };

  const handleRefresh = () => {
    fetchStrategies();
    fetchRuns();
    fetchSessions();
    fetchConfigs();
    fetchMetrics();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Optimization Management</h2>
          <p className="text-muted-foreground">
            AI-powered optimization with meta-learning and self-iterative design
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleRefresh} disabled={loading}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={() => setShowCreateStrategy(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Strategy
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="strategies">Strategies</TabsTrigger>
          <TabsTrigger value="runs">Runs</TabsTrigger>
          <TabsTrigger value="sessions">Meta-Learning</TabsTrigger>
          <TabsTrigger value="configs">Configs</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="strategies" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {strategies.map((strategy) => (
              <Card key={strategy.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{strategy.name}</CardTitle>
                    <Badge variant={strategy.is_active ? "default" : "secondary"}>
                      {strategy.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{strategy.description}</p>
                  <div className="flex items-center space-x-2 mb-3">
                    <Badge variant="outline">{strategy.strategy_type}</Badge>
                    <Badge variant="outline">{strategy.performance_metrics.length} metrics</Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" onClick={() => handleViewStrategy(strategy)}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setShowRunOptimization(true)}>
                      <Play className="h-4 w-4 mr-1" />
                      Run
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteStrategy(strategy.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="runs" className="space-y-4">
          <div className="space-y-4">
            {runs.map((run) => (
              <Card key={run.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Run #{run.id.slice(-8)}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge variant={
                        run.status === 'completed' ? 'default' :
                        run.status === 'running' ? 'secondary' :
                        run.status === 'failed' ? 'destructive' : 'outline'
                      }>
                        {run.status}
                      </Badge>
                      {run.status === 'running' && (
                        <Button size="sm" variant="outline" onClick={() => handleStopRun(run.id)}>
                          <Pause className="h-4 w-4 mr-1" />
                          Stop
                        </Button>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Progress</span>
                      <span className="text-sm text-muted-foreground">
                        {run.current_iteration}/{run.total_iterations}
                      </span>
                    </div>
                    <Progress value={run.progress} className="w-full" />
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Best Score:</span>
                        <span className="ml-2">{run.best_score.toFixed(4)}</span>
                      </div>
                      <div>
                        <span className="font-medium">Iteration:</span>
                        <span className="ml-2">{run.current_iteration}</span>
                      </div>
                      <div>
                        <span className="font-medium">Started:</span>
                        <span className="ml-2">{new Date(run.started_at).toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="font-medium">Duration:</span>
                        <span className="ml-2">
                          {run.completed_at ? 
                            `${Math.round((new Date(run.completed_at).getTime() - new Date(run.started_at).getTime()) / 1000)}s` :
                            'Running...'
                          }
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button size="sm" onClick={() => handleViewRun(run)}>
                        <Eye className="h-4 w-4 mr-1" />
                        View Details
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => handleExportData(`run_${run.id}`)}>
                        <Download className="h-4 w-4 mr-1" />
                        Export
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="sessions" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sessions.map((session) => (
              <Card key={session.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{session.name}</CardTitle>
                    <Badge variant={session.is_active ? "default" : "secondary"}>
                      {session.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{session.description}</p>
                  <div className="flex items-center space-x-2 mb-3">
                    <Badge variant="outline">{session.model_type}</Badge>
                    <Badge variant="outline">{session.training_data.length} samples</Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" onClick={() => handleViewSession(session)}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteSession(session.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="configs" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {configs.map((config) => (
              <Card key={config.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{config.name}</CardTitle>
                    <Badge variant={config.is_active ? "default" : "secondary"}>
                      {config.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{config.description}</p>
                  <div className="flex items-center space-x-2 mb-3">
                    <Badge variant="outline">{config.optimization_type}</Badge>
                    <Badge variant="outline">{config.target_metrics.length} metrics</Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" onClick={() => handleViewConfig(config)}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteConfig(config.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          {metrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Total Runs</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.total_runs}</div>
                  <p className="text-xs text-muted-foreground">
                    {metrics.successful_runs} successful
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{(metrics.success_rate * 100).toFixed(1)}%</div>
                  <p className="text-xs text-muted-foreground">
                    {metrics.successful_runs}/{metrics.total_runs} runs
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Best Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.best_score.toFixed(4)}</div>
                  <p className="text-xs text-muted-foreground">
                    {metrics.average_improvement > 0 ? '+' : ''}{metrics.average_improvement.toFixed(2)}% improvement
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">${metrics.total_cost.toFixed(2)}</div>
                  <p className="text-xs text-muted-foreground">
                    ${metrics.cost_efficiency.toFixed(2)} per run
                  </p>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Modals */}
      <Dialog open={showCreateStrategy} onOpenChange={setShowCreateStrategy}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Optimization Strategy</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="strategy-name">Name</Label>
              <Input id="strategy-name" placeholder="Enter strategy name" />
            </div>
            <div>
              <Label htmlFor="strategy-description">Description</Label>
              <Textarea id="strategy-description" placeholder="Enter strategy description" />
            </div>
            <div>
              <Label htmlFor="strategy-type">Strategy Type</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select strategy type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="genetic">Genetic Algorithm</SelectItem>
                  <SelectItem value="gradient">Gradient Descent</SelectItem>
                  <SelectItem value="bayesian">Bayesian Optimization</SelectItem>
                  <SelectItem value="reinforcement">Reinforcement Learning</SelectItem>
                  <SelectItem value="hybrid">Hybrid Approach</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateStrategy(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleCreateStrategy({})}>
                Create Strategy
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showCreateSession} onOpenChange={setShowCreateSession}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Meta-Learning Session</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="session-name">Name</Label>
              <Input id="session-name" placeholder="Enter session name" />
            </div>
            <div>
              <Label htmlFor="session-description">Description</Label>
              <Textarea id="session-description" placeholder="Enter session description" />
            </div>
            <div>
              <Label htmlFor="session-objective">Learning Objective</Label>
              <Textarea id="session-objective" placeholder="Enter learning objective" />
            </div>
            <div>
              <Label htmlFor="session-model">Model Type</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select model type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="neural_network">Neural Network</SelectItem>
                  <SelectItem value="decision_tree">Decision Tree</SelectItem>
                  <SelectItem value="ensemble">Ensemble</SelectItem>
                  <SelectItem value="transformer">Transformer</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateSession(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleCreateSession({})}>
                Create Session
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showCreateConfig} onOpenChange={setShowCreateConfig}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Optimization Config</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="config-name">Name</Label>
              <Input id="config-name" placeholder="Enter config name" />
            </div>
            <div>
              <Label htmlFor="config-description">Description</Label>
              <Textarea id="config-description" placeholder="Enter config description" />
            </div>
            <div>
              <Label htmlFor="config-type">Optimization Type</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select optimization type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="prompt">Prompt Optimization</SelectItem>
                  <SelectItem value="parameter">Parameter Optimization</SelectItem>
                  <SelectItem value="workflow">Workflow Optimization</SelectItem>
                  <SelectItem value="chain">Chain Optimization</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateConfig(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleCreateConfig({})}>
                Create Config
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showRunOptimization} onOpenChange={setShowRunOptimization}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Run Optimization</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="run-strategy">Strategy</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select strategy" />
                </SelectTrigger>
                <SelectContent>
                  {strategies.map((strategy) => (
                    <SelectItem key={strategy.id} value={strategy.id}>
                      {strategy.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="run-prompt">Prompt</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select prompt" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="prompt-1">Prompt 1</SelectItem>
                  <SelectItem value="prompt-2">Prompt 2</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="run-iterations">Iterations</Label>
              <Input id="run-iterations" type="number" placeholder="Enter number of iterations" />
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowRunOptimization(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleRunOptimization({})}>
                Start Optimization
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default OptimizationManagement;
