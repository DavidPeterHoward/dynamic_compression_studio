'use client'

import { motion } from 'framer-motion'
import { Activity, AlertCircle, CheckCircle, Clock, Database, TrendingUp, XCircle, Zap } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import {
    Area,
    AreaChart,
    CartesianGrid,
    Legend,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from 'recharts'

interface CompressionDataPoint {
  contentSize: number
  timestamp: number
  [algorithmName: string]: number
}

interface AlgorithmMetrics {
  name: string
  color: string
  enabled: boolean
  currentRatio: number
  trend: 'up' | 'down' | 'stable'
  viability: 'excellent' | 'good' | 'fair' | 'poor'
  viabilityScore: number
  reason: string
}

interface CompressionPerformanceGraphsProps {
  content: string
  selectedAlgorithm?: string
  realTimeUpdate?: boolean
}

const algorithmColors: Record<string, string> = {
  gzip: '#3b82f6',           // blue
  brotli: '#8b5cf6',         // purple
  lz4: '#10b981',            // green
  zstd: '#f59e0b',           // amber
  bzip2: '#ec4899',          // pink
  lzma: '#6366f1',           // indigo
  content_aware: '#14b8a6',  // teal
  quantum_biological: '#f97316', // orange
  neuromorphic: '#a855f7',   // violet
  topological: '#06b6d4'     // cyan
}

const CompressionPerformanceGraphs: React.FC<CompressionPerformanceGraphsProps> = ({
  content,
  selectedAlgorithm,
  realTimeUpdate = true
}) => {
  const [dataPoints, setDataPoints] = useState<CompressionDataPoint[]>([])
  const [algorithmMetrics, setAlgorithmMetrics] = useState<AlgorithmMetrics[]>([])
  const [isGenerating, setIsGenerating] = useState(false)

  // Initialize algorithm metrics
  useEffect(() => {
    const algorithms = Object.keys(algorithmColors).map(name => ({
      name,
      color: algorithmColors[name],
      enabled: selectedAlgorithm ? name === selectedAlgorithm : true,
      currentRatio: 1.0,
      trend: 'stable' as 'up' | 'down' | 'stable',
      viability: 'good' as 'excellent' | 'good' | 'fair' | 'poor',
      viabilityScore: 50,
      reason: 'Calculating...'
    }))
    setAlgorithmMetrics(algorithms)
  }, [selectedAlgorithm])

  // Generate real-time compression predictions
  useEffect(() => {
    if (!content || content.length === 0) {
      setDataPoints([])
      return
    }

    if (!realTimeUpdate) return

    setIsGenerating(true)

    // Simulate compression ratio calculations
    const contentSize = content.length
    
    // Calculate entropy of content for more accurate predictions
    const entropy = calculateEntropy(content)
    const repetitionRatio = calculateRepetitionRatio(content)
    
    const newDataPoint: CompressionDataPoint = {
      contentSize,
      timestamp: Date.now()
    }

    // Calculate compression ratios and viability for each algorithm
    const viabilityData: Record<string, { viability: 'excellent' | 'good' | 'fair' | 'poor', score: number, reason: string }> = {}
    
    Object.keys(algorithmColors).forEach(algorithm => {
      const ratio = predictCompressionRatio(algorithm, content, entropy, repetitionRatio)
      newDataPoint[algorithm] = ratio
      viabilityData[algorithm] = calculateViability(algorithm, content, entropy, repetitionRatio, ratio)
    })

    setDataPoints(prev => {
      const updated = [...prev, newDataPoint]
      // Keep last 20 data points for performance
      return updated.slice(-20)
    })

    // Update metrics with viability information
    setAlgorithmMetrics(prev => prev.map(metric => {
      const currentRatio = newDataPoint[metric.name]
      const viabilityInfo = viabilityData[metric.name]
      const trend = prev.find(m => m.name === metric.name)
        ? currentRatio > prev.find(m => m.name === metric.name)!.currentRatio ? 'up' 
        : currentRatio < prev.find(m => m.name === metric.name)!.currentRatio ? 'down'
        : 'stable'
        : 'stable'
      
      return {
        ...metric,
        currentRatio,
        trend,
        viability: viabilityInfo.viability,
        viabilityScore: viabilityInfo.score,
        reason: viabilityInfo.reason
      }
    }))

    setIsGenerating(false)
  }, [content, realTimeUpdate])

  // Calculate Shannon entropy
  const calculateEntropy = (text: string): number => {
    const freq: Record<string, number> = {}
    for (const char of text) {
      freq[char] = (freq[char] || 0) + 1
    }
    
    let entropy = 0
    const len = text.length
    for (const count of Object.values(freq)) {
      const p = count / len
      entropy -= p * Math.log2(p)
    }
    
    return entropy
  }

  // Calculate repetition ratio
  const calculateRepetitionRatio = (text: string): number => {
    const words = text.split(/\s+/)
    const uniqueWords = new Set(words)
    return words.length > 0 ? 1 - (uniqueWords.size / words.length) : 0
  }

  // Predict compression ratio based on algorithm characteristics
  const predictCompressionRatio = (
    algorithm: string,
    content: string,
    entropy: number,
    repetitionRatio: number
  ): number => {
    const size = content.length
    
    // Base compression ratios (tuned for different algorithms)
    const baseRatios: Record<string, number> = {
      gzip: 2.5,
      brotli: 3.0,
      lz4: 1.8,
      zstd: 2.8,
      bzip2: 3.5,
      lzma: 4.0,
      content_aware: 3.2,
      quantum_biological: 2.2,
      neuromorphic: 1.9,
      topological: 1.5
    }

    let ratio = baseRatios[algorithm] || 2.0

    // Adjust for entropy (lower entropy = better compression)
    const entropyFactor = 1 + (8 - entropy) / 8 * 0.5
    ratio *= entropyFactor

    // Adjust for repetition (higher repetition = better compression)
    ratio *= (1 + repetitionRatio * 0.8)

    // Adjust for size (larger files compress better)
    if (size < 100) ratio *= 0.7
    else if (size < 500) ratio *= 0.85
    else if (size < 1000) ratio *= 0.95

    // Add some variation for realism
    const variation = (Math.random() - 0.5) * 0.1
    ratio *= (1 + variation)

    return Math.max(1.0, Math.min(10.0, ratio))
  }

  // Calculate algorithm viability based on content characteristics
  const calculateViability = (
    algorithm: string,
    content: string,
    entropy: number,
    repetitionRatio: number,
    ratio: number
  ): { viability: 'excellent' | 'good' | 'fair' | 'poor', score: number, reason: string } => {
    const size = content.length
    let score = 0
    let reasons: string[] = []

    // Algorithm-specific viability rules
    switch (algorithm) {
      case 'gzip':
        if (entropy < 5) { score += 30; reasons.push('Low entropy') }
        if (repetitionRatio > 0.3) { score += 25; reasons.push('High repetition') }
        if (size > 1000) { score += 20; reasons.push('Good size') }
        score += Math.min(25, ratio * 5)
        break

      case 'brotli':
        if (entropy < 6) { score += 25; reasons.push('Text-friendly') }
        if (repetitionRatio > 0.2) { score += 25; reasons.push('Pattern-rich') }
        if (size > 500) { score += 25; reasons.push('Optimal size') }
        score += Math.min(25, ratio * 5)
        break

      case 'lz4':
        if (size < 10000) { score += 35; reasons.push('Fast compression') }
        if (repetitionRatio > 0.4) { score += 30; reasons.push('High repetition') }
        score += Math.min(35, ratio * 7)
        break

      case 'zstd':
        if (entropy < 6.5) { score += 30; reasons.push('Balanced entropy') }
        if (repetitionRatio > 0.25) { score += 25; reasons.push('Good patterns') }
        if (size > 500) { score += 20; reasons.push('Suitable size') }
        score += Math.min(25, ratio * 5)
        break

      case 'bzip2':
        if (entropy < 5.5) { score += 25; reasons.push('Low entropy') }
        if (repetitionRatio > 0.35) { score += 30; reasons.push('High repetition') }
        if (size > 1000) { score += 20; reasons.push('Large data') }
        score += Math.min(25, ratio * 5)
        break

      case 'lzma':
        if (entropy < 5) { score += 30; reasons.push('Very compressible') }
        if (repetitionRatio > 0.3) { score += 25; reasons.push('Repetitive content') }
        if (size > 2000) { score += 20; reasons.push('Large file') }
        score += Math.min(25, ratio * 4)
        break

      case 'content_aware':
        score += 40 // Always good due to AI adaptation
        if (size > 500) { score += 30; reasons.push('AI-optimized') }
        score += Math.min(30, ratio * 6)
        reasons.push('Adaptive')
        break

      case 'quantum_biological':
        if (repetitionRatio > 0.4) { score += 30; reasons.push('Pattern correlation') }
        if (size > 100 && size < 5000) { score += 25; reasons.push('Optimal for quantum') }
        if (entropy > 4 && entropy < 7) { score += 20; reasons.push('Quantum advantage') }
        score += Math.min(25, ratio * 5)
        break

      case 'neuromorphic':
        if (size > 200) { score += 25; reasons.push('Neural patterns') }
        if (repetitionRatio > 0.3 && repetitionRatio < 0.7) { score += 30; reasons.push('Temporal patterns') }
        if (entropy > 5) { score += 20; reasons.push('Complex data') }
        score += Math.min(25, ratio * 6)
        break

      case 'topological':
        if (size > 500) { score += 30; reasons.push('Geometric structure') }
        if (entropy > 5.5) { score += 25; reasons.push('Complex topology') }
        if (repetitionRatio < 0.5) { score += 20; reasons.push('Diverse patterns') }
        score += Math.min(25, ratio * 5)
        break
    }

    // Determine viability category
    let viability: 'excellent' | 'good' | 'fair' | 'poor'
    if (score >= 80) viability = 'excellent'
    else if (score >= 60) viability = 'good'
    else if (score >= 40) viability = 'fair'
    else viability = 'poor'

    return {
      viability,
      score: Math.min(100, score),
      reason: reasons.slice(0, 2).join(', ') || 'General use'
    }
  }

  // Toggle algorithm visibility
  const toggleAlgorithm = (algorithmName: string) => {
    setAlgorithmMetrics(prev => prev.map(metric =>
      metric.name === algorithmName ? { ...metric, enabled: !metric.enabled } : metric
    ))
  }

  // Calculate statistics
  const stats = useMemo(() => {
    if (dataPoints.length === 0) return null

    const latest = dataPoints[dataPoints.length - 1]
    const enabledAlgorithms = algorithmMetrics.filter(m => m.enabled)
    
    const ratios = enabledAlgorithms.map(m => latest[m.name]).filter(r => r > 0)
    const bestRatio = Math.max(...ratios)
    const avgRatio = ratios.reduce((a, b) => a + b, 0) / ratios.length
    const worstRatio = Math.min(...ratios)

    return {
      best: { 
        ratio: bestRatio,
        algorithm: enabledAlgorithms.find(m => latest[m.name] === bestRatio)?.name || ''
      },
      average: avgRatio,
      worst: {
        ratio: worstRatio,
        algorithm: enabledAlgorithms.find(m => latest[m.name] === worstRatio)?.name || ''
      },
      originalSize: latest.contentSize,
      estimatedCompressed: Math.round(latest.contentSize / avgRatio)
    }
  }, [dataPoints, algorithmMetrics])

  if (!content || content.length === 0) {
    return (
      <div className="p-8 rounded-xl bg-slate-800/30 border border-slate-700/50 text-center">
        <Activity className="w-12 h-12 mx-auto text-slate-600 mb-3" />
        <p className="text-slate-400">Enter content to see real-time compression predictions</p>
      </div>
    )
  }

  // Get viability colors and icons
  const getViabilityColor = (viability: string) => {
    switch (viability) {
      case 'excellent':
        return 'from-green-500/20 to-emerald-500/20 border-green-500/50 text-green-300'
      case 'good':
        return 'from-blue-500/20 to-cyan-500/20 border-blue-500/50 text-blue-300'
      case 'fair':
        return 'from-yellow-500/20 to-amber-500/20 border-yellow-500/50 text-yellow-300'
      case 'poor':
        return 'from-red-500/20 to-rose-500/20 border-red-500/50 text-red-300'
      default:
        return 'from-gray-500/20 to-slate-500/20 border-gray-500/50 text-gray-300'
    }
  }

  const getViabilityIcon = (viability: string) => {
    switch (viability) {
      case 'excellent':
        return <CheckCircle className="w-3 h-3" />
      case 'good':
        return <CheckCircle className="w-3 h-3" />
      case 'fair':
        return <AlertCircle className="w-3 h-3" />
      case 'poor':
        return <XCircle className="w-3 h-3" />
      default:
        return <Activity className="w-3 h-3" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Algorithm Viability Pills */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50"
      >
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center">
          <Activity className="w-4 h-4 mr-2" />
          Algorithm Viability Analysis
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {algorithmMetrics.filter(m => m.enabled).map(metric => (
            <motion.div
              key={metric.name}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`p-3 rounded-lg bg-gradient-to-br border-2 min-w-0 ${getViabilityColor(metric.viability)}`}
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-xs font-semibold uppercase truncate flex-1 min-w-0">{metric.name}</span>
                <div className="flex-shrink-0">{getViabilityIcon(metric.viability)}</div>
              </div>
              <div className="flex items-center space-x-2 mb-2">
                <div 
                  className="w-2 h-2 rounded-full flex-shrink-0" 
                  style={{ backgroundColor: metric.color }}
                />
                <span className="text-lg font-bold whitespace-nowrap">{metric.currentRatio.toFixed(1)}x</span>
              </div>
              <div className="text-xs opacity-75 mb-2 truncate" title={metric.reason}>{metric.reason}</div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-xs font-semibold capitalize truncate">{metric.viability}</span>
                <span className="text-xs font-semibold flex-shrink-0 tabular-nums">{Math.round(metric.viabilityScore)}%</span>
              </div>
              <div className="w-full bg-black/20 rounded-full h-1.5">
                <div
                  className="h-1.5 rounded-full transition-all duration-300"
                  style={{
                    width: `${metric.viabilityScore}%`,
                    backgroundColor: metric.color
                  }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 rounded-xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/30"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-green-300">Best Ratio</span>
              <TrendingUp className="w-4 h-4 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-white">{stats.best.ratio.toFixed(1)}x</div>
            <div className="text-xs text-green-300 mt-1">{stats.best.algorithm}</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border border-blue-500/30"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-blue-300">Average Ratio</span>
              <Activity className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-white">{stats.average.toFixed(1)}x</div>
            <div className="text-xs text-blue-300 mt-1">Across all algorithms</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/30"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-purple-300">Original Size</span>
              <Database className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-white">{stats.originalSize}</div>
            <div className="text-xs text-purple-300 mt-1">bytes</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="p-4 rounded-xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/30"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-amber-300">Est. Compressed</span>
              <Zap className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-white">{stats.estimatedCompressed}</div>
            <div className="text-xs text-amber-300 mt-1">bytes (avg)</div>
          </motion.div>
        </div>
      )}

      {/* Main Graph */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">Compression Ratio vs Content Size</h3>
            <p className="text-sm text-slate-400">Real-time predictions as you type</p>
          </div>
          {isGenerating && (
            <div className="flex items-center space-x-2 text-cyan-400">
              <Clock className="w-4 h-4 animate-spin" />
              <span className="text-sm">Calculating...</span>
            </div>
          )}
        </div>

        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={dataPoints}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="contentSize"
              stroke="#64748b"
              label={{ value: 'Content Size (bytes)', position: 'insideBottom', offset: -5, fill: '#94a3b8' }}
            />
            <YAxis
              stroke="#64748b"
              label={{ value: 'Compression Ratio', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '0.5rem',
                color: '#fff'
              }}
              formatter={(value: number) => `${value.toFixed(2)}x`}
            />
            <Legend />
             {algorithmMetrics.filter(m => m.enabled).map(metric => {
               // Adjust line appearance based on viability
               const getStrokeWidth = () => {
                 switch (metric.viability) {
                   case 'excellent': return 3
                   case 'good': return 2.5
                   case 'fair': return 2
                   case 'poor': return 1.5
                   default: return 2
                 }
               }

               const getStrokeDasharray = () => {
                 if (metric.viability === 'poor') return '5 5'
                 if (metric.viability === 'fair') return '8 4'
                 return undefined
               }

               const getOpacity = () => {
                 switch (metric.viability) {
                   case 'excellent': return 1
                   case 'good': return 0.9
                   case 'fair': return 0.7
                   case 'poor': return 0.5
                   default: return 0.8
                 }
               }

               return (
                 <Line
                   key={metric.name}
                   type="monotone"
                   dataKey={metric.name}
                   stroke={metric.color}
                   strokeWidth={getStrokeWidth()}
                   strokeDasharray={getStrokeDasharray()}
                   strokeOpacity={getOpacity()}
                   dot={{ 
                     fill: metric.color, 
                     r: metric.viability === 'excellent' ? 5 : metric.viability === 'good' ? 4 : 3,
                     strokeWidth: 2,
                     stroke: '#1e293b'
                   }}
                   activeDot={{ 
                     r: 8,
                     stroke: metric.color,
                     strokeWidth: 3,
                     fill: '#1e293b'
                   }}
                   name={`${metric.name} (${metric.viability})`}
                 />
               )
             })}
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Comparison Chart (With vs Without Compression) */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50"
      >
        <h3 className="text-lg font-semibold text-white mb-4">Size Comparison: Original vs Compressed</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={dataPoints}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="contentSize"
              stroke="#64748b"
              label={{ value: 'Content Size (bytes)', position: 'insideBottom', offset: -5, fill: '#94a3b8' }}
            />
            <YAxis
              stroke="#64748b"
              label={{ value: 'Size (bytes)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '0.5rem',
                color: '#fff'
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="contentSize"
              stroke="#ef4444"
              fill="#ef4444"
              fillOpacity={0.3}
              name="Original Size"
            />
            {selectedAlgorithm && (
              <Area
                type="monotone"
                dataKey={(data: CompressionDataPoint) => data.contentSize / (data[selectedAlgorithm] || 1)}
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.3}
                name="Compressed Size"
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </motion.div>

       {/* Algorithm Toggle with Viability */}
       <motion.div
         initial={{ opacity: 0, y: 20 }}
         animate={{ opacity: 1, y: 0 }}
         transition={{ delay: 0.6 }}
         className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50"
       >
         <h3 className="text-sm font-semibold text-white mb-3">Algorithm Controls</h3>
         <div className="flex flex-wrap gap-2">
           {algorithmMetrics.map(metric => (
             <button
               key={metric.name}
               onClick={() => toggleAlgorithm(metric.name)}
               className={`px-3 py-2 rounded-lg text-sm font-medium transition-all relative ${
                 metric.enabled
                   ? 'bg-slate-700 border-2 text-white shadow-lg'
                   : 'bg-slate-800/50 border border-slate-700 text-slate-400'
               }`}
               style={{
                 borderColor: metric.enabled ? metric.color : undefined
               }}
             >
               <div className="flex items-center space-x-2">
                 <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: metric.color }} />
                 <span>{metric.name}</span>
                 {metric.enabled && (
                   <>
                     <span className="text-xs opacity-75">
                       {metric.currentRatio.toFixed(2)}x
                       {metric.trend === 'up' && ' ↑'}
                       {metric.trend === 'down' && ' ↓'}
                     </span>
                     <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                       metric.viability === 'excellent' ? 'bg-green-500/20 text-green-300' :
                       metric.viability === 'good' ? 'bg-blue-500/20 text-blue-300' :
                       metric.viability === 'fair' ? 'bg-yellow-500/20 text-yellow-300' :
                       'bg-red-500/20 text-red-300'
                     }`}>
                       {metric.viability}
                     </span>
                   </>
                 )}
               </div>
             </button>
           ))}
         </div>
         <div className="mt-3 text-xs text-slate-400">
           <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
               <div className="w-3 h-0.5 bg-white"></div>
               <span>Excellent/Good</span>
             </div>
             <div className="flex items-center space-x-1">
               <div className="w-3 h-0.5 bg-white" style={{ borderTop: '2px dashed white', background: 'transparent' }}></div>
               <span>Fair</span>
             </div>
             <div className="flex items-center space-x-1">
               <div className="w-3 h-0.5 bg-white opacity-50" style={{ borderTop: '2px dashed white', background: 'transparent' }}></div>
               <span>Poor</span>
             </div>
           </div>
         </div>
       </motion.div>
    </div>
  )
}

export default CompressionPerformanceGraphs

