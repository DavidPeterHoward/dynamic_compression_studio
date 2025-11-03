'use client'

import { Zap } from 'lucide-react'
import { memo } from 'react'

interface AlgorithmsViewProps {
    metrics: any
}

const AlgorithmsView = memo(({ metrics }: AlgorithmsViewProps) => {
    return (
        <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-6 flex items-center space-x-2">
                <Zap className="w-5 h-5" />
                <span>Algorithm Performance Analysis</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(metrics.algorithmPerformance).map(([algoName, perf]: [string, any]) => (
                    <div key={algoName} className="bg-slate-800/50 p-4 rounded-lg">
                        <h4 className="font-semibold mb-3 text-blue-400">{algoName}</h4>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-slate-400">Compression Ratio</span>
                                <span>{perf.compressionRatio.toFixed(1)}x</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-400">Speed</span>
                                <span>{perf.speed.toFixed(1)} MB/s</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-400">Quality</span>
                                <span>{perf.quality.toFixed(1)}%</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-400">Success Rate</span>
                                <span>{perf.successRate.toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
})

AlgorithmsView.displayName = 'AlgorithmsView'

export default AlgorithmsView
