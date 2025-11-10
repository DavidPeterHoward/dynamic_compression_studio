'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@//components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import {
  Sparkles,
  Brain,
  MessageSquare,
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  Users,
  Settings,
  Zap,
  Target,
  Clock,
  Send,
  Bot,
  User,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  Copy,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

interface AIRecommendation {
  id: string
  type: 'optimization' | 'deployment' | 'configuration' | 'alert' | 'insight'
  priority: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  impact: 'low' | 'medium' | 'high'
  confidence: number
  category: string
  suggestedActions: string[]
  metrics: {
    potentialImprovement?: number
    estimatedTime?: string
    riskLevel?: 'low' | 'medium' | 'high'
  }
  timestamp: string
  status: 'pending' | 'applied' | 'dismissed' | 'in_progress'
}

interface ConversationMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  suggestions?: string[]
  actions?: string[]
}

interface AIAgentAssistantProps {
  recommendations: AIRecommendation[]
  onRecommendationAction?: (recommendationId: string, action: 'apply' | 'dismiss' | 'defer') => void
  onSendMessage?: (message: string) => void
  conversation?: ConversationMessage[]
  isTyping?: boolean
  className?: string
}

export default function AIAgentAssistant({
  recommendations,
  onRecommendationAction,
  onSendMessage,
  conversation = [],
  isTyping = false,
  className = ''
}: AIAgentAssistantProps) {
  const [activeTab, setActiveTab] = useState<'recommendations' | 'chat' | 'insights'>('recommendations')
  const [selectedRecommendation, setSelectedRecommendation] = useState<AIRecommendation | null>(null)
  const [messageInput, setMessageInput] = useState('')
  const [expandedRecommendations, setExpandedRecommendations] = useState<Set<string>>(new Set())
  const chatEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation, isTyping])

  const handleSendMessage = () => {
    if (messageInput.trim()) {
      onSendMessage?.(messageInput.trim())
      setMessageInput('')
    }
  }

  const toggleRecommendation = (id: string) => {
    const newExpanded = new Set(expandedRecommendations)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedRecommendations(newExpanded)
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-400 bg-red-500/20 border-red-500/30'
      case 'high': return 'text-orange-400 bg-orange-500/20 border-orange-500/30'
      case 'medium': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30'
      case 'low': return 'text-blue-400 bg-blue-500/20 border-blue-500/30'
      default: return 'text-gray-400 bg-gray-500/20 border-gray-500/30'
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-green-400'
      case 'medium': return 'text-yellow-400'
      case 'low': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'optimization': return <TrendingUp className="w-4 h-4" />
      case 'deployment': return <Zap className="w-4 h-4" />
      case 'configuration': return <Settings className="w-4 h-4" />
      case 'alert': return <AlertTriangle className="w-4 h-4" />
      case 'insight': return <Lightbulb className="w-4 h-4" />
      default: return <Sparkles className="w-4 h-4" />
    }
  }

  const pendingRecommendations = recommendations.filter(r => r.status === 'pending')
  const appliedRecommendations = recommendations.filter(r => r.status === 'applied')

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl shadow-lg">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">AI Agent Assistant</h2>
            <p className="text-slate-400">Intelligent recommendations and insights</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="border-purple-500/30 text-purple-400">
            {pendingRecommendations.length} pending
          </Badge>
          <Badge variant="outline" className="border-green-500/30 text-green-400">
            {appliedRecommendations.length} applied
          </Badge>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-slate-800/50 p-1 rounded-lg">
        <Button
          variant={activeTab === 'recommendations' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('recommendations')}
          className="flex-1"
        >
          <Lightbulb className="w-4 h-4 mr-2" />
          Recommendations ({pendingRecommendations.length})
        </Button>
        <Button
          variant={activeTab === 'chat' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('chat')}
          className="flex-1"
        >
          <MessageSquare className="w-4 h-4 mr-2" />
          Chat
        </Button>
        <Button
          variant={activeTab === 'insights' ? 'default' : 'ghost'}
          size="sm"
          onClick={() => setActiveTab('insights')}
          className="flex-1"
        >
          <Brain className="w-4 h-4 mr-2" />
          Insights
        </Button>
      </div>

      {/* Recommendations Tab */}
      <AnimatePresence mode="wait">
        {activeTab === 'recommendations' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {pendingRecommendations.length === 0 ? (
              <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardContent className="p-8 text-center">
                  <CheckCircle className="w-16 h-16 mx-auto text-green-400 mb-4" />
                  <h3 className="text-lg font-medium text-slate-300 mb-2">All Caught Up!</h3>
                  <p className="text-slate-400">No pending recommendations at this time.</p>
                </CardContent>
              </Card>
            ) : (
              pendingRecommendations.map((rec) => (
                <Card key={rec.id} className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${getPriorityColor(rec.priority)}`}>
                          {getTypeIcon(rec.type)}
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{rec.title}</h3>
                          <div className="flex items-center space-x-2 mt-1">
                            <Badge variant="outline" className={getPriorityColor(rec.priority)}>
                              {rec.priority}
                            </Badge>
                            <Badge variant="outline" className="border-slate-600">
                              {rec.category}
                            </Badge>
                            <span className={`text-sm ${getImpactColor(rec.impact)}`}>
                              {rec.impact} impact
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <div className="text-right">
                          <div className="text-sm text-slate-400">Confidence</div>
                          <div className="text-lg font-bold text-blue-400">{rec.confidence}%</div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleRecommendation(rec.id)}
                        >
                          {expandedRecommendations.has(rec.id) ?
                            <ChevronUp className="w-4 h-4" /> :
                            <ChevronDown className="w-4 h-4" />
                          }
                        </Button>
                      </div>
                    </div>

                    <p className="text-slate-300 mb-4">{rec.description}</p>

                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      {rec.metrics.potentialImprovement && (
                        <div className="text-center p-3 bg-slate-700/30 rounded-lg">
                          <div className="text-2xl font-bold text-green-400">
                            +{rec.metrics.potentialImprovement}%
                          </div>
                          <div className="text-sm text-slate-400">Potential Improvement</div>
                        </div>
                      )}

                      {rec.metrics.estimatedTime && (
                        <div className="text-center p-3 bg-slate-700/30 rounded-lg">
                          <div className="text-2xl font-bold text-blue-400">
                            {rec.metrics.estimatedTime}
                          </div>
                          <div className="text-sm text-slate-400">Estimated Time</div>
                        </div>
                      )}

                      {rec.metrics.riskLevel && (
                        <div className="text-center p-3 bg-slate-700/30 rounded-lg">
                          <div className={`text-2xl font-bold ${
                            rec.metrics.riskLevel === 'low' ? 'text-green-400' :
                            rec.metrics.riskLevel === 'medium' ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {rec.metrics.riskLevel.toUpperCase()}
                          </div>
                          <div className="text-sm text-slate-400">Risk Level</div>
                        </div>
                      )}
                    </div>

                    {/* Suggested Actions */}
                    <AnimatePresence>
                      {expandedRecommendations.has(rec.id) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="space-y-3"
                        >
                          <div>
                            <h4 className="font-medium text-slate-300 mb-2">Suggested Actions:</h4>
                            <ul className="space-y-1">
                              {rec.suggestedActions.map((action, index) => (
                                <li key={index} className="flex items-center space-x-2 text-sm text-slate-400">
                                  <div className="w-1.5 h-1.5 bg-blue-400 rounded-full" />
                                  <span>{action}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div className="flex items-center space-x-2 pt-3 border-t border-slate-600">
                            <Button
                              size="sm"
                              onClick={() => onRecommendationAction?.(rec.id, 'apply')}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <CheckCircle className="w-4 h-4 mr-2" />
                              Apply
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => onRecommendationAction?.(rec.id, 'defer')}
                              className="border-slate-600"
                            >
                              <Clock className="w-4 h-4 mr-2" />
                              Later
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => onRecommendationAction?.(rec.id, 'dismiss')}
                              className="border-slate-600"
                            >
                              <XCircle className="w-4 h-4 mr-2" />
                              Dismiss
                            </Button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </CardContent>
                </Card>
              ))
            )}

            {/* Applied Recommendations Summary */}
            {appliedRecommendations.length > 0 && (
              <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span>Applied Recommendations</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {appliedRecommendations.slice(0, 5).map((rec) => (
                      <div key={rec.id} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                        <span className="text-sm">{rec.title}</span>
                        <Badge variant="outline" className="border-green-500/30 text-green-400">
                          Applied
                        </Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Tab */}
      <AnimatePresence mode="wait">
        {activeTab === 'chat' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bot className="w-5 h-5" />
                  <span>AI Assistant Chat</span>
                </CardTitle>
                <CardDescription>Ask questions about your agents and get intelligent responses</CardDescription>
              </CardHeader>
              <CardContent>
                {/* Chat Messages */}
                <div className="h-96 overflow-y-auto space-y-4 mb-4 p-4 bg-slate-900/50 rounded-lg">
                  {conversation.map((message) => (
                    <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-md p-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-700 text-slate-200'
                      }`}>
                        <div className="flex items-center space-x-2 mb-1">
                          {message.role === 'user' ? (
                            <User className="w-4 h-4" />
                          ) : (
                            <Bot className="w-4 h-4" />
                          )}
                          <span className="text-xs opacity-70">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <p className="text-sm">{message.content}</p>

                        {/* Suggestions */}
                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="mt-2 space-y-1">
                            {message.suggestions.map((suggestion, index) => (
                              <Button
                                key={index}
                                size="sm"
                                variant="outline"
                                className="text-xs border-slate-600 hover:border-slate-500 mr-1 mb-1"
                                onClick={() => setMessageInput(suggestion)}
                              >
                                {suggestion}
                              </Button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-slate-700 text-slate-200 p-3 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <Bot className="w-4 h-4" />
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                            <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>

                {/* Chat Input */}
                <div className="flex space-x-2">
                  <Input
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask about your agents..."
                    className="flex-1 bg-slate-700/50 border-slate-600"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!messageInput.trim() || isTyping}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>

                {/* Quick Suggestions */}
                <div className="mt-4 flex flex-wrap gap-2">
                  {[
                    "How can I optimize agent performance?",
                    "What agents need attention?",
                    "Show me system health insights",
                    "Recommend new agent deployments",
                    "Analyze recent task failures"
                  ].map((suggestion) => (
                    <Button
                      key={suggestion}
                      size="sm"
                      variant="outline"
                      className="text-xs border-slate-600 hover:border-slate-500"
                      onClick={() => setMessageInput(suggestion)}
                    >
                      {suggestion}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Insights Tab */}
      <AnimatePresence mode="wait">
        {activeTab === 'insights' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* System Insights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5 text-green-400" />
                    <span>Performance Insights</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <TrendingUp className="w-4 h-4 text-green-400" />
                      <span className="font-medium text-green-400">Optimization Opportunity</span>
                    </div>
                    <p className="text-sm text-slate-300">
                      Database Agent response time improved by 35% after recent optimization.
                    </p>
                  </div>

                  <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Users className="w-4 h-4 text-blue-400" />
                      <span className="font-medium text-blue-400">Collaboration Insight</span>
                    </div>
                    <p className="text-sm text-slate-300">
                      Agent collaboration increased efficiency by 22% across workflows.
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-400" />
                    <span>System Alerts</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-400" />
                      <span className="font-medium text-yellow-400">Warning</span>
                    </div>
                    <p className="text-sm text-slate-300">
                      Meta-Learner Agent showing signs of overfitting. Consider retraining.
                    </p>
                  </div>

                  <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                      <span className="font-medium text-red-400">Critical Alert</span>
                    </div>
                    <p className="text-sm text-slate-300">
                      API Layer Agent experiencing high error rates. Immediate attention required.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Predictive Analytics */}
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5 text-purple-400" />
                  <span>Predictive Analytics</span>
                </CardTitle>
                <CardDescription>AI-powered predictions and forecasting</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-slate-700/30 rounded-lg">
                    <div className="text-2xl font-bold text-blue-400 mb-2">85%</div>
                    <p className="text-sm text-slate-400">Predicted task success rate</p>
                    <p className="text-xs text-green-400 mt-1">+5% from current</p>
                  </div>

                  <div className="text-center p-4 bg-slate-700/30 rounded-lg">
                    <div className="text-2xl font-bold text-green-400 mb-2">2.3s</div>
                    <p className="text-sm text-slate-400">Predicted avg response time</p>
                    <p className="text-xs text-green-400 mt-1">-0.8s improvement</p>
                  </div>

                  <div className="text-center p-4 bg-slate-700/30 rounded-lg">
                    <div className="text-2xl font-bold text-purple-400 mb-2">94%</div>
                    <p className="text-sm text-slate-400">Predicted system uptime</p>
                    <p className="text-xs text-green-400 mt-1">+2% improvement</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

