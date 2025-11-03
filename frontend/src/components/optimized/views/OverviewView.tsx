'use client'

import { Award, Zap } from 'lucide-react'
import { memo } from 'react'

interface OverviewViewProps {
    metrics: any
}

const OverviewView = memo(({ metrics }: OverviewViewProps) => {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Key Metrics */}
            <div className="glass p-6 rounded-xl">
                <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                    <Award className="w-5 h-5" />
                    <span>Key Performance Indicators</span>
                </h3>
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400">Overall Quality</span>
                        <span className="text-lg font-semibold">{metrics.qualityMetrics.overallQuality.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400">System Availability</span>
                        <span className="text-lg font-semibold">{metrics.systemPerformance.availability.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400">Innovation Score</span>
                        <span className="text-lg font-semibold">{metrics.experimentalResults.innovationScore.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400">Fusion Accuracy</span>
                        <span className="text-lg font-semibold">{metrics.sensorFusion.fusionAccuracy.toFixed(1)}%</span>
                    </div>
                </div>
            </div>

            {/* Top Algorithms */}
            <div className="glass p-6 rounded-xl">
                <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                    <Zap className="w-5 h-5" />
                    <span>Top Performing Algorithms</span>
                </h3>
                <div className="space-y-3">
                    {metrics.comparativeAnalysis.algorithmRanking.slice(0, 3).map((algo: any, index: number) => (
                        <div key={algo.algorithm} className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                                    index === 0 ? 'bg-yellow-500 text-yellow-900' :
                                    index === 1 ? 'bg-gray-400 text-gray-900' :
                                    'bg-orange-500 text-orange-900'
                                }`}>
                                    {index + 1}
                                </div>
                                <span className="font-medium">{algo.algorithm}</span>
                            </div>
                            <span className="text-lg font-semibold">{algo.score.toFixed(1)}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
})

OverviewView.displayName = 'OverviewView'

export default OverviewView
