'use client'

import { createContext, ReactNode, useContext, useEffect, useState } from 'react'
import { QueryClient, QueryClientProvider } from 'react-query'
import { ReactQueryDevtools } from 'react-query/devtools'

// Types for meta-recursive learning and system state
interface MetaLearningState {
  isActive: boolean
  currentIteration: number
  learningRate: number
  adaptationSpeed: number
  knowledgeBase: Record<string, any>
  performanceHistory: Array<{
    timestamp: number
    metrics: Record<string, number>
    improvements: string[]
  }>
}

interface SystemMetrics {
  cpu: number
  memory: number
  disk: number
  network: number
  compressionEfficiency: number
  algorithmPerformance: Record<string, number>
  userSatisfaction: number
  systemHealth: 'healthy' | 'warning' | 'error'
}

interface CompressionState {
  currentAlgorithm: string
  parameters: Record<string, any>
  history: Array<{
    id: string
    algorithm: string
    compressionRatio: number
    time: number
    timestamp: Date
  }>
  realTimeMetrics: {
    throughput: number
    successRate: number
    averageCompressionRatio: number
  }
}

interface ExperimentState {
  activeExperiments: Array<{
    id: string
    name: string
    type: 'algorithm' | 'parameter' | 'meta-learning' | 'synthetic' | 'comparison' | 'optimization'
    status: 'running' | 'completed' | 'failed' | 'queued' | 'paused'
    progress: number
    results: Record<string, any>
    // Enhanced tracking fields
    contentAnalysis?: {
      contentType: string
      contentSize: number
      contentPatterns: string[]
      entropy: number
      redundancy: number
      structure: string
      language: string
      encoding: string
      metadata: Record<string, any>
    }
    algorithms?: Array<{
      name: string
      version: string
      parameters: Record<string, any>
      performance: {
        compressionRatio: number
        speed: number
        memoryUsage: number
        accuracy: number
      }
      schema: {
        inputFormat: string
        outputFormat: string
        dataTypes: string[]
        constraints: Record<string, any>
      }
    }>
    compressionProgress: {
      currentPhase: 'analysis' | 'compression' | 'decompression' | 'validation' | 'optimization'
      phaseProgress: number
      processedBytes: number
      totalBytes: number
      currentAlgorithm: string
      compressionHistory: Array<{
        timestamp: Date
        algorithm: string
        ratio: number
        speed: number
        quality: number
      }>
    }
    generativeContent: {
      isGenerating: boolean
      generationType: 'synthetic' | 'augmented' | 'transformed'
      patterns: string[]
      complexity: number
      volume: number
      quality: number
      diversity: number
      generationProgress: number
      generatedSamples: Array<{
        id: string
        type: string
        size: number
        quality: number
        timestamp: Date
      }>
    }
    logs?: Array<{
      timestamp: Date
      level: 'info' | 'warning' | 'error' | 'debug'
      message: string
      data?: any
    }>
  }>
  syntheticDataGeneration: {
    isActive: boolean
    patterns: string[]
    complexity: number
    volume: number
  }
}

interface AppState {
  metaLearning: MetaLearningState
  systemMetrics: SystemMetrics
  compression: CompressionState
  experiments: ExperimentState
  theme: 'light' | 'dark' | 'auto'
  sidebarOpen: boolean
  notifications: Array<{
    id: string
    type: 'info' | 'success' | 'warning' | 'error'
    title: string
    message: string
    timestamp: Date
  }>
}

interface AppContextType {
  state: AppState
  updateMetaLearning: (updates: Partial<MetaLearningState>) => void
  updateSystemMetrics: (metrics: Partial<SystemMetrics>) => void
  updateCompression: (updates: Partial<CompressionState>) => void
  updateExperiments: (updates: Partial<ExperimentState>) => void
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  toggleSidebar: () => void
  setTheme: (theme: AppState['theme']) => void
  startMetaLearning: () => void
  stopMetaLearning: () => void
  generateSyntheticData: (patterns: string[], complexity: number, volume: number) => void
  runExperiment: (experiment: Omit<ExperimentState['activeExperiments'][0], 'id' | 'status' | 'progress' | 'results'>) => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

// Initial state
const initialState: AppState = {
  metaLearning: {
    isActive: false,
    currentIteration: 0,
    learningRate: 0.01,
    adaptationSpeed: 1.0,
    knowledgeBase: {},
    performanceHistory: []
  },
  systemMetrics: {
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
    compressionEfficiency: 0,
    algorithmPerformance: {},
    userSatisfaction: 0,
    systemHealth: 'healthy'
  },
  compression: {
    currentAlgorithm: 'content_aware',
    parameters: {
      level: 'balanced',
      optimization_target: 'ratio'
    },
    history: [],
    realTimeMetrics: {
      throughput: 0,
      successRate: 0,
      averageCompressionRatio: 0
    }
  },
  experiments: {
    activeExperiments: [],
    syntheticDataGeneration: {
      isActive: false,
      patterns: [],
      complexity: 0.5,
      volume: 1000
    }
  },
  theme: 'dark',
  sidebarOpen: false,
  notifications: []
}

// App Provider Component
export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 5 * 60 * 1000,
      },
    },
  }))

  const [state, setState] = useState<AppState>(initialState)

  // Update functions
  const updateMetaLearning = (updates: Partial<MetaLearningState>) => {
    setState(prev => ({
      ...prev,
      metaLearning: { ...prev.metaLearning, ...updates }
    }))
  }

  const updateSystemMetrics = (metrics: Partial<SystemMetrics>) => {
    setState(prev => ({
      ...prev,
      systemMetrics: { ...prev.systemMetrics, ...metrics }
    }))
  }

  const updateCompression = (updates: Partial<CompressionState>) => {
    setState(prev => ({
      ...prev,
      compression: { ...prev.compression, ...updates }
    }))
  }

  const updateExperiments = (updates: Partial<ExperimentState>) => {
    setState(prev => ({
      ...prev,
      experiments: { ...prev.experiments, ...updates }
    }))
  }

  const addNotification = (notification: Omit<AppState['notifications'][0], 'id' | 'timestamp'>) => {
    const newNotification = {
      ...notification,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date()
    }
    
    setState(prev => ({
      ...prev,
      notifications: [...prev.notifications, newNotification]
    }))
  }

  const removeNotification = (id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== id)
    }))
  }

  const toggleSidebar = () => {
    setState(prev => ({
      ...prev,
      sidebarOpen: !prev.sidebarOpen
    }))
  }

  const setTheme = (theme: AppState['theme']) => {
    setState(prev => ({ ...prev, theme }))
    document.documentElement.classList.remove('light', 'dark')
    if (theme !== 'auto') {
      document.documentElement.classList.add(theme)
    }
  }

  const startMetaLearning = async () => {
    updateMetaLearning({ isActive: true, currentIteration: 0 })
    
    const learningLoop = async () => {
      while (state.metaLearning.isActive) {
        try {
          const experience = {
            metrics: state.systemMetrics,
            compression: state.compression,
            experiments: state.experiments
          }
          
          updateMetaLearning({
            currentIteration: state.metaLearning.currentIteration + 1
          })
          
          await new Promise(resolve => setTimeout(resolve, 5000))
        } catch (error) {
          console.error('Meta-learning error:', error)
          addNotification({
            type: 'error',
            title: 'Meta-Learning Error',
            message: 'An error occurred during meta-learning iteration'
          })
        }
      }
    }
    
    learningLoop()
  }

  const stopMetaLearning = () => {
    updateMetaLearning({ isActive: false })
  }

  const generateSyntheticData = (patterns: string[], complexity: number, volume: number) => {
    updateExperiments({
      syntheticDataGeneration: {
        isActive: true,
        patterns,
        complexity,
        volume
      }
    })
    
    setTimeout(() => {
      updateExperiments({
        syntheticDataGeneration: {
          isActive: false,
          patterns,
          complexity,
          volume
        }
      })
      
      addNotification({
        type: 'success',
        title: 'Synthetic Data Generated',
        message: `Generated ${volume} data samples with ${patterns.length} patterns`
      })
    }, 2000)
  }

  const runExperiment = (experiment: any) => {
    const newExperiment = {
      ...experiment,
      id: Math.random().toString(36).substr(2, 9),
      status: 'running' as const,
      progress: 0,
      results: {},
      // Enhanced tracking data
      contentAnalysis: experiment.contentAnalysis || {
        contentType: 'mixed',
        contentSize: 1024 * 1024,
        contentPatterns: ['repetitive', 'structured'],
        entropy: 0.75,
        redundancy: 0.25,
        structure: 'hierarchical',
        language: 'english',
        encoding: 'utf-8',
        metadata: {}
      },
      algorithms: experiment.algorithms || [
        {
          name: 'gzip',
          version: '1.0',
          parameters: { level: 6 },
          performance: {
            compressionRatio: 2.5,
            speed: 50.0,
            memoryUsage: 32.0,
            accuracy: 0.95
          },
          schema: {
            inputFormat: 'binary',
            outputFormat: 'gzip',
            dataTypes: ['text', 'binary'],
            constraints: {}
          }
        }
      ],
      compressionProgress: experiment.compressionProgress || {
        currentPhase: 'analysis',
        phaseProgress: 0,
        processedBytes: 0,
        totalBytes: 1024 * 1024,
        currentAlgorithm: 'gzip',
        compressionHistory: []
      },
      generativeContent: experiment.generativeContent || {
        isGenerating: false,
        generationType: 'synthetic',
        patterns: ['repetitive', 'structured'],
        complexity: 0.7,
        volume: 1000,
        quality: 0.85,
        diversity: 0.8,
        generationProgress: 0,
        generatedSamples: []
      },
      logs: experiment.logs || []
    }
    
    setState(prev => ({
      ...prev,
      experiments: {
        ...prev.experiments,
        activeExperiments: [...prev.experiments.activeExperiments, newExperiment]
      }
    }))
    
    const progressInterval = setInterval(() => {
      setState(prev => {
        const updatedExperiments = prev.experiments.activeExperiments.map(exp => {
          if (exp.id === newExperiment.id) {
            const newProgress = Math.min(exp.progress + Math.random() * 20, 100)
            const newStatus: 'running' | 'completed' | 'failed' = newProgress >= 100 ? 'completed' : 'running'
            
            // Enhanced progress tracking
            const phases: Array<'analysis' | 'compression' | 'decompression' | 'validation' | 'optimization'> = ['analysis', 'compression', 'decompression', 'validation', 'optimization']
            const currentPhaseIndex = Math.floor(newProgress / 20)
            const currentPhase = phases[Math.min(currentPhaseIndex, phases.length - 1)]
            const phaseProgress = (newProgress % 20) * 5
            
            // Update compression progress
            const processedBytes = Math.floor((newProgress / 100) * (exp.compressionProgress?.totalBytes || 1024 * 1024))
            
            // Add compression history entry
            const compressionHistory = exp.compressionProgress?.compressionHistory || []
            if (Math.random() > 0.7) { // 30% chance to add history entry
              compressionHistory.push({
                timestamp: new Date(),
                algorithm: exp.compressionProgress?.currentAlgorithm || 'gzip',
                ratio: 2.0 + Math.random() * 2,
                speed: 30 + Math.random() * 40,
                quality: 0.8 + Math.random() * 0.2
              })
            }
            
            // Update generative content progress
            const generationProgress = Math.min(newProgress * 0.8, 100)
            const isGenerating = newProgress < 80
            
            // Add log entries
            const logs = exp.logs || []
            if (Math.random() > 0.8) { // 20% chance to add log
              logs.push({
                timestamp: new Date(),
                level: Math.random() > 0.9 ? 'warning' : 'info',
                message: `Processing phase: ${currentPhase} - ${phaseProgress.toFixed(1)}% complete`,
                data: {
                  phase: currentPhase,
                  progress: phaseProgress,
                  processedBytes
                }
              })
            }
            
            if (newStatus === 'completed') {
              clearInterval(progressInterval)
              addNotification({
                type: 'success',
                title: 'Experiment Completed',
                message: `Experiment "${exp.name}" has completed successfully`
              })
            }
            
            return {
              ...exp,
              progress: newProgress,
              status: newStatus,
              compressionProgress: {
                ...exp.compressionProgress,
                currentPhase,
                phaseProgress,
                processedBytes,
                compressionHistory
              },
              generativeContent: {
                ...exp.generativeContent,
                isGenerating,
                generationProgress
              },
              logs,
              results: newStatus === 'completed' ? {
                compressionRatio: 2.5 + Math.random() * 3,
                processingTime: 0.1 + Math.random() * 0.5,
                memoryUsage: 50 + Math.random() * 100,
                accuracy: 0.85 + Math.random() * 0.15
              } : exp.results
            }
          }
          return exp
        })
        
        return {
          ...prev,
          experiments: {
            ...prev.experiments,
            activeExperiments: updatedExperiments
          }
        }
      })
    }, 1000)
  }

  // System metrics polling
  useEffect(() => {
    const pollMetrics = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8443'}/api/v1/health/detailed`)
        if (response.ok) {
          const data = await response.json()
          
          updateSystemMetrics({
            cpu: data.performance_metrics?.cpu_usage_total || 0,
            memory: data.performance_metrics?.memory_usage_percent || 0,
            disk: data.performance_metrics?.disk_usage_percent || 0,
            network: 0,
            systemHealth: data.status === 'healthy' ? 'healthy' : 
                         data.status === 'warning' ? 'warning' : 'error'
          })
        }
      } catch (error) {
        console.error('Failed to fetch system metrics:', error)
      }
    }
    
    const interval = setInterval(pollMetrics, 10000)
    pollMetrics()
    
    return () => clearInterval(interval)
  }, [])

  // Auto-cleanup notifications
  useEffect(() => {
    const cleanupInterval = setInterval(() => {
      const now = Date.now()
      setState(prev => ({
        ...prev,
        notifications: prev.notifications.filter(n => 
          now - n.timestamp.getTime() < 30000
        )
      }))
    }, 5000)
    
    return () => clearInterval(cleanupInterval)
  }, [])

  const contextValue: AppContextType = {
    state,
    updateMetaLearning,
    updateSystemMetrics,
    updateCompression,
    updateExperiments,
    addNotification,
    removeNotification,
    toggleSidebar,
    setTheme,
    startMetaLearning,
    stopMetaLearning,
    generateSyntheticData,
    runExperiment
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AppContext.Provider value={contextValue}>
        {children}
      </AppContext.Provider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

// Hook to use app context
export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within a Providers')
  }
  return context
}
