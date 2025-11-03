'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    AlertTriangle,
    BarChart3,
    Brain,
    CheckCircle,
    Eye,
    Loader2,
    Network,
    Play,
    TestTube,
    Zap
} from 'lucide-react'
import { useState } from 'react'

interface ProtocolConfig {
  name: string
  type: 'http' | 'https' | 'websocket' | 'grpc' | 'tcp' | 'udp' | 'quic'
  transport: 'tcp' | 'udp' | 'quic'
  application: 'http1.1' | 'http2' | 'http3' | 'websocket' | 'grpc'
  delivery: 'streaming' | 'batch' | 'real_time' | 'cached'
  compression: string[]
  optimization: string[]
  limitations: string[]
  enabled: boolean
}

interface NetworkConditions {
  bandwidth: 'low' | 'medium' | 'high' | 'variable'
  latency: 'low' | 'medium' | 'high'
  packetLoss: 'low' | 'medium' | 'high'
  congestion: 'none' | 'light' | 'moderate' | 'heavy'
  jitter: number
  mtu: number
}

interface ProtocolTest {
  id: string
  protocol: string
  status: 'running' | 'completed' | 'failed' | 'queued'
  progress: number
  results: {
    compressionRatio: number
    throughput: number
    latency: number
    errorRate: number
    efficiency: number
    adaptation: number
  }
  networkConditions: NetworkConditions
  contentSize: number
  contentType: string
  timestamp: Date
}

interface LLMConfig {
  model: string
  temperature: number
  maxTokens: number
  symbolicLookup: boolean
  decompressionFunction: boolean
  chunkSize: number
  streaming: boolean
  batching: boolean
}

export default function ProtocolsTab() {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedProtocol, setSelectedProtocol] = useState<string>('http')
  const [networkConditions, setNetworkConditions] = useState<NetworkConditions>({
    bandwidth: 'medium',
    latency: 'medium',
    packetLoss: 'low',
    congestion: 'none',
    jitter: 5,
    mtu: 1500
  })
  const [llmConfig, setLlmConfig] = useState<LLMConfig>({
    model: 'gpt-4',
    temperature: 0.7,
    maxTokens: 2048,
    symbolicLookup: true,
    decompressionFunction: true,
    chunkSize: 1024,
    streaming: true,
    batching: true
  })
  const [runningTests, setRunningTests] = useState<ProtocolTest[]>([])
  const [testHistory, setTestHistory] = useState<ProtocolTest[]>([])
  const [isTesting, setIsTesting] = useState(false)

  const protocols: Record<string, ProtocolConfig> = {
    http: {
      name: 'HTTP/1.1',
      type: 'http',
      transport: 'tcp',
      application: 'http1.1',
      delivery: 'batch',
      compression: ['gzip', 'deflate', 'brotli'],
      optimization: ['header_compression', 'connection_reuse'],
      limitations: ['head_of_line_blocking', 'single_connection'],
      enabled: true
    },
    http2: {
      name: 'HTTP/2',
      type: 'http',
      transport: 'tcp',
      application: 'http2',
      delivery: 'streaming',
      compression: ['hpack', 'stream_compression'],
      optimization: ['multiplexing', 'server_push', 'header_compression'],
      limitations: ['tcp_dependency', 'head_of_line_blocking'],
      enabled: true
    },
    http3: {
      name: 'HTTP/3',
      type: 'http',
      transport: 'quic',
      application: 'http3',
      delivery: 'streaming',
      compression: ['qpack', 'stream_compression'],
      optimization: ['quic_multiplexing', '0_rtt', 'connection_migration'],
      limitations: ['complexity', 'deployment_challenges'],
      enabled: true
    },
    websocket: {
      name: 'WebSocket',
      type: 'websocket',
      transport: 'tcp',
      application: 'websocket',
      delivery: 'real_time',
      compression: ['permessage_deflate', 'custom_compression'],
      optimization: ['bidirectional_streaming', 'real_time_compression'],
      limitations: ['protocol_overhead', 'state_management'],
      enabled: true
    },
    grpc: {
      name: 'gRPC',
      type: 'grpc',
      transport: 'tcp',
      application: 'grpc',
      delivery: 'streaming',
      compression: ['gzip', 'deflate', 'custom_codecs'],
      optimization: ['streaming_rpc', 'bidirectional_streaming', 'header_compression'],
      limitations: ['http2_dependency', 'complexity'],
      enabled: true
    }
  }

  const startProtocolTest = async () => {
    const test: ProtocolTest = {
      id: Date.now().toString(),
      protocol: selectedProtocol,
      status: 'running',
      progress: 0,
      results: {
        compressionRatio: 0,
        throughput: 0,
        latency: 0,
        errorRate: 0,
        efficiency: 0,
        adaptation: 0
      },
      networkConditions,
      contentSize: 1024 * 1024, // 1MB
      contentType: 'mixed',
      timestamp: new Date()
    }

    setRunningTests(prev => [...prev, test])
    setIsTesting(true)

    // Simulate test progress
    const interval = setInterval(() => {
      setRunningTests(prev => prev.map(t => {
        if (t.id === test.id) {
          const newProgress = Math.min(t.progress + 10, 100)
          const isComplete = newProgress === 100
          
          if (isComplete) {
            // Generate realistic results
            const results = {
              compressionRatio: 2.5 + Math.random() * 2,
              throughput: 50 + Math.random() * 100,
              latency: 10 + Math.random() * 50,
              errorRate: Math.random() * 0.05,
              efficiency: 0.7 + Math.random() * 0.3,
              adaptation: 0.6 + Math.random() * 0.4
            }
            
            setTimeout(() => {
              setTestHistory(prev => [...prev, { ...t, status: 'completed', progress: 100, results }])
              setRunningTests(prev => prev.filter(rt => rt.id !== t.id))
            }, 1000)
            
            clearInterval(interval)
            setIsTesting(false)
          }
          
          return { ...t, progress: newProgress }
        }
        return t
      }))
    }, 500)
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Eye },
    { id: 'protocols', label: 'Protocols', icon: Network },
    { id: 'testing', label: 'Testing', icon: TestTube },
    { id: 'llm', label: 'LLM Integration', icon: Brain },
    { id: 'metrics', label: 'Metrics', icon: BarChart3 },
    { id: 'optimization', label: 'Optimization', icon: Zap }
  ]

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Protocol-Aware Optimization</h1>
            <p className="text-gray-600 mt-1">
              Multi-protocol support with transport layer understanding and network condition awareness
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Activity className="w-4 h-4" />
              <span>Meta-Learning Active</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-green-600">
              <CheckCircle className="w-4 h-4" />
              <span>Self-Optimizing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="p-6"
            >
              <ProtocolOverview protocols={protocols} />
            </motion.div>
          )}

          {activeTab === 'protocols' && (
            <motion.div
              key="protocols"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="p-6"
            >
              <ProtocolDetails 
                protocols={protocols}
                selectedProtocol={selectedProtocol}
                setSelectedProtocol={setSelectedProtocol}
              />
            </motion.div>
          )}

          {activeTab === 'testing' && (
            <motion.div
              key="testing"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="p-6"
            >
              <ProtocolTesting
                protocols={protocols}
                selectedProtocol={selectedProtocol}
                networkConditions={networkConditions}
                setNetworkConditions={setNetworkConditions}
                runningTests={runningTests}
                testHistory={testHistory}
                isTesting={isTesting}
                startProtocolTest={startProtocolTest}
              />
            </motion.div>
          )}

          {activeTab === 'llm' && (
            <motion.div
              key="llm"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="p-6"
            >
              <LLMIntegration
                llmConfig={llmConfig}
                setLlmConfig={setLlmConfig}
              />
            </motion.div>
          )}

          {activeTab === 'metrics' && (
            <motion.div
              key="metrics"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="p-6"
            >
              <ProtocolMetrics
                testHistory={testHistory}
                runningTests={runningTests}
              />
            </motion.div>
          )}

          {activeTab === 'optimization' && (
            <motion.div
              key="optimization"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="p-6"
            >
              <OptimizationPanel
                protocols={protocols}
                testHistory={testHistory}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

// Protocol Overview Component
function ProtocolOverview({ protocols }: { protocols: Record<string, ProtocolConfig> }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Supported Protocols</p>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(protocols).length}</p>
            </div>
            <Network className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Optimizations</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
            </div>
            <Zap className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Meta-Learning Score</p>
              <p className="text-2xl font-bold text-gray-900">94%</p>
            </div>
            <Brain className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Protocol Performance Summary</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {Object.entries(protocols).map(([key, protocol]) => (
              <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <div>
                    <h4 className="font-medium text-gray-900">{protocol.name}</h4>
                    <p className="text-sm text-gray-600">
                      {protocol.transport.toUpperCase()} • {protocol.application}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-6 text-sm">
                  <div>
                    <p className="text-gray-600">Compression</p>
                    <p className="font-medium">{protocol.compression.length} methods</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Optimizations</p>
                    <p className="font-medium">{protocol.optimization.length} features</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Status</p>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Active
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Protocol Details Component
function ProtocolDetails({ 
  protocols, 
  selectedProtocol, 
  setSelectedProtocol 
}: { 
  protocols: Record<string, ProtocolConfig>
  selectedProtocol: string
  setSelectedProtocol: (protocol: string) => void
}) {
  const protocol = protocols[selectedProtocol]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Protocol Configuration</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Protocol
              </label>
              <select
                value={selectedProtocol}
                onChange={(e) => setSelectedProtocol(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {Object.entries(protocols).map(([key, protocol]) => (
                  <option key={key} value={key}>{protocol.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Compression Methods</h4>
              <div className="space-y-2">
                {protocol.compression.map((method, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-gray-700">{method}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Optimization Features</h4>
              <div className="space-y-2">
                {protocol.optimization.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Zap className="w-4 h-4 text-blue-500" />
                    <span className="text-sm text-gray-700">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Known Limitations</h4>
              <div className="space-y-2">
                {protocol.limitations.map((limitation, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm text-gray-700">{limitation}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Protocol Testing Component
function ProtocolTesting({
  protocols,
  selectedProtocol,
  networkConditions,
  setNetworkConditions,
  runningTests,
  testHistory,
  isTesting,
  startProtocolTest
}: {
  protocols: Record<string, ProtocolConfig>
  selectedProtocol: string
  networkConditions: NetworkConditions
  setNetworkConditions: (conditions: NetworkConditions) => void
  runningTests: ProtocolTest[]
  testHistory: ProtocolTest[]
  isTesting: boolean
  startProtocolTest: () => void
}) {
  return (
    <div className="space-y-6">
      {/* Network Conditions Configuration */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Network Conditions</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bandwidth</label>
              <select
                value={networkConditions.bandwidth}
                onChange={(e) => setNetworkConditions({...networkConditions, bandwidth: e.target.value as any})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="variable">Variable</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Latency</label>
              <select
                value={networkConditions.latency}
                onChange={(e) => setNetworkConditions({...networkConditions, latency: e.target.value as any})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Packet Loss</label>
              <select
                value={networkConditions.packetLoss}
                onChange={(e) => setNetworkConditions({...networkConditions, packetLoss: e.target.value as any})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          
          <div className="mt-6 flex justify-center">
            <button
              onClick={startProtocolTest}
              disabled={isTesting}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isTesting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              <span>{isTesting ? 'Testing...' : 'Start Protocol Test'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Running Tests */}
      {runningTests.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Running Tests</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {runningTests.map((test) => (
                <div key={test.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">
                      {protocols[test.protocol]?.name} Test
                    </h4>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                      Running
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${test.progress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">{test.progress}% complete</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Test History */}
      {testHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Test History</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {testHistory.slice(-5).reverse().map((test) => (
                <div key={test.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-900">
                      {protocols[test.protocol]?.name} Test
                    </h4>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Completed
                    </span>
                  </div>
                  <div className="grid grid-cols-2 lg:grid-cols-6 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Compression Ratio</p>
                      <p className="font-medium">{test.results.compressionRatio.toFixed(2)}x</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Throughput</p>
                      <p className="font-medium">{test.results.throughput.toFixed(0)} MB/s</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Latency</p>
                      <p className="font-medium">{test.results.latency.toFixed(0)}ms</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Error Rate</p>
                      <p className="font-medium">{(test.results.errorRate * 100).toFixed(2)}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Efficiency</p>
                      <p className="font-medium">{(test.results.efficiency * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Adaptation</p>
                      <p className="font-medium">{(test.results.adaptation * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// LLM Integration Component
function LLMIntegration({
  llmConfig,
  setLlmConfig
}: {
  llmConfig: LLMConfig
  setLlmConfig: (config: LLMConfig) => void
}) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">LLM Configuration</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Model</label>
              <select
                value={llmConfig.model}
                onChange={(e) => setLlmConfig({...llmConfig, model: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="claude-3">Claude-3</option>
                <option value="llama-2">Llama-2</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Temperature</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={llmConfig.temperature}
                onChange={(e) => setLlmConfig({...llmConfig, temperature: parseFloat(e.target.value)})}
                className="w-full"
              />
              <p className="text-sm text-gray-600 mt-1">{llmConfig.temperature}</p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Max Tokens</label>
              <input
                type="number"
                value={llmConfig.maxTokens}
                onChange={(e) => setLlmConfig({...llmConfig, maxTokens: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Chunk Size</label>
              <input
                type="number"
                value={llmConfig.chunkSize}
                onChange={(e) => setLlmConfig({...llmConfig, chunkSize: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>

          <div className="mt-6 space-y-4">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={llmConfig.symbolicLookup}
                onChange={(e) => setLlmConfig({...llmConfig, symbolicLookup: e.target.checked})}
                className="rounded"
              />
              <label className="text-sm font-medium text-gray-700">Enable Symbolic Lookup</label>
            </div>
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={llmConfig.decompressionFunction}
                onChange={(e) => setLlmConfig({...llmConfig, decompressionFunction: e.target.checked})}
                className="rounded"
              />
              <label className="text-sm font-medium text-gray-700">Enable Decompression Function</label>
            </div>
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={llmConfig.streaming}
                onChange={(e) => setLlmConfig({...llmConfig, streaming: e.target.checked})}
                className="rounded"
              />
              <label className="text-sm font-medium text-gray-700">Enable Streaming</label>
            </div>
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={llmConfig.batching}
                onChange={(e) => setLlmConfig({...llmConfig, batching: e.target.checked})}
                className="rounded"
              />
              <label className="text-sm font-medium text-gray-700">Enable Batching</label>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Protocol Metrics Component
function ProtocolMetrics({
  testHistory,
  runningTests
}: {
  testHistory: ProtocolTest[]
  runningTests: ProtocolTest[]
}) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Tests</p>
              <p className="text-2xl font-bold text-gray-900">{testHistory.length}</p>
            </div>
            <TestTube className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running Tests</p>
              <p className="text-2xl font-bold text-gray-900">{runningTests.length}</p>
            </div>
            <Loader2 className="w-8 h-8 text-yellow-500 animate-spin" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Compression</p>
              <p className="text-2xl font-bold text-gray-900">
                {testHistory.length > 0 
                  ? (testHistory.reduce((sum, test) => sum + test.results.compressionRatio, 0) / testHistory.length).toFixed(1)
                  : '0.0'}x
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {testHistory.length > 0 
                  ? ((testHistory.filter(test => test.status === 'completed').length / testHistory.length) * 100).toFixed(0)
                  : '0'}%
              </p>
            </div>
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Performance Trends</h3>
        </div>
        <div className="p-6">
          <div className="h-64 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 mx-auto mb-2" />
              <p>Performance charts will be displayed here</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Optimization Panel Component
function OptimizationPanel({
  protocols,
  testHistory
}: {
  protocols: Record<string, ProtocolConfig>
  testHistory: ProtocolTest[]
}) {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Meta-Learning Optimization</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">Self-Learning</h4>
              <p className="text-sm text-blue-700">
                Continuously improving algorithms based on performance data and user feedback
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <h4 className="font-medium text-green-900 mb-2">Cross-Protocol Transfer</h4>
              <p className="text-sm text-green-700">
                Knowledge transfer between different protocols for optimal performance
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <h4 className="font-medium text-purple-900 mb-2">Adaptive Optimization</h4>
              <p className="text-sm text-purple-700">
                Dynamic parameter adjustment based on real-time network conditions
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Optimization Recommendations</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-3 p-4 bg-yellow-50 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              <div>
                <h4 className="font-medium text-yellow-900">HTTP/2 Optimization</h4>
                <p className="text-sm text-yellow-700">
                  Consider enabling server push for improved performance
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-4 bg-green-50 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <div>
                <h4 className="font-medium text-green-900">WebSocket Enhancement</h4>
                <p className="text-sm text-green-700">
                  Real-time compression is performing optimally
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg">
              <Brain className="w-5 h-5 text-blue-600" />
              <div>
                <h4 className="font-medium text-blue-900">Meta-Learning Suggestion</h4>
                <p className="text-sm text-blue-700">
                  Increase synthetic data generation for better cross-protocol learning
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

