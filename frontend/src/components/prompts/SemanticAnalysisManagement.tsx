'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    BarChart3,
    Brain,
    Eye,
    Filter,
    Hash,
    Plus,
    RefreshCw,
    Search,
    Settings,
    Tag,
    Target,
    Trash2,
    TrendingUp,
    XCircle
} from 'lucide-react'
import { useEffect, useState } from 'react'

// Types for semantic analysis
interface SemanticAnalysis {
  id: string
  prompt_id: string
  analysis_type: string
  semantic_embedding: number[]
  similarity_scores: SimilarityScore[]
  semantic_clusters: SemanticCluster[]
  topic_modeling: TopicModeling
  sentiment_analysis: SentimentAnalysis
  entity_extraction: EntityExtraction
  keyword_analysis: KeywordAnalysis
  semantic_similarity: SemanticSimilarity
  created_at: string
  updated_at: string
}

interface SimilarityScore {
  prompt_id: string
  similarity: number
  distance: number
  method: string
}

interface SemanticCluster {
  id: string
  name: string
  description: string
  prompts: string[]
  centroid: number[]
  size: number
  coherence: number
  separation: number
}

interface TopicModeling {
  topics: Topic[]
  coherence_score: number
  perplexity: number
  topic_distribution: Record<string, number>
}

interface Topic {
  id: string
  name: string
  keywords: string[]
  weight: number
  coherence: number
  prompts: string[]
}

interface SentimentAnalysis {
  overall_sentiment: string
  sentiment_score: number
  confidence: number
  emotional_tone: string
  subjectivity: number
  polarity: number
}

interface EntityExtraction {
  entities: Entity[]
  entity_types: Record<string, number>
  named_entities: NamedEntity[]
}

interface Entity {
  text: string
  type: string
  confidence: number
  start: number
  end: number
}

interface NamedEntity {
  text: string
  label: string
  confidence: number
  start: number
  end: number
}

interface KeywordAnalysis {
  keywords: Keyword[]
  key_phrases: KeyPhrase[]
  tf_idf_scores: Record<string, number>
  word_frequency: Record<string, number>
}

interface Keyword {
  word: string
  frequency: number
  importance: number
  tf_idf: number
}

interface KeyPhrase {
  phrase: string
  frequency: number
  importance: number
  length: number
}

interface SemanticSimilarity {
  similar_prompts: SimilarPrompt[]
  semantic_distance: number
  cosine_similarity: number
  euclidean_distance: number
  jaccard_similarity: number
}

interface SimilarPrompt {
  prompt_id: string
  similarity: number
  distance: number
  method: string
}

interface SemanticAnalysisConfig {
  embedding_model: string
  similarity_threshold: number
  cluster_algorithm: string
  topic_modeling_method: string
  sentiment_model: string
  entity_model: string
  keyword_extraction_method: string
}

export default function SemanticAnalysisManagement() {
  const [analyses, setAnalyses] = useState<SemanticAnalysis[]>([])
  const [selectedAnalysis, setSelectedAnalysis] = useState<SemanticAnalysis | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'similarity' | 'clustering' | 'topics' | 'sentiment' | 'entities' | 'keywords'>('overview')
  const [filters, setFilters] = useState({
    analysis_type: '',
    date_range: '',
    similarity_threshold: 0.5
  })
  const [loading, setLoading] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showConfigModal, setShowConfigModal] = useState(false)

  // Fetch analyses on component mount
  useEffect(() => {
    fetchAnalyses()
  }, [])

  const fetchAnalyses = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8443/api/v1/prompts/semantic-analysis/')
      if (response.ok) {
        const data = await response.json()
        setAnalyses(data.analyses || [])
      }
    } catch (error) {
      console.error('Error fetching analyses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAnalysis = () => {
    setShowCreateModal(true)
  }

  const handleConfigureAnalysis = () => {
    setShowConfigModal(true)
  }

  const handleRunAnalysis = async (promptId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/${promptId}/semantic-analysis`, {
        method: 'POST'
      })
      if (response.ok) {
        const data = await response.json()
        setAnalyses(prev => [data.analysis, ...prev])
      }
    } catch (error) {
      console.error('Error running analysis:', error)
    }
  }

  const handleViewAnalysis = (analysis: SemanticAnalysis) => {
    setSelectedAnalysis(analysis)
  }

  const handleDeleteAnalysis = async (analysisId: string) => {
    try {
      const response = await fetch(`http://localhost:8443/api/v1/prompts/semantic-analysis/${analysisId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setAnalyses(prev => prev.filter(a => a.id !== analysisId))
      }
    } catch (error) {
      console.error('Error deleting analysis:', error)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold gradient-text">Semantic Analysis</h3>
          <p className="text-slate-400">AI-powered semantic analysis and similarity detection</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchAnalyses}
            className="btn-secondary flex items-center space-x-2"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleConfigureAnalysis}
            className="btn-secondary flex items-center space-x-2"
          >
            <Settings className="w-4 h-4" />
            <span>Configure</span>
          </button>
          <button
            onClick={handleCreateAnalysis}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Run Analysis</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="glass p-4 rounded-xl">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm font-medium">Filters:</span>
          </div>
          <select
            value={filters.analysis_type}
            onChange={(e) => setFilters({...filters, analysis_type: e.target.value})}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          >
            <option value="">All Types</option>
            <option value="embedding">Embedding</option>
            <option value="similarity">Similarity</option>
            <option value="clustering">Clustering</option>
            <option value="topic_modeling">Topic Modeling</option>
            <option value="sentiment">Sentiment</option>
            <option value="entity">Entity Extraction</option>
            <option value="keyword">Keyword Analysis</option>
          </select>
          <select
            value={filters.date_range}
            onChange={(e) => setFilters({...filters, date_range: e.target.value})}
            className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
          >
            <option value="">All Time</option>
            <option value="1d">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <div className="flex items-center space-x-2">
            <label className="text-sm">Similarity Threshold:</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={filters.similarity_threshold}
              onChange={(e) => setFilters({...filters, similarity_threshold: parseFloat(e.target.value)})}
              className="w-20"
            />
            <span className="text-sm text-slate-400">{filters.similarity_threshold}</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="glass p-4 rounded-xl">
        <div className="flex space-x-1">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'similarity', label: 'Similarity', icon: Target },
            { id: 'clustering', label: 'Clustering', icon: Brain },
            { id: 'topics', label: 'Topics', icon: Hash },
            { id: 'sentiment', label: 'Sentiment', icon: TrendingUp },
            { id: 'entities', label: 'Entities', icon: Tag },
            { id: 'keywords', label: 'Keywords', icon: Search }
          ].map(tab => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <OverviewTab analyses={analyses} onView={handleViewAnalysis} onDelete={handleDeleteAnalysis} />
        )}
        {activeTab === 'similarity' && (
          <SimilarityTab analyses={analyses} onView={handleViewAnalysis} />
        )}
        {activeTab === 'clustering' && (
          <ClusteringTab analyses={analyses} onView={handleViewAnalysis} />
        )}
        {activeTab === 'topics' && (
          <TopicsTab analyses={analyses} onView={handleViewAnalysis} />
        )}
        {activeTab === 'sentiment' && (
          <SentimentTab analyses={analyses} onView={handleViewAnalysis} />
        )}
        {activeTab === 'entities' && (
          <EntitiesTab analyses={analyses} onView={handleViewAnalysis} />
        )}
        {activeTab === 'keywords' && (
          <KeywordsTab analyses={analyses} onView={handleViewAnalysis} />
        )}
      </AnimatePresence>

      {/* Modals */}
      {showCreateModal && (
        <CreateAnalysisModal
          onClose={() => setShowCreateModal(false)}
          onRun={handleRunAnalysis}
        />
      )}

      {showConfigModal && (
        <ConfigModal
          onClose={() => setShowConfigModal(false)}
        />
      )}

      {selectedAnalysis && (
        <AnalysisDetailModal
          analysis={selectedAnalysis}
          onClose={() => setSelectedAnalysis(null)}
        />
      )}
    </motion.div>
  )
}

// Sub-components
interface OverviewTabProps {
  analyses: SemanticAnalysis[]
  onView: (analysis: SemanticAnalysis) => void
  onDelete: (analysisId: string) => void
}

const OverviewTab = ({ analyses, onView, onDelete }: OverviewTabProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-blue-400 mb-2">{analyses.length}</div>
          <div className="text-sm text-slate-400">Total Analyses</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-green-400 mb-2">
            {analyses.reduce((acc, a) => acc + a.similarity_scores.length, 0)}
          </div>
          <div className="text-sm text-slate-400">Similarity Scores</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-purple-400 mb-2">
            {analyses.reduce((acc, a) => acc + a.semantic_clusters.length, 0)}
          </div>
          <div className="text-sm text-slate-400">Clusters</div>
        </div>
        <div className="glass p-6 rounded-xl text-center">
          <div className="text-3xl font-bold text-yellow-400 mb-2">
            {analyses.reduce((acc, a) => acc + a.topic_modeling.topics.length, 0)}
          </div>
          <div className="text-sm text-slate-400">Topics</div>
        </div>
      </div>

      {/* Analyses List */}
      <div className="space-y-4">
        {analyses.map(analysis => (
          <div key={analysis.id} className="glass p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-4">
                  <h5 className="font-semibold text-blue-400">
                    Analysis {analysis.id.slice(0, 8)}
                  </h5>
                  <span className="px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded">
                    {analysis.analysis_type}
                  </span>
                  <span className="text-sm text-slate-400">
                    {new Date(analysis.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="mt-2 text-sm text-slate-400">
                  Similarity Scores: {analysis.similarity_scores.length} | 
                  Clusters: {analysis.semantic_clusters.length} | 
                  Topics: {analysis.topic_modeling.topics.length}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onView(analysis)}
                  className="btn-secondary"
                >
                  <Eye className="w-4 h-4" />
                </button>
                <button
                  onClick={() => onDelete(analysis.id)}
                  className="btn-secondary text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {analyses.length === 0 && (
        <div className="text-center py-12">
          <Brain className="w-16 h-16 mx-auto mb-4 text-slate-400" />
          <h3 className="text-lg font-semibold mb-2">No analyses found</h3>
          <p className="text-slate-400 mb-4">Run your first semantic analysis to get started</p>
        </div>
      )}
    </motion.div>
  )
}

const SimilarityTab = ({ analyses, onView }: { analyses: SemanticAnalysis[], onView: (analysis: SemanticAnalysis) => void }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Similarity Analysis</h4>
      <div className="glass p-6 rounded-xl">
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Target className="w-16 h-16" />
          <span className="ml-2">Similarity Analysis Chart Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

const ClusteringTab = ({ analyses, onView }: { analyses: SemanticAnalysis[], onView: (analysis: SemanticAnalysis) => void }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Semantic Clustering</h4>
      <div className="glass p-6 rounded-xl">
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Brain className="w-16 h-16" />
          <span className="ml-2">Clustering Visualization Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

const TopicsTab = ({ analyses, onView }: { analyses: SemanticAnalysis[], onView: (analysis: SemanticAnalysis) => void }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Topic Modeling</h4>
      <div className="glass p-6 rounded-xl">
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Hash className="w-16 h-16" />
          <span className="ml-2">Topic Modeling Visualization Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

const SentimentTab = ({ analyses, onView }: { analyses: SemanticAnalysis[], onView: (analysis: SemanticAnalysis) => void }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Sentiment Analysis</h4>
      <div className="glass p-6 rounded-xl">
        <div className="h-64 flex items-center justify-center text-slate-400">
          <TrendingUp className="w-16 h-16" />
          <span className="ml-2">Sentiment Analysis Chart Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

const EntitiesTab = ({ analyses, onView }: { analyses: SemanticAnalysis[], onView: (analysis: SemanticAnalysis) => void }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Entity Extraction</h4>
      <div className="glass p-6 rounded-xl">
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Tag className="w-16 h-16" />
          <span className="ml-2">Entity Extraction Visualization Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

const KeywordsTab = ({ analyses, onView }: { analyses: SemanticAnalysis[], onView: (analysis: SemanticAnalysis) => void }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <h4 className="text-lg font-semibold">Keyword Analysis</h4>
      <div className="glass p-6 rounded-xl">
        <div className="h-64 flex items-center justify-center text-slate-400">
          <Search className="w-16 h-16" />
          <span className="ml-2">Keyword Analysis Visualization Placeholder</span>
        </div>
      </div>
    </motion.div>
  )
}

// Modal components
interface CreateAnalysisModalProps {
  onClose: () => void
  onRun: (promptId: string) => void
}

const CreateAnalysisModal = ({ onClose, onRun }: CreateAnalysisModalProps) => {
  const [formData, setFormData] = useState({
    prompt_id: '',
    analysis_type: 'comprehensive',
    config: {} as SemanticAnalysisConfig
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onRun(formData.prompt_id)
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Run Semantic Analysis</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Prompt ID</label>
            <input
              type="text"
              value={formData.prompt_id}
              onChange={(e) => setFormData({...formData, prompt_id: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              placeholder="Enter prompt ID or select from list"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Analysis Type</label>
            <select
              value={formData.analysis_type}
              onChange={(e) => setFormData({...formData, analysis_type: e.target.value})}
              className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="comprehensive">Comprehensive</option>
              <option value="similarity">Similarity Only</option>
              <option value="clustering">Clustering Only</option>
              <option value="topic_modeling">Topic Modeling Only</option>
              <option value="sentiment">Sentiment Only</option>
              <option value="entity">Entity Extraction Only</option>
              <option value="keyword">Keyword Analysis Only</option>
            </select>
          </div>
          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Run Analysis
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface ConfigModalProps {
  onClose: () => void
}

const ConfigModal = ({ onClose }: ConfigModalProps) => {
  const [config, setConfig] = useState<SemanticAnalysisConfig>({
    embedding_model: 'sentence-transformers/all-MiniLM-L6-v2',
    similarity_threshold: 0.5,
    cluster_algorithm: 'kmeans',
    topic_modeling_method: 'lda',
    sentiment_model: 'cardiffnlp/twitter-roberta-base-sentiment-latest',
    entity_model: 'dbmdz/bert-large-cased-finetuned-conll03-english',
    keyword_extraction_method: 'tfidf'
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Save configuration
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-2xl w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Configure Semantic Analysis</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Embedding Model</label>
              <select
                value={config.embedding_model}
                onChange={(e) => setConfig({...config, embedding_model: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="sentence-transformers/all-MiniLM-L6-v2">MiniLM-L6-v2</option>
                <option value="sentence-transformers/all-mpnet-base-v2">MPNet-base-v2</option>
                <option value="sentence-transformers/all-distilroberta-v1">DistilRoBERTa-v1</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Similarity Threshold</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.similarity_threshold}
                onChange={(e) => setConfig({...config, similarity_threshold: parseFloat(e.target.value)})}
                className="w-full"
              />
              <span className="text-sm text-slate-400">{config.similarity_threshold}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Cluster Algorithm</label>
              <select
                value={config.cluster_algorithm}
                onChange={(e) => setConfig({...config, cluster_algorithm: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="kmeans">K-Means</option>
                <option value="dbscan">DBSCAN</option>
                <option value="hierarchical">Hierarchical</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Topic Modeling Method</label>
              <select
                value={config.topic_modeling_method}
                onChange={(e) => setConfig({...config, topic_modeling_method: e.target.value})}
                className="w-full p-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="lda">LDA</option>
                <option value="nmf">NMF</option>
                <option value="bertopic">BERTopic</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Save Configuration
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

interface AnalysisDetailModalProps {
  analysis: SemanticAnalysis
  onClose: () => void
}

const AnalysisDetailModal = ({ analysis, onClose }: AnalysisDetailModalProps) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="glass p-6 rounded-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Analysis Details</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <XCircle className="w-6 h-6" />
          </button>
        </div>

        <div className="space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Analysis Type</label>
              <div className="text-slate-300">{analysis.analysis_type}</div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Created</label>
              <div className="text-slate-300">
                {new Date(analysis.created_at).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Similarity Scores */}
          <div>
            <h4 className="font-semibold mb-4">Similarity Scores</h4>
            <div className="space-y-2">
              {analysis.similarity_scores.slice(0, 5).map((score, index) => (
                <div key={index} className="flex justify-between p-2 bg-slate-800 rounded">
                  <span className="text-sm">Prompt {score.prompt_id.slice(0, 8)}</span>
                  <span className="text-sm text-blue-400">{(score.similarity * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Semantic Clusters */}
          <div>
            <h4 className="font-semibold mb-4">Semantic Clusters</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.semantic_clusters.map(cluster => (
                <div key={cluster.id} className="p-4 bg-slate-800 rounded-lg">
                  <h5 className="font-semibold text-blue-400 mb-2">{cluster.name}</h5>
                  <p className="text-sm text-slate-400 mb-2">{cluster.description}</p>
                  <div className="text-sm text-slate-300">
                    Size: {cluster.size} | Coherence: {(cluster.coherence * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Topics */}
          <div>
            <h4 className="font-semibold mb-4">Topics</h4>
            <div className="space-y-2">
              {analysis.topic_modeling.topics.map(topic => (
                <div key={topic.id} className="p-3 bg-slate-800 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold text-blue-400">{topic.name}</span>
                    <span className="text-sm text-slate-400">Weight: {(topic.weight * 100).toFixed(1)}%</span>
                  </div>
                  <div className="text-sm text-slate-300">
                    Keywords: {topic.keywords.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sentiment Analysis */}
          <div>
            <h4 className="font-semibold mb-4">Sentiment Analysis</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Overall Sentiment</label>
                <div className="text-slate-300">{analysis.sentiment_analysis.overall_sentiment}</div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Sentiment Score</label>
                <div className="text-slate-300">{(analysis.sentiment_analysis.sentiment_score * 100).toFixed(1)}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
