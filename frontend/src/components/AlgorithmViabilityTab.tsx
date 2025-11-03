'use client'

/**
 * Algorithm Viability Analysis Component
 * 
 * Provides comprehensive analysis and visualization of compression algorithm
 * performance, capabilities, and viability across different content types.
 * 
 * Features:
 * - Real-time algorithm testing and comparison
 * - Performance metrics and rankings
 * - Viability scoring and recommendations
 * - Interactive algorithm capabilities explorer
 * - Synthetic data integration for continuous testing
 */

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    Award,
    BarChart3,
    CheckCircle,
    Clock,
    FileText,
    Info,
    Loader2,
    Target,
    TrendingUp,
    Zap
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

// Types
interface AlgorithmPerformanceResult {
  algorithm: string
  success: boolean
  compression_ratio: number
  compression_percentage: number
  compression_time_ms: number
  throughput_mbps: number
  original_size: number
  compressed_size: number
  quality_score: number
  efficiency_score: number
  viability_rating: 'excellent' | 'good' | 'fair' | 'poor'
  recommendation: string
}

interface ViabilityAnalysisResponse {
  test_timestamp: string
  content_size: number
  total_algorithms_tested: number
  successful_tests: number
  algorithm_results: AlgorithmPerformanceResult[]
  best_compression_ratio: AlgorithmPerformanceResult
  best_speed: AlgorithmPerformanceResult
  best_balanced: AlgorithmPerformanceResult
  recommended_algorithm: string
  recommendation_reasoning: string[]
}

interface AlgorithmCapabilities {
  name: string
  category: string
  description: string
  typical_compression_ratio_range: [number, number]
  typical_speed: string
  memory_usage: string
  best_for: string[]
  characteristics: Record<string, any>
  viability_score: number
}

export default function AlgorithmViabilityTab() {
  // State
  const [testContent, setTestContent] = useState('')
  const [isTestinginProgress, setIsTestingProgress] = useState(false)
  const [viabilityResults, setViabilityResults] = useState<ViabilityAnalysisResponse | null>(null)
  const [algorithmCapabilities, setAlgorithmCapabilities] = useState<AlgorithmCapabilities[]>([])
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string | null>(null)
  const [includeExperimental, setIncludeExperimental] = useState(false)
  const [activeView, setActiveView] = useState<'testing' | 'capabilities' | 'results'>('testing')

  // Load algorithm capabilities on mount
  useEffect(() => {
    loadAlgorithmCapabilities()
  }, [])

  const loadAlgorithmCapabilities = async () => {
    try {
      const response = await fetch('/api/v1/compression/algorithm-viability/capabilities')
      const data = await response.json()
      setAlgorithmCapabilities(data)
    } catch (error) {
      console.error('Failed to load algorithm capabilities:', error)
    }
  }

  const runViabilityTest = useCallback(async () => {
    if (!testContent.trim()) {
      alert('Please enter test content')
      return
    }

    setIsTestingProgress(true)
    try {
      const response = await fetch('/api/v1/compression/algorithm-viability/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: testContent,
          include_experimental: includeExperimental
        })
      })

      const data = await response.json()
      setViabilityResults(data)
      setActiveView('results')
    } catch (error) {
      console.error('Viability test failed:', error)
      alert('Failed to run viability test. Please try again.')
    } finally {
      setIsTestingProgress(false)
    }
  }, [testContent, includeExperimental])

  const generateSyntheticTestData = () => {
    const samples = [
      'The quick brown fox jumps over the lazy dog. '.repeat(100),
      JSON.stringify({ users: Array(50).fill(0).map((_, i) => ({ id: i, name: `User${i}`, email: `user${i}@example.com` })) }, null, 2),
      Array(100).fill(0).map((_, i) => `[${Date.now() + i}] INFO [system] Request processed successfully`).join('\n'),
      'import React from "react"\n\nfunction Component() {\n  return <div>Hello World</div>\n}\n\nexport default Component\n'.repeat(10)
    ]
    setTestContent(samples[Math.floor(Math.random() * samples.length)])
  }

  const getViabilityColor = (rating: string) => {
    switch (rating) {
      case 'excellent': return 'text-green-400 bg-green-500/10 border-green-500/50'
      case 'good': return 'text-blue-400 bg-blue-500/10 border-blue-500/50'
      case 'fair': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/50'
      case 'poor': return 'text-red-400 bg-red-500/10 border-red-500/50'
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/50'
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'traditional': return 'from-blue-500/20 to-cyan-500/20 border-blue-500/50'
      case 'advanced': return 'from-purple-500/20 to-pink-500/20 border-purple-500/50'
      case 'experimental': return 'from-orange-500/20 to-red-500/20 border-orange-500/50'
      default: return 'from-gray-500/20 to-slate-500/20 border-gray-500/50'
    }
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2 flex items-center gap-2">
            <Target className="w-8 h-8" />
            Algorithm Viability Analysis
          </h1>
          <p className="text-slate-400">
            Comprehensive testing and analysis of compression algorithm performance
          </p>
        </div>

        {/* View Selector */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveView('testing')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeView === 'testing'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Testing
          </button>
          <button
            onClick={() => setActiveView('capabilities')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeView === 'capabilities'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Capabilities
          </button>
          {viabilityResults && (
            <button
              onClick={() => setActiveView('results')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeView === 'results'
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              Results
            </button>
          )}
        </div>
      </motion.div>

      {/* Testing View */}
      {activeView === 'testing' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Test Input */}
          <div className="lg:col-span-2 glass p-6 rounded-xl">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-400" />
              Test Content
            </h2>

            <textarea
              value={testContent}
              onChange={(e) => setTestContent(e.target.value)}
              placeholder="Enter or generate test content..."
              className="w-full h-64 input-field resize-none mb-4"
            />

            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-slate-400">
                {testContent.length.toLocaleString()} chars • {formatBytes(testContent.length)}
              </span>
              <button
                onClick={generateSyntheticTestData}
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Generate Synthetic Data
              </button>
            </div>

            <div className="flex items-center justify-between mb-4 p-3 bg-slate-800/50 rounded-lg">
              <span className="text-sm font-medium">Include Experimental Algorithms</span>
              <button
                onClick={() => setIncludeExperimental(!includeExperimental)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  includeExperimental ? 'bg-blue-600' : 'bg-slate-600'
                }`}
              >
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  includeExperimental ? 'translate-x-6' : 'translate-x-1'
                }`} />
              </button>
            </div>

            <button
              onClick={runViabilityTest}
              disabled={isTestinginProgress || !testContent.trim()}
              className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl hover:from-blue-600 hover:to-cyan-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isTestinginProgress ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Testing Algorithms...</span>
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  <span>Run Viability Test</span>
                </>
              )}
            </button>
          </div>

          {/* Quick Info */}
          <div className="space-y-4">
            <div className="glass p-6 rounded-xl">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Info className="w-5 h-5 text-cyan-400" />
                About Testing
              </h3>
              <div className="space-y-3 text-sm text-slate-300">
                <p>
                  The viability test compresses your content using all available algorithms
                  and provides comprehensive performance analysis.
                </p>
                <p className="text-slate-400">
                  Metrics include:
                </p>
                <ul className="list-disc list-inside text-slate-400 space-y-1">
                  <li>Compression ratio</li>
                  <li>Processing speed</li>
                  <li>Throughput (MB/s)</li>
                  <li>Quality & efficiency scores</li>
                  <li>Viability ratings</li>
                </ul>
              </div>
            </div>

            <div className="glass p-6 rounded-xl">
              <h3 className="text-sm font-semibold mb-3">Traditional Algorithms</h3>
              <div className="flex flex-wrap gap-2">
                {['GZIP', 'LZMA', 'BZIP2', 'LZ4', 'ZSTD', 'Brotli'].map((alg) => (
                  <span key={alg} className="text-xs bg-blue-900/30 text-blue-300 px-2 py-1 rounded">
                    {alg}
                  </span>
                ))}
              </div>

              <h3 className="text-sm font-semibold mb-3 mt-4">Experimental Algorithms</h3>
              <div className="flex flex-wrap gap-2">
                {['Quantum-Bio', 'Neuromorphic', 'Topological'].map((alg) => (
                  <span key={alg} className="text-xs bg-orange-900/30 text-orange-300 px-2 py-1 rounded">
                    {alg}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Capabilities View */}
      {activeView === 'capabilities' && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {algorithmCapabilities.map((capability) => (
            <motion.div
              key={capability.name}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`glass p-6 rounded-xl border-2 cursor-pointer transition-all ${
                selectedAlgorithm === capability.name
                  ? `bg-gradient-to-br ${getCategoryColor(capability.category)} shadow-lg`
                  : 'border-slate-700 hover:border-slate-600'
              }`}
              onClick={() => setSelectedAlgorithm(
                selectedAlgorithm === capability.name ? null : capability.name
              )}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold capitalize">{capability.name}</h3>
                <span className={`text-xs px-2 py-1 rounded ${
                  capability.category === 'traditional' ? 'bg-blue-900/50 text-blue-300' :
                  capability.category === 'advanced' ? 'bg-purple-900/50 text-purple-300' :
                  'bg-orange-900/50 text-orange-300'
                }`}>
                  {capability.category}
                </span>
              </div>

              <p className="text-sm text-slate-300 mb-4">{capability.description}</p>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400">Compression Ratio:</span>
                  <span className="font-semibold text-green-400">
                    {capability.typical_compression_ratio_range[0]}x - {capability.typical_compression_ratio_range[1]}x
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400">Speed:</span>
                  <span className="font-semibold text-blue-400 capitalize">
                    {capability.typical_speed.replace('_', ' ')}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400">Memory Usage:</span>
                  <span className="font-semibold text-purple-400 capitalize">
                    {capability.memory_usage.replace('_', ' ')}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400">Viability Score:</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded-full"
                        style={{ width: `${capability.viability_score * 100}%` }}
                      />
                    </div>
                    <span className="font-semibold text-cyan-400">
                      {(capability.viability_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>

              <AnimatePresence>
                {selectedAlgorithm === capability.name && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="mt-4 pt-4 border-t border-slate-700"
                  >
                    <h4 className="text-sm font-semibold mb-2">Best For:</h4>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {capability.best_for.map((use) => (
                        <span key={use} className="text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded">
                          {use}
                        </span>
                      ))}
                    </div>

                    <h4 className="text-sm font-semibold mb-2">Characteristics:</h4>
                    <div className="space-y-1">
                      {Object.entries(capability.characteristics).map(([key, value]) => (
                        <div key={key} className="flex items-center justify-between text-xs">
                          <span className="text-slate-400 capitalize">{key.replace('_', ' ')}:</span>
                          <span className={value === true ? 'text-green-400' : 'text-slate-300'}>
                            {typeof value === 'boolean' ? (value ? '✓' : '✗') : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      )}

      {/* Results View */}
      {activeView === 'results' && viabilityResults && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="glass p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-blue-400 mb-1">
                {viabilityResults.total_algorithms_tested}
              </div>
              <div className="text-sm text-slate-400">Algorithms Tested</div>
            </div>

            <div className="glass p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-green-400 mb-1">
                {viabilityResults.successful_tests}
              </div>
              <div className="text-sm text-slate-400">Successful Tests</div>
            </div>

            <div className="glass p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-purple-400 mb-1">
                {formatBytes(viabilityResults.content_size)}
              </div>
              <div className="text-sm text-slate-400">Content Size</div>
            </div>

            <div className="glass p-4 rounded-xl text-center">
              <div className="text-2xl font-bold text-yellow-400 mb-1 uppercase">
                {viabilityResults.recommended_algorithm}
              </div>
              <div className="text-sm text-slate-400">Recommended</div>
            </div>
          </div>

          {/* Best Performers */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="glass p-6 rounded-xl border-2 border-green-500/50">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-green-400" />
                Best Compression
              </h3>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-green-400 uppercase">
                  {viabilityResults.best_compression_ratio.algorithm}
                </div>
                <div className="text-3xl font-bold text-white">
                  {viabilityResults.best_compression_ratio.compression_ratio.toFixed(2)}x
                </div>
                <div className="text-sm text-slate-400">
                  {viabilityResults.best_compression_ratio.compression_percentage.toFixed(1)}% reduction
                </div>
              </div>
            </div>

            <div className="glass p-6 rounded-xl border-2 border-blue-500/50">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-400" />
                Fastest Speed
              </h3>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-blue-400 uppercase">
                  {viabilityResults.best_speed.algorithm}
                </div>
                <div className="text-3xl font-bold text-white">
                  {viabilityResults.best_speed.compression_time_ms.toFixed(1)}ms
                </div>
                <div className="text-sm text-slate-400">
                  {viabilityResults.best_speed.throughput_mbps.toFixed(2)} MB/s
                </div>
              </div>
            </div>

            <div className="glass p-6 rounded-xl border-2 border-purple-500/50">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-purple-400" />
                Best Balanced
              </h3>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-purple-400 uppercase">
                  {viabilityResults.best_balanced.algorithm}
                </div>
                <div className="text-3xl font-bold text-white">
                  {viabilityResults.best_balanced.efficiency_score.toFixed(3)}
                </div>
                <div className="text-sm text-slate-400">
                  Efficiency Score
                </div>
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="glass p-6 rounded-xl border-2 border-cyan-500/50">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-cyan-400" />
              Overall Recommendation
            </h3>
            <div className="mb-4">
              <span className="text-2xl font-bold text-cyan-400 uppercase">
                {viabilityResults.recommended_algorithm}
              </span>
            </div>
            <div className="space-y-2">
              {viabilityResults.recommendation_reasoning.map((reason, index) => (
                <div key={index} className="flex items-start gap-2 text-sm text-slate-300">
                  <TrendingUp className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                  <span>{reason}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Results Table */}
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-400" />
              Detailed Results
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-slate-300">Algorithm</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Ratio</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Time</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Throughput</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Quality</th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-slate-300">Viability</th>
                  </tr>
                </thead>
                <tbody>
                  {viabilityResults.algorithm_results
                    .filter(r => r.success)
                    .sort((a, b) => b.compression_ratio - a.compression_ratio)
                    .map((result) => (
                      <tr key={result.algorithm} className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-4">
                          <span className="font-semibold uppercase">{result.algorithm}</span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="text-green-400 font-semibold">{result.compression_ratio.toFixed(2)}x</span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="text-blue-400">{result.compression_time_ms.toFixed(1)}ms</span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="text-purple-400">{result.throughput_mbps.toFixed(2)} MB/s</span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <div className="w-16 bg-slate-700 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-yellow-500 to-green-500 h-2 rounded-full"
                                style={{ width: `${result.quality_score * 100}%` }}
                              />
                            </div>
                            <span className="text-xs text-slate-400">{(result.quality_score * 100).toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className={`text-xs px-2 py-1 rounded border ${getViabilityColor(result.viability_rating)}`}>
                            {result.viability_rating}
                          </span>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Run Another Test Button */}
          <div className="flex justify-center">
            <button
              onClick={() => setActiveView('testing')}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl hover:from-blue-600 hover:to-cyan-600 transition-all duration-200 flex items-center gap-2"
            >
              <Zap className="w-5 h-5" />
              <span>Run Another Test</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

