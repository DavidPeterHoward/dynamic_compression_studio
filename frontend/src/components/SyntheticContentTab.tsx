'use client'

import { motion } from 'framer-motion'
import { Database, Image as ImageIcon, Music, Video } from 'lucide-react'
import { useState } from 'react'
import { SyntheticMediaTabNew } from './media'
import SyntheticDataTab from './SyntheticDataTab'

interface SyntheticDataConfig {
  patterns: string[]
  complexity: number
  volume: number
  contentType: string
  extensions: string[]
  mixedContent: boolean
  entropy: number
  redundancy: number
  structure: string
  language: string
  encoding: string
  metadata: Record<string, any>
  customPatterns: string[]
  compressionChallenges: boolean
  learningOptimization: boolean
  diversityControl: boolean
}

interface SyntheticContentTabProps {
  syntheticConfig: SyntheticDataConfig
  setSyntheticConfig: (config: SyntheticDataConfig) => void
  onGenerate: () => void
  isGenerating: boolean
}

type ContentType = 'data' | 'video' | 'image' | 'audio'

export default function SyntheticContentTab({
  syntheticConfig,
  setSyntheticConfig,
  onGenerate,
  isGenerating
}: SyntheticContentTabProps) {
  const [activeContentType, setActiveContentType] = useState<ContentType>('data')

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="glass p-6 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold gradient-text">Synthetic Content Generation</h2>
              <p className="text-slate-400">Advanced data and media generation for compression algorithm testing</p>
            </div>
          </div>
        </div>

        {/* Content Type Selector - Sub-tabs */}
        <div className="flex space-x-2 mt-4">
          <button
            data-testid="data-content-tab"
            onClick={() => setActiveContentType('data')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeContentType === 'data'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Database className="w-5 h-5" />
            <span>Data Files</span>
          </button>
          <button
            data-testid="video-content-tab"
            onClick={() => setActiveContentType('video')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeContentType === 'video'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Video className="w-5 h-5" />
            <span>Video</span>
          </button>
          <button
            data-testid="image-content-tab"
            onClick={() => setActiveContentType('image')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeContentType === 'image'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <ImageIcon className="w-5 h-5" />
            <span>Images</span>
          </button>
          <button
            data-testid="audio-content-tab"
            onClick={() => setActiveContentType('audio')}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              activeContentType === 'audio'
                ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-300 hover:bg-slate-700/50'
            }`}
          >
            <Music className="w-5 h-5" />
            <span>Audio</span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="mt-6">
        {activeContentType === 'data' && (
          <SyntheticDataTab
            syntheticConfig={syntheticConfig}
            setSyntheticConfig={setSyntheticConfig}
            onGenerate={onGenerate}
            isGenerating={isGenerating}
          />
        )}

        {(activeContentType === 'video' || activeContentType === 'image' || activeContentType === 'audio') && (
          <SyntheticMediaTabNew initialMediaType={activeContentType as 'video' | 'image' | 'audio'} />
        )}
      </div>
    </motion.div>
  )
}

