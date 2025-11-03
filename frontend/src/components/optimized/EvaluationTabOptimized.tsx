'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    BarChart3,
    Brain,
    GitCompare,
    RefreshCw,
    Target,
    TestTube,
    TrendingUp,
    XCircle,
    Zap
} from 'lucide-react'
import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from 'react'
import { useMetrics } from '../../hooks/useMetrics'
import { API_BASE_URL } from '../../lib/constants'

// Lazy load heavy components
const OverviewView = lazy(() => import('./views/OverviewView'))
const AlgorithmsView = lazy(() => import('./views/AlgorithmsView'))
// const PerformanceView = lazy(() => import('./views/PerformanceView'))
// const QualityView = lazy(() => import('./views/QualityView'))
// const ExperimentsView = lazy(() => import('./views/ExperimentsView'))
// const ComparisonView = lazy(() => import('./views/ComparisonView'))
// const TrendsView = lazy(() => import('./views/TrendsView'))
// const SensorFusionView = lazy(() => import('./views/SensorFusionView'))

// Memoized components for better performance
const LoadingSpinner = () => (
    <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Loading evaluation data...</span>
        </div>
    </div>
)

const ErrorDisplay = ({ error, onRetry }: { error: string; onRetry: () => void }) => (
    <div className="flex items-center justify-center h-64">
        <div className="text-center">
            <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-red-400 mb-2">Error Loading Data</h3>
            <p className="text-slate-400 mb-4">{error}</p>
            <button
                onClick={onRetry}
                className="btn-secondary flex items-center space-x-2 mx-auto"
            >
                <RefreshCw className="w-4 h-4" />
                <span>Retry</span>
            </button>
        </div>
    </div>
)

// Memoized view navigation
const ViewNavigation = ({ views, activeView, onViewChange }: {
    views: Array<{ id: string; label: string; icon: any }>
    activeView: string
    onViewChange: (viewId: string) => void
}) => (
    <div className="glass p-4 rounded-xl">
        <div className="flex space-x-2 overflow-x-auto">
            {views.map((view) => {
                const Icon = view.icon
                return (
                    <button
                        key={view.id}
                        onClick={() => onViewChange(view.id)}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 whitespace-nowrap ${
                            activeView === view.id
                                ? 'bg-blue-500 text-white'
                                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700'
                        }`}
                    >
                        <Icon className="w-4 h-4" />
                        <span>{view.label}</span>
                    </button>
                )
            })}
        </div>
    </div>
)

// Default fallback data with memoization
const defaultEvaluationData = {
    algorithmPerformance: {
        gzip: {
            compressionRatio: 2.5,
            speed: 15.2,
            memoryUsage: 45.8,
            accuracy: 95.2,
            efficiency: 88.5,
            reliability: 92.1,
            adaptability: 85.3,
            quality: 89.7,
            throughput: 125.6,
            successRate: 98.5
        },
        zstandard: {
            compressionRatio: 3.2,
            speed: 18.7,
            memoryUsage: 52.3,
            accuracy: 97.8,
            efficiency: 91.2,
            reliability: 94.5,
            adaptability: 88.9,
            quality: 92.3,
            throughput: 145.2,
            successRate: 99.1
        }
    },
    systemPerformance: {
        cpu: 45.2,
        memory: 62.8,
        disk: 78.5,
        network: 23.1,
        gpu: 15.7,
        temperature: 42.3,
        powerConsumption: 125.6,
        responseTime: 45.8,
        throughput: 156.7,
        errorRate: 1.2,
        availability: 99.8
    },
    contentAnalysis: {
        totalFiles: 1250,
        totalSize: 1048576000,
        contentTypes: { text: 450, image: 300, video: 200, audio: 150, binary: 150 },
        complexityScores: { text: 0.65, image: 0.85, video: 0.92, audio: 0.78, binary: 0.45 },
        entropyDistribution: { low: 0.25, medium: 0.45, high: 0.30 },
        averageFileSize: 838860,
        largestFileSize: 52428800,
        smallestFileSize: 1024
    },
    experimentalResults: {
        totalExperiments: 85,
        successfulExperiments: 78,
        failedExperiments: 7,
        metaLearningProgress: 72.5,
        syntheticDataGenerated: 524288000,
        algorithmEvolutions: 12,
        performanceImprovements: { compression_ratio: 15.2, speed: 8.7, quality: 12.3 },
        innovationScore: 85.7,
        experimentSuccessRate: 91.8
    },
    qualityMetrics: {
        overallQuality: 88.5,
        compressionQuality: 91.2,
        decompressionQuality: 89.7,
        dataIntegrity: 99.8,
        consistency: 87.3,
        reliability: 92.1,
        userSatisfaction: 85.9,
        accuracy: 94.6
    },
    comparativeAnalysis: {
        algorithmRanking: [
            { algorithm: "zstandard", score: 94.5, rank: 1 },
            { algorithm: "gzip", score: 88.7, rank: 2 },
            { algorithm: "brotli", score: 85.3, rank: 3 }
        ],
        performanceComparison: {
            zstandard: { compression_ratio: 3.2, speed: 18.7, quality: 92.3 },
            gzip: { compression_ratio: 2.5, speed: 15.2, quality: 89.7 },
            brotli: { compression_ratio: 2.8, speed: 16.8, quality: 91.1 }
        },
        efficiencyAnalysis: { zstandard: 91.2, gzip: 88.5, brotli: 89.8 },
        qualityComparison: { zstandard: 92.3, gzip: 89.7, brotli: 91.1 },
        costBenefitAnalysis: {
            zstandard: { cost: 0.15, benefit: 0.92, ratio: 6.13 },
            gzip: { cost: 0.12, benefit: 0.85, ratio: 7.08 },
            brotli: { cost: 0.14, benefit: 0.89, ratio: 6.36 }
        }
    },
    sensorFusion: {
        multiModalData: {
            compression_metrics: 0.92,
            system_metrics: 0.88,
            quality_metrics: 0.91,
            user_feedback: 0.85
        },
        crossValidationScores: {
            algorithm_performance: 0.89,
            system_performance: 0.87,
            quality_assessment: 0.91
        },
        ensembleScores: {
            weighted_average: 0.89,
            majority_voting: 0.87,
            stacking: 0.92
        },
        confidenceIntervals: {
            compression_ratio: { lower: 2.8, upper: 3.6, confidence: 0.95 },
            quality_score: { lower: 88.5, upper: 94.2, confidence: 0.95 }
        },
        fusionAccuracy: 91.3,
        dataCorrelation: {
            compression_quality: 0.85,
            system_performance: 0.78,
            user_satisfaction: 0.82
        }
    }
}

export default function EvaluationTabOptimized() {
    const [activeView, setActiveView] = useState('overview')
    const [evaluationMetrics, setEvaluationMetrics] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [filters, setFilters] = useState({
        timeRange: {
            start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            end: new Date().toISOString()
        },
        algorithms: [],
        metrics: [],
        view: 'overview'
    })

    // Use the useMetrics hook for consistency with other components
    const { metrics: systemMetrics, loading: systemLoading, error: systemError, refresh: refreshSystemMetrics } = useMetrics()

    // Memoized views configuration
    const views = useMemo(() => [
        { id: 'overview', label: 'Overview', icon: BarChart3 },
        { id: 'algorithms', label: 'Algorithms', icon: Zap },
        { id: 'performance', label: 'Performance', icon: Activity },
        { id: 'quality', label: 'Quality', icon: Target },
        { id: 'experiments', label: 'Experiments', icon: TestTube },
        { id: 'comparison', label: 'Comparison', icon: GitCompare },
        { id: 'trends', label: 'Trends', icon: TrendingUp },
        { id: 'sensor-fusion', label: 'Sensor Fusion', icon: Brain }
    ], [])

    // Memoized fetch function with error handling
    const fetchEvaluationMetrics = useCallback(async () => {
        try {
            setLoading(true)
            setError(null)
            
            const response = await fetch(`${API_BASE_URL}/api/v1/evaluation/metrics`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filters: {
                        time_range: "day",
                        algorithms: filters.algorithms,
                        content_types: [],
                        min_compression_ratio: 0,
                        max_compression_ratio: 10
                    },
                    view: filters.view,
                    include_details: true,
                    format: "json"
                })
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const result = await response.json()
            
            if (result.success && result.data) {
                // Transform the backend data structure to match our frontend interface
                const transformedData = {
                    algorithmPerformance: {},
                    systemPerformance: {
                        cpu: result.data.system_performance?.cpu_usage || 0,
                        memory: result.data.system_performance?.memory_usage || 0,
                        disk: result.data.system_performance?.disk_usage || 0,
                        network: result.data.system_performance?.network_usage || 0,
                        gpu: result.data.system_performance?.gpu_usage || 0,
                        temperature: result.data.system_performance?.temperature || 0,
                        powerConsumption: result.data.system_performance?.power_consumption || 0,
                        responseTime: result.data.system_performance?.response_time || 0,
                        throughput: result.data.system_performance?.throughput || 0,
                        errorRate: result.data.system_performance?.error_rate || 0,
                        availability: result.data.system_performance?.availability || 0
                    },
                    contentAnalysis: {
                        totalFiles: result.data.content_analysis?.total_files || 0,
                        totalSize: result.data.content_analysis?.total_size || 0,
                        contentTypes: result.data.content_analysis?.content_types || {},
                        complexityScores: result.data.content_analysis?.complexity_scores || {},
                        entropyDistribution: result.data.content_analysis?.entropy_distribution || {},
                        averageFileSize: result.data.content_analysis?.average_file_size || 0,
                        largestFileSize: result.data.content_analysis?.largest_file_size || 0,
                        smallestFileSize: result.data.content_analysis?.smallest_file_size || 0
                    },
                    experimentalResults: {
                        totalExperiments: result.data.experimental_results?.total_experiments || 0,
                        successfulExperiments: result.data.experimental_results?.successful_experiments || 0,
                        failedExperiments: result.data.experimental_results?.failed_experiments || 0,
                        metaLearningProgress: result.data.experimental_results?.meta_learning_progress || 0,
                        syntheticDataGenerated: result.data.experimental_results?.synthetic_data_generated || 0,
                        algorithmEvolutions: result.data.experimental_results?.algorithm_evolutions || 0,
                        performanceImprovements: result.data.experimental_results?.performance_improvements || {},
                        innovationScore: result.data.experimental_results?.innovation_score || 0,
                        experimentSuccessRate: result.data.experimental_results?.experiment_success_rate || 0
                    },
                    qualityMetrics: {
                        overallQuality: result.data.quality_metrics?.overall_quality || 0,
                        compressionQuality: result.data.quality_metrics?.compression_quality || 0,
                        decompressionQuality: result.data.quality_metrics?.decompression_quality || 0,
                        dataIntegrity: result.data.quality_metrics?.data_integrity || 0,
                        consistency: result.data.quality_metrics?.consistency || 0,
                        reliability: result.data.quality_metrics?.reliability || 0,
                        userSatisfaction: result.data.quality_metrics?.user_satisfaction || 0,
                        accuracy: result.data.quality_metrics?.accuracy || 0
                    },
                    comparativeAnalysis: {
                        algorithmRanking: result.data.comparative_analysis?.algorithm_ranking || [],
                        performanceComparison: result.data.comparative_analysis?.performance_comparison || {},
                        efficiencyAnalysis: result.data.comparative_analysis?.efficiency_analysis || {},
                        qualityComparison: result.data.comparative_analysis?.quality_comparison || {},
                        costBenefitAnalysis: result.data.comparative_analysis?.cost_benefit_analysis || {}
                    },
                    sensorFusion: {
                        multiModalData: result.data.sensor_fusion?.multi_modal_data || {},
                        crossValidationScores: result.data.sensor_fusion?.cross_validation_scores || {},
                        ensembleScores: result.data.sensor_fusion?.ensemble_scores || {},
                        confidenceIntervals: result.data.sensor_fusion?.confidence_intervals || {},
                        fusionAccuracy: result.data.sensor_fusion?.fusion_accuracy || 0,
                        dataCorrelation: result.data.sensor_fusion?.data_correlation || {}
                    }
                }

                // Transform algorithm performance data
                if (result.data.algorithm_performance) {
                    result.data.algorithm_performance.forEach((algo: any) => {
                        (transformedData.algorithmPerformance as any)[algo.algorithm_name] = {
                            compressionRatio: algo.compression_ratio || 0,
                            speed: algo.compression_speed || 0,
                            memoryUsage: algo.memory_usage || 0,
                            accuracy: algo.accuracy || 0,
                            efficiency: algo.efficiency || 0,
                            reliability: algo.reliability || 0,
                            adaptability: algo.adaptability || 0,
                            quality: algo.quality || 0,
                            throughput: algo.throughput || 0,
                            successRate: algo.success_rate || 0
                        }
                    })
                }

                setEvaluationMetrics(transformedData)
            } else {
                throw new Error(result.message || 'Failed to fetch evaluation metrics')
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
            console.error('Error fetching evaluation metrics:', err)
            // Use fallback data if API fails
            setEvaluationMetrics(defaultEvaluationData)
        } finally {
            setLoading(false)
        }
    }, [filters])

    useEffect(() => {
        fetchEvaluationMetrics()
    }, [fetchEvaluationMetrics])

    const handleRefresh = useCallback(() => {
        fetchEvaluationMetrics()
        refreshSystemMetrics()
    }, [fetchEvaluationMetrics, refreshSystemMetrics])

    const handleViewChange = useCallback((viewId: string) => {
        setActiveView(viewId)
        setFilters(prev => ({ ...prev, view: viewId }))
    }, [])

    // Use evaluation metrics if available, otherwise use fallback data
    const metrics = evaluationMetrics || defaultEvaluationData

    if (loading) {
        return <LoadingSpinner />
    }

    if (error && !evaluationMetrics) {
        return <ErrorDisplay error={error} onRetry={handleRefresh} />
    }

    // Memoized view components mapping
    const viewComponents = useMemo(() => ({
        overview: OverviewView,
        algorithms: AlgorithmsView,
        // performance: PerformanceView,
        // quality: QualityView,
        // experiments: ExperimentsView,
        // comparison: ComparisonView,
        // trends: TrendsView,
        // 'sensor-fusion': SensorFusionView
    }), [])

    const ActiveViewComponent = viewComponents[activeView as keyof typeof viewComponents]

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold gradient-text">Evaluation Dashboard</h1>
                    <p className="text-slate-400">Comprehensive analysis of compression algorithms and system performance</p>
                </div>
                <button
                    onClick={handleRefresh}
                    className="btn-secondary flex items-center space-x-2"
                >
                    <RefreshCw className="w-4 h-4" />
                    <span>Refresh</span>
                </button>
            </div>

            {/* View Navigation */}
            <ViewNavigation 
                views={views} 
                activeView={activeView} 
                onViewChange={handleViewChange} 
            />

            {/* Content */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={activeView}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                >
                    <Suspense fallback={<LoadingSpinner />}>
                        {ActiveViewComponent && (
                            <ActiveViewComponent metrics={metrics} />
                        )}
                    </Suspense>
                </motion.div>
            </AnimatePresence>
        </div>
    )
}
