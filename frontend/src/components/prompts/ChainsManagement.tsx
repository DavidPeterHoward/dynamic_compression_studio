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
interface PromptChain {
  id: string;
  name: string;
  description: string;
  chain_type: 'sequential' | 'parallel' | 'conditional' | 'iterative' | 'recursive';
  steps: ChainStep[];
  execution_strategy: 'linear' | 'parallel' | 'adaptive' | 'dynamic';
  success_criteria: SuccessCriteria;
  failure_handling: FailureHandling;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ChainStep {
  id: string;
  step_number: number;
  prompt_id: string;
  step_type: 'prompt' | 'condition' | 'loop' | 'merge' | 'split';
  parameters: Record<string, any>;
  dependencies: string[];
  timeout: number;
  retry_count: number;
  success_condition: string;
  failure_action: 'continue' | 'stop' | 'retry' | 'fallback';
  fallback_prompt_id?: string;
  metadata: Record<string, any>;
}

interface SuccessCriteria {
  min_success_rate: number;
  max_failure_rate: number;
  quality_threshold: number;
  performance_metrics: string[];
  evaluation_method: 'automatic' | 'manual' | 'hybrid';
}

interface FailureHandling {
  max_retries: number;
  retry_delay: number;
  fallback_chain_id?: string;
  error_notification: boolean;
  rollback_strategy: 'none' | 'partial' | 'full';
}

interface ChainExecution {
  id: string;
  chain_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  current_step: number;
  total_steps: number;
  started_at: string;
  completed_at?: string;
  results: ExecutionResult[];
  error_message?: string;
  execution_metrics: ExecutionMetrics;
}

interface ExecutionResult {
  step_id: string;
  step_number: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  input: any;
  output: any;
  execution_time: number;
  cost: number;
  quality_score: number;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

interface ExecutionMetrics {
  total_execution_time: number;
  total_cost: number;
  average_quality_score: number;
  success_rate: number;
  failure_rate: number;
  retry_count: number;
  fallback_count: number;
}

interface ChainTemplate {
  id: string;
  name: string;
  description: string;
  template_type: 'basic' | 'advanced' | 'custom';
  chain_structure: any;
  parameters: Record<string, any>;
  usage_count: number;
  success_rate: number;
  created_at: string;
  updated_at: string;
}

interface ChainTest {
  id: string;
  chain_id: string;
  test_name: string;
  test_type: 'unit' | 'integration' | 'performance' | 'stress';
  test_data: any;
  expected_results: any;
  test_results: TestResults;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

interface TestResults {
  passed: boolean;
  execution_time: number;
  quality_score: number;
  error_count: number;
  warnings: string[];
  detailed_results: any;
}

const ChainsManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chains');
  const [chains, setChains] = useState<PromptChain[]>([]);
  const [executions, setExecutions] = useState<ChainExecution[]>([]);
  const [templates, setTemplates] = useState<ChainTemplate[]>([]);
  const [tests, setTests] = useState<ChainTest[]>([]);
  const [selectedChain, setSelectedChain] = useState<PromptChain | null>(null);
  const [selectedExecution, setSelectedExecution] = useState<ChainExecution | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<ChainTemplate | null>(null);
  const [selectedTest, setSelectedTest] = useState<ChainTest | null>(null);
  const [loading, setLoading] = useState(false);
  const [showCreateChain, setShowCreateChain] = useState(false);
  const [showCreateTemplate, setShowCreateTemplate] = useState(false);
  const [showCreateTest, setShowCreateTest] = useState(false);
  const [showRunChain, setShowRunChain] = useState(false);

  // Fetch data
  const fetchChains = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/chains');
      const data = await response.json();
      setChains(data);
    } catch (error) {
      console.error('Error fetching chains:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExecutions = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/chains/executions');
      const data = await response.json();
      setExecutions(data);
    } catch (error) {
      console.error('Error fetching executions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/chains/templates');
      const data = await response.json();
      setTemplates(data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTests = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/chains/tests');
      const data = await response.json();
      setTests(data);
    } catch (error) {
      console.error('Error fetching tests:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChains();
    fetchExecutions();
    fetchTemplates();
    fetchTests();
  }, []);

  // Handlers
  const handleCreateChain = async (chainData: Partial<PromptChain>) => {
    try {
      const response = await fetch('/api/chains', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chainData)
      });
      if (response.ok) {
        fetchChains();
        setShowCreateChain(false);
      }
    } catch (error) {
      console.error('Error creating chain:', error);
    }
  };

  const handleCreateTemplate = async (templateData: Partial<ChainTemplate>) => {
    try {
      const response = await fetch('/api/chains/templates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(templateData)
      });
      if (response.ok) {
        fetchTemplates();
        setShowCreateTemplate(false);
      }
    } catch (error) {
      console.error('Error creating template:', error);
    }
  };

  const handleCreateTest = async (testData: Partial<ChainTest>) => {
    try {
      const response = await fetch('/api/chains/tests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testData)
      });
      if (response.ok) {
        fetchTests();
        setShowCreateTest(false);
      }
    } catch (error) {
      console.error('Error creating test:', error);
    }
  };

  const handleRunChain = async (executionData: Partial<ChainExecution>) => {
    try {
      const response = await fetch('/api/chains/executions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(executionData)
      });
      if (response.ok) {
        fetchExecutions();
        setShowRunChain(false);
      }
    } catch (error) {
      console.error('Error running chain:', error);
    }
  };

  const handleStopExecution = async (executionId: string) => {
    try {
      const response = await fetch(`/api/chains/executions/${executionId}/stop`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchExecutions();
      }
    } catch (error) {
      console.error('Error stopping execution:', error);
    }
  };

  const handleDeleteChain = async (chainId: string) => {
    try {
      const response = await fetch(`/api/chains/${chainId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchChains();
      }
    } catch (error) {
      console.error('Error deleting chain:', error);
    }
  };

  const handleDeleteTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`/api/chains/templates/${templateId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchTemplates();
      }
    } catch (error) {
      console.error('Error deleting template:', error);
    }
  };

  const handleDeleteTest = async (testId: string) => {
    try {
      const response = await fetch(`/api/chains/tests/${testId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        fetchTests();
      }
    } catch (error) {
      console.error('Error deleting test:', error);
    }
  };

  const handleViewChain = (chain: PromptChain) => {
    setSelectedChain(chain);
  };

  const handleViewExecution = (execution: ChainExecution) => {
    setSelectedExecution(execution);
  };

  const handleViewTemplate = (template: ChainTemplate) => {
    setSelectedTemplate(template);
  };

  const handleViewTest = (test: ChainTest) => {
    setSelectedTest(test);
  };

  const handleExportData = async (type: string) => {
    try {
      const response = await fetch(`/api/chains/export/${type}`);
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
    fetchChains();
    fetchExecutions();
    fetchTemplates();
    fetchTests();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Chains Management</h2>
          <p className="text-muted-foreground">
            Complex prompt chains with execution strategies and testing
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleRefresh} disabled={loading}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={() => setShowCreateChain(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Chain
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="chains">Chains</TabsTrigger>
          <TabsTrigger value="executions">Executions</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="tests">Tests</TabsTrigger>
        </TabsList>

        <TabsContent value="chains" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {chains.map((chain) => (
              <Card key={chain.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{chain.name}</CardTitle>
                    <Badge variant={chain.is_active ? "default" : "secondary"}>
                      {chain.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{chain.description}</p>
                  <div className="flex items-center space-x-2 mb-3">
                    <Badge variant="outline">{chain.chain_type}</Badge>
                    <Badge variant="outline">{chain.steps.length} steps</Badge>
                    <Badge variant="outline">{chain.execution_strategy}</Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" onClick={() => handleViewChain(chain)}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setShowRunChain(true)}>
                      <Play className="h-4 w-4 mr-1" />
                      Run
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteChain(chain.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="executions" className="space-y-4">
          <div className="space-y-4">
            {executions.map((execution) => (
              <Card key={execution.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Execution #{execution.id.slice(-8)}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge variant={
                        execution.status === 'completed' ? 'default' :
                        execution.status === 'running' ? 'secondary' :
                        execution.status === 'failed' ? 'destructive' : 'outline'
                      }>
                        {execution.status}
                      </Badge>
                      {execution.status === 'running' && (
                        <Button size="sm" variant="outline" onClick={() => handleStopExecution(execution.id)}>
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
                        {execution.current_step}/{execution.total_steps}
                      </span>
                    </div>
                    <Progress value={execution.progress} className="w-full" />
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Quality Score:</span>
                        <span className="ml-2">{execution.execution_metrics.average_quality_score.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="font-medium">Success Rate:</span>
                        <span className="ml-2">{(execution.execution_metrics.success_rate * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="font-medium">Started:</span>
                        <span className="ml-2">{new Date(execution.started_at).toLocaleString()}</span>
                      </div>
                      <div>
                        <span className="font-medium">Duration:</span>
                        <span className="ml-2">
                          {execution.completed_at ? 
                            `${Math.round((new Date(execution.completed_at).getTime() - new Date(execution.started_at).getTime()) / 1000)}s` :
                            'Running...'
                          }
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button size="sm" onClick={() => handleViewExecution(execution)}>
                        <Eye className="h-4 w-4 mr-1" />
                        View Details
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => handleExportData(`execution_${execution.id}`)}>
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

        <TabsContent value="templates" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <Card key={template.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{template.name}</CardTitle>
                    <Badge variant="outline">{template.template_type}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{template.description}</p>
                  <div className="flex items-center space-x-2 mb-3">
                    <Badge variant="outline">{template.usage_count} uses</Badge>
                    <Badge variant="outline">{(template.success_rate * 100).toFixed(1)}% success</Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" onClick={() => handleViewTemplate(template)}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteTemplate(template.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="tests" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tests.map((test) => (
              <Card key={test.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{test.test_name}</CardTitle>
                    <Badge variant={
                      test.status === 'completed' ? 'default' :
                      test.status === 'running' ? 'secondary' :
                      test.status === 'failed' ? 'destructive' : 'outline'
                    }>
                      {test.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">{test.test_type} test</p>
                  <div className="flex items-center space-x-2 mb-3">
                    <Badge variant={test.test_results.passed ? "default" : "destructive"}>
                      {test.test_results.passed ? "Passed" : "Failed"}
                    </Badge>
                    <Badge variant="outline">{test.test_results.execution_time}ms</Badge>
                    <Badge variant="outline">{test.test_results.quality_score.toFixed(2)} quality</Badge>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button size="sm" onClick={() => handleViewTest(test)}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => handleDeleteTest(test.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Modals */}
      <Dialog open={showCreateChain} onOpenChange={setShowCreateChain}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Prompt Chain</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="chain-name">Name</Label>
              <Input id="chain-name" placeholder="Enter chain name" />
            </div>
            <div>
              <Label htmlFor="chain-description">Description</Label>
              <Textarea id="chain-description" placeholder="Enter chain description" />
            </div>
            <div>
              <Label htmlFor="chain-type">Chain Type</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select chain type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sequential">Sequential</SelectItem>
                  <SelectItem value="parallel">Parallel</SelectItem>
                  <SelectItem value="conditional">Conditional</SelectItem>
                  <SelectItem value="iterative">Iterative</SelectItem>
                  <SelectItem value="recursive">Recursive</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="execution-strategy">Execution Strategy</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select execution strategy" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="linear">Linear</SelectItem>
                  <SelectItem value="parallel">Parallel</SelectItem>
                  <SelectItem value="adaptive">Adaptive</SelectItem>
                  <SelectItem value="dynamic">Dynamic</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateChain(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleCreateChain({})}>
                Create Chain
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showCreateTemplate} onOpenChange={setShowCreateTemplate}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Chain Template</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="template-name">Name</Label>
              <Input id="template-name" placeholder="Enter template name" />
            </div>
            <div>
              <Label htmlFor="template-description">Description</Label>
              <Textarea id="template-description" placeholder="Enter template description" />
            </div>
            <div>
              <Label htmlFor="template-type">Template Type</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select template type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="basic">Basic</SelectItem>
                  <SelectItem value="advanced">Advanced</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateTemplate(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleCreateTemplate({})}>
                Create Template
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showCreateTest} onOpenChange={setShowCreateTest}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Chain Test</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="test-name">Test Name</Label>
              <Input id="test-name" placeholder="Enter test name" />
            </div>
            <div>
              <Label htmlFor="test-type">Test Type</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select test type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="unit">Unit Test</SelectItem>
                  <SelectItem value="integration">Integration Test</SelectItem>
                  <SelectItem value="performance">Performance Test</SelectItem>
                  <SelectItem value="stress">Stress Test</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="test-chain">Chain</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select chain" />
                </SelectTrigger>
                <SelectContent>
                  {chains.map((chain) => (
                    <SelectItem key={chain.id} value={chain.id}>
                      {chain.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowCreateTest(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleCreateTest({})}>
                Create Test
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showRunChain} onOpenChange={setShowRunChain}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Run Chain</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="run-chain">Chain</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select chain" />
                </SelectTrigger>
                <SelectContent>
                  {chains.map((chain) => (
                    <SelectItem key={chain.id} value={chain.id}>
                      {chain.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="run-input">Input Data</Label>
              <Textarea id="run-input" placeholder="Enter input data (JSON format)" />
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowRunChain(false)}>
                Cancel
              </Button>
              <Button onClick={() => handleRunChain({})}>
                Start Execution
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ChainsManagement;
