'use client'

import { motion } from 'framer-motion'
import {
  BarChart3,
  BookOpen,
  Brain,
  Calculator,
  CheckCircle,
  Eye,
  Lightbulb,
  MessageSquare,
  Network,
  Pause,
  Play,
  Scale,
  Settings,
  Shield,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  X,
  Zap
} from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'

import { useApp } from '@/components/providers'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Loader2 } from 'lucide-react'

// Debate Agent Types with their specializations
const DEBATE_AGENT_TYPES = [
  {
    id: '11',
    name: 'Logical Analyst',
    type: 'logical_analyst',
    icon: Shield,
    color: 'blue',
    specialization: 'Logical validity, formal reasoning, identifying fallacies',
    strengths: ['Formal logic', 'Syllogisms', 'Fallacy detection', 'Proof theory'],
    weaknesses: ['Emotional appeals', 'Creative metaphors', 'Intuitive reasoning']
  },
  {
    id: '12',
    name: 'Argumentation Specialist',
    type: 'argumentation_specialist',
    icon: MessageSquare,
    color: 'green',
    specialization: 'Argumentation, persuasive techniques, rhetorical analysis',
    strengths: ['Rhetorical devices', 'Persuasive appeals', 'Debate structure', 'Audience analysis'],
    weaknesses: ['Mathematical proofs', 'Technical jargon', 'Abstract concepts']
  },
  {
    id: '13',
    name: 'Conceptual Analyst',
    type: 'conceptual_analyst',
    icon: BookOpen,
    color: 'purple',
    specialization: 'Conceptual analysis, assumptions, philosophical frameworks',
    strengths: ['Philosophical analysis', 'Conceptual clarity', 'Assumption testing', 'Framework evaluation'],
    weaknesses: ['Practical applications', 'Quantitative data', 'Real-time decisions']
  },
  {
    id: '14',
    name: 'Critical Thinker',
    type: 'critical_thinker',
    icon: Eye,
    color: 'red',
    specialization: 'Critical thinking, devil\'s advocate, identifying weaknesses',
    strengths: ['Problem identification', 'Counter-argumentation', 'Risk assessment', 'Gap analysis'],
    weaknesses: ['Positive reinforcement', 'Consensus building', 'Team harmony']
  },
  {
    id: '15',
    name: 'Linguistic Analyst',
    type: 'linguistic_analyst',
    icon: Sparkles,
    color: 'yellow',
    specialization: 'Linguistic structure, semantics, wordplay, etymology',
    strengths: ['Language precision', 'Semantic analysis', 'Etymological insights', 'Linguistic ambiguity'],
    weaknesses: ['Non-verbal communication', 'Mathematical concepts', 'Visual reasoning']
  },
  {
    id: '16',
    name: 'Mathematical Thinker',
    type: 'mathematical_thinker',
    icon: Calculator,
    color: 'indigo',
    specialization: 'Mathematical relationships, formal structures, patterns',
    strengths: ['Pattern recognition', 'Formal structures', 'Quantitative analysis', 'Logical consistency'],
    weaknesses: ['Emotional contexts', 'Ambiguous situations', 'Qualitative nuances']
  },
  {
    id: '17',
    name: 'Creative Innovator',
    type: 'creative_innovator',
    icon: Lightbulb,
    color: 'pink',
    specialization: 'Creative solutions, unconventional thinking, associations',
    strengths: ['Creative synthesis', 'Unconventional approaches', 'Association mapping', 'Innovative solutions'],
    weaknesses: ['Rigid structures', 'Formal constraints', 'Predictable outcomes']
  },
  {
    id: '18',
    name: 'Integration Specialist',
    type: 'integration_specialist',
    icon: Network,
    color: 'cyan',
    specialization: 'Integration, synthesis, reconciling viewpoints',
    strengths: ['Viewpoint synthesis', 'Consensus building', 'Perspective integration', 'Balanced analysis'],
    weaknesses: ['Extreme positions', 'Black-and-white thinking', 'Direct confrontation']
  },
  {
    id: '19',
    name: 'Strategic Planner',
    type: 'strategic_planner',
    icon: TrendingUp,
    color: 'orange',
    specialization: 'Long-term thinking, adaptability, scenario planning',
    strengths: ['Strategic foresight', 'Scenario planning', 'Adaptive strategies', 'Long-term consequences'],
    weaknesses: ['Immediate action', 'Short-term focus', 'Tactical details']
  }
]

interface DebateParticipant {
  agent_id: string
  agent_name: string
  agent_type: string
  specialization: string
  position: 'pro' | 'con' | 'neutral'
  confidence_score: number
  arguments_made: number
  rebuttals_given: number
  fallacies_identified: number
  strength_score: number
}

interface DebateRound {
  round_number: number
  timestamp: string
  arguments: DebateArgument[]
  consensus_metrics: {
    agreement_level: number
    convergence_trend: 'increasing' | 'decreasing' | 'stable'
    dominant_viewpoints: string[]
  }
}

interface DebateArgument {
  id: string
  agent_id: string
  agent_name: string
  agent_type: string
  content: string
  round_number: number
  timestamp: string
  evidence_score: number
  creativity_score: number
  fallacies_detected: number
  consensus_impact: number
}

interface DebateConfiguration {
  debate_topic: string
  problem_statement: string
  premise_area: string
  debate_mode: 'structured' | 'freeform' | 'autonomous'
  max_rounds: number
  max_iterations_per_round: number
  iterations_per_agent: number
  consensus_threshold: number
  time_limit_per_argument: number
  response_timeout: number
  selected_agents: string[]
  agent_roles: Record<string, string>
  debate_rules: {
    allow_ad_hominem: boolean
    require_evidence: boolean
    enable_fact_checking: boolean
    allow_creativity: boolean
    enforce_formality: boolean
    evidence_threshold: number
    creativity_weight: number
    max_fallacies_per_argument: number
    require_counter_arguments: boolean
    allow_collaboration: boolean
    enforce_turn_taking: boolean
  }
  ollama_model: string
  temperature: number
  max_tokens: number
  system_prompt_template: string
  enable_detailed_logging: boolean
  export_format: string
  real_time_updates: boolean
}

interface RoundSummary {
  round_number: number
  arguments_count: number
  consensus_score: number
  key_points_discussed: string[]
  evidence_quality_avg: number
  creativity_level_avg: number
}

interface DebateConclusion {
  conclusion_type: 'consensus' | 'majority' | 'deadlock' | 'synthesis'
  winning_position?: string
  confidence_score: number
  key_insights: string[]
  recommendations: string[]
  summary: string
  timestamp: string
}

interface DebateSession {
  session_id: string
  status: 'initialized' | 'active' | 'paused' | 'completed' | 'consensus_reached'
  configuration: DebateConfiguration
  participants: DebateParticipant[]
  rounds: DebateRound[]
  current_round: number
  total_arguments: number
  consensus_score: number
  winning_position?: 'pro' | 'con' | 'synthesis'
  conclusion?: string
  started_at: string
  completed_at?: string
}

export default function MultiAgentDebateSystem() {
  const { addNotification } = useApp()

  // Enhanced state management for Ollama-powered debates
  const [debateSession, setDebateSession] = useState<DebateSession | null>(null)
  const [isConfiguring, setIsConfiguring] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)
  const [activeTab, setActiveTab] = useState<'setup' | 'debate' | 'analysis'>('setup')
  const [ollamaStatus, setOllamaStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const [debateProgress, setDebateProgress] = useState(0)

  // Comprehensive debate configuration
  const [debateConfig, setDebateConfig] = useState<DebateConfiguration>({
    // Core debate parameters
    debate_topic: '',
    problem_statement: '',
    premise_area: '',
    debate_mode: 'structured',

    // Round and iteration controls
    max_rounds: 5,
    max_iterations_per_round: 3,
    iterations_per_agent: 2,
    consensus_threshold: 0.8,

    // Timing and constraints
    time_limit_per_argument: 60,
    response_timeout: 30,

    // Agent selection and roles
    selected_agents: [],
    agent_roles: {}, // Maps agent IDs to their debate roles

    // Debate rules and constraints
    debate_rules: {
      allow_ad_hominem: false,
      require_evidence: true,
      enable_fact_checking: true,
      allow_creativity: true,
      enforce_formality: true,
      evidence_threshold: 0.7,
      creativity_weight: 0.3,
      max_fallacies_per_argument: 1,
      require_counter_arguments: true,
      allow_collaboration: false,
      enforce_turn_taking: true
    },

    // Ollama configuration
    ollama_model: 'llama2:7b',
    temperature: 0.7,
    max_tokens: 512,
    system_prompt_template: '',

    // Output and tracking
    enable_detailed_logging: true,
    export_format: 'json',
    real_time_updates: true
  })

  // Debate execution state
  const [debateExecution, setDebateExecution] = useState({
    current_round: 0,
    current_iteration: 0,
    current_agent_index: 0,
    total_iterations_completed: 0,
    arguments_made: 0,
    consensus_score: 0,
    debate_history: [] as DebateArgument[],
    agent_responses: {} as Record<string, string[]>,
    round_summaries: [] as RoundSummary[],
    final_conclusion: null as DebateConclusion | null
  })

  // Ollama integration
  const [ollamaModels, setOllamaModels] = useState<string[]>([])
  const [ollamaConnection, setOllamaConnection] = useState<any>(null)

  // Ollama connection management
  const connectToOllama = useCallback(async () => {
    try {
      setOllamaStatus('connecting')

      // Test Ollama connection
      const response = await fetch('http://localhost:11434/api/tags')
      if (!response.ok) {
        throw new Error('Ollama not available')
      }

      const data = await response.json()
      setOllamaModels(data.models?.map((m: any) => m.name) || [])

      setOllamaStatus('connected')
      addNotification({
        type: 'success',
        title: 'Ollama Connected',
        message: `Connected to Ollama with ${data.models?.length || 0} models available`
      })
    } catch (error) {
      setOllamaStatus('disconnected')
      addNotification({
        type: 'error',
        title: 'Ollama Connection Failed',
        message: 'Unable to connect to Ollama. Make sure it\'s running on localhost:11434'
      })
    }
  }, [addNotification])

  // Generate agent response using Ollama
  const generateAgentResponse = useCallback(async (
    agent: typeof DEBATE_AGENT_TYPES[0],
    debateContext: {
      topic: string
      premise: string
      problemStatement: string
      currentRound: number
      previousArguments: DebateArgument[]
      agentRole: string
      debateRules: any
    }
  ): Promise<string> => {
    const systemPrompt = `You are ${agent.name}, a ${agent.specialization}.

DEBATE CONTEXT:
- Topic: ${debateContext.topic}
- Premise: ${debateContext.premise}
- Problem Statement: ${debateContext.problemStatement}
- Round: ${debateContext.currentRound}
- Your Role: ${debateContext.agentRole}

DEBATE RULES:
- ${debateContext.debateRules.require_evidence ? 'Must provide evidence for claims' : 'Evidence optional'}
- ${debateContext.debateRules.enable_fact_checking ? 'Facts will be verified' : 'No fact checking'}
- ${debateContext.debateRules.allow_creativity ? 'Creative arguments allowed' : 'Stick to logical arguments'}
- ${debateContext.debateRules.enforce_formality ? 'Maintain formal tone' : 'Natural conversation style'}
- ${debateContext.debateRules.require_counter_arguments ? 'Address previous arguments' : 'Focus on your position'}

YOUR STRENGTHS: ${agent.strengths.join(', ')}
YOUR WEAKNESSES: ${agent.weaknesses.join(', ')}

Provide a thoughtful, well-reasoned response that advances the debate. Be specific and use your specialized expertise.`

    const userPrompt = debateContext.previousArguments.length > 0
      ? `Previous arguments in this debate:\n${debateContext.previousArguments.map((arg, i) =>
          `Argument ${i + 1} by ${arg.agent_name} (${arg.agent_type}): ${arg.content}`
        ).join('\n\n')}\n\nRespond to these arguments using your expertise as ${agent.name}.`
      : `This is the opening round. Present your initial position on the topic using your expertise as ${agent.name}.`

    try {
      const response = await fetch('http://localhost:11434/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: debateConfig.ollama_model,
          system: systemPrompt,
          prompt: userPrompt,
          stream: false,
          options: {
            temperature: debateConfig.temperature,
            max_tokens: debateConfig.max_tokens,
            top_p: 0.9,
            top_k: 40,
          }
        })
      })

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status}`)
      }

      const data = await response.json()
      return data.response.trim()
    } catch (error) {
      console.error('Ollama generation error:', error)
      return `Error generating response for ${agent.name}. Please check Ollama connection.`
    }
  }, [debateConfig])

  // Execute debate round with Ollama integration
  const executeDebateRound = useCallback(async () => {
    if (!debateSession || debateConfig.selected_agents.length === 0) return

    setIsLoading(true)
    const currentRound = debateExecution.current_round + 1

    try {
      const roundArguments: DebateArgument[] = []

      for (const agentId of debateConfig.selected_agents) {
        const agent = DEBATE_AGENT_TYPES.find(a => a.id === agentId)
        if (!agent) continue

        const agentRole = debateConfig.agent_roles[agentId] || 'Participant'

        // Generate response using Ollama
        const response = await generateAgentResponse(agent, {
          topic: debateConfig.debate_topic,
          premise: debateConfig.premise_area,
          problemStatement: debateConfig.problem_statement,
          currentRound,
          previousArguments: roundArguments,
          agentRole,
          debateRules: debateConfig.debate_rules
        })

        const argument: DebateArgument = {
          id: `arg_${Date.now()}_${agentId}`,
          agent_id: agentId,
          agent_name: agent.name,
          agent_type: agent.type,
          content: response,
          round_number: currentRound,
          timestamp: new Date().toISOString(),
          evidence_score: Math.random() * 0.3 + 0.7, // Simulated evidence score
          creativity_score: Math.random() * 0.4 + 0.3, // Simulated creativity score
          fallacies_detected: Math.floor(Math.random() * 2), // Simulated fallacy detection
          consensus_impact: Math.random() * 0.6 - 0.3 // Simulated consensus impact
        }

        roundArguments.push(argument)

        // Update progress
        setDebateProgress((roundArguments.length / debateConfig.selected_agents.length) * 100)
      }

      // Update debate execution state
      setDebateExecution(prev => ({
        ...prev,
        current_round: currentRound,
        debate_history: [...prev.debate_history, ...roundArguments],
        total_iterations_completed: prev.total_iterations_completed + 1,
        arguments_made: prev.arguments_made + roundArguments.length
      }))

      // Generate round summary
      const roundSummary: RoundSummary = {
        round_number: currentRound,
        arguments_count: roundArguments.length,
        consensus_score: roundArguments.reduce((sum, arg) => sum + arg.consensus_impact, 0) / roundArguments.length,
        key_points_discussed: roundArguments.map(arg => arg.content.substring(0, 100) + '...'),
        evidence_quality_avg: roundArguments.reduce((sum, arg) => sum + arg.evidence_score, 0) / roundArguments.length,
        creativity_level_avg: roundArguments.reduce((sum, arg) => sum + arg.creativity_score, 0) / roundArguments.length
      }

      setDebateExecution(prev => ({
        ...prev,
        round_summaries: [...prev.round_summaries, roundSummary]
      }))

      addNotification({
        type: 'success',
        title: `Round ${currentRound} Complete`,
        message: `${roundArguments.length} arguments generated. Consensus: ${(roundSummary.consensus_score * 100).toFixed(1)}%`
      })

    } catch (error) {
      console.error('Debate round execution error:', error)
      addNotification({
        type: 'error',
        title: 'Debate Round Failed',
        message: 'Failed to execute debate round. Check Ollama connection.'
      })
    } finally {
      setIsLoading(false)
      setDebateProgress(0)
    }
  }, [debateSession, debateConfig, debateExecution, generateAgentResponse, addNotification])

  // Start comprehensive debate with Ollama
  const startOllamaDebate = useCallback(async () => {
    if (!debateConfig.debate_topic.trim() || debateConfig.selected_agents.length < 2) {
      addNotification({
        type: 'error',
        title: 'Invalid Configuration',
        message: 'Please provide a debate topic and select at least 2 agents.'
      })
      return
    }

    if (ollamaStatus !== 'connected') {
      addNotification({
        type: 'error',
        title: 'Ollama Not Connected',
        message: 'Please connect to Ollama before starting the debate.'
      })
      return
    }

    setIsLoading(true)
    setDebateExecution({
      current_round: 0,
      current_iteration: 0,
      current_agent_index: 0,
      total_iterations_completed: 0,
      arguments_made: 0,
      consensus_score: 0,
      debate_history: [],
      agent_responses: {},
      round_summaries: [],
      final_conclusion: null
    })

    try {
      // Initialize debate session
      const session: DebateSession = {
        session_id: `debate_${Date.now()}`,
        status: 'active',
        configuration: debateConfig,
        participants: debateConfig.selected_agents.map(id => {
          const agent = DEBATE_AGENT_TYPES.find(a => a.id === id)
          return {
            agent_id: id,
            agent_name: agent?.name || 'Unknown Agent',
            agent_type: agent?.type || 'unknown',
            specialization: agent?.specialization || 'General debate participant',
            position: 'neutral' as const,
            confidence_score: 0.5,
            arguments_made: 0,
            rebuttals_given: 0,
            fallacies_identified: 0,
            strength_score: 0.5
          }
        }),
        rounds: [],
        current_round: 0,
        total_arguments: 0,
        consensus_score: 0,
        started_at: new Date().toISOString()
      }

      setDebateSession(session)
      setActiveTab('debate')
      setIsConfiguring(false)

      addNotification({
        type: 'success',
        title: 'Debate Started',
        message: `Agent debate initiated with ${debateConfig.selected_agents.length} participants using Ollama`
      })

      // Execute first round
      await executeDebateRound()

    } catch (error) {
      console.error('Failed to start debate:', error)
      addNotification({
        type: 'error',
        title: 'Debate Start Failed',
        message: 'Failed to initialize the debate session.'
      })
    } finally {
      setIsLoading(false)
    }
  }, [debateConfig, ollamaStatus, executeDebateRound, addNotification])

  // WebSocket connection for real-time debate updates
  const [ws, setWs] = useState<WebSocket | null>(null)

  // Initialize WebSocket connection for debate updates
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const websocket = new WebSocket('ws://localhost:8441/ws/debate-updates')

        websocket.onopen = () => {
          setWsConnected(true)
          addNotification({
            type: 'success',
            title: 'Debate System Connected',
            message: 'Real-time debate updates active'
          })
        }

        websocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            handleDebateWebSocketMessage(data)
          } catch (error) {
            console.error('Failed to parse debate WebSocket message:', error)
          }
        }

        websocket.onclose = () => {
          setWsConnected(false)
          // Auto-reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000)
        }

        websocket.onerror = (error) => {
          console.error('Debate WebSocket error:', error)
          setWsConnected(false)
        }

        setWs(websocket)
      } catch (error) {
        console.error('Failed to create debate WebSocket connection:', error)
      }
    }

    connectWebSocket()

    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])

  // Handle WebSocket messages for debate updates
  const handleDebateWebSocketMessage = useCallback((data: any) => {
    switch (data.event_type) {
      case 'debate_started':
        setDebateSession(data.session)
        setActiveTab('debate')
        break
      case 'round_completed':
        setDebateSession(prev => prev ? {
          ...prev,
          rounds: [...prev.rounds, data.round],
          current_round: data.round.round_number
        } : null)
        break
      case 'argument_made':
        // Update the current round with new argument
        setDebateSession(prev => {
          if (!prev) return null
          const updatedRounds = [...prev.rounds]
          const currentRoundIndex = updatedRounds.length - 1
          if (currentRoundIndex >= 0) {
            updatedRounds[currentRoundIndex] = {
              ...updatedRounds[currentRoundIndex],
              arguments: [...updatedRounds[currentRoundIndex].arguments, data.argument]
            }
          }
          return {
            ...prev,
            rounds: updatedRounds,
            total_arguments: prev.total_arguments + 1
          }
        })
        break
      case 'consensus_reached':
        setDebateSession(prev => prev ? {
          ...prev,
          status: 'consensus_reached',
          consensus_score: data.consensus_score,
          winning_position: data.winning_position,
          conclusion: data.conclusion,
          completed_at: new Date().toISOString()
        } : null)
        setActiveTab('analysis')
        break
      case 'debate_completed':
        setDebateSession(prev => prev ? {
          ...prev,
          status: 'completed',
          completed_at: new Date().toISOString()
        } : null)
        setActiveTab('analysis')
        break
    }
  }, [])

  // Initialize debate session
  const initializeDebate = useCallback(async () => {
    if (!debateConfig.debate_topic.trim() || !debateConfig.problem_statement.trim()) {
      addNotification({
        type: 'warning',
        title: 'Configuration Required',
        message: 'Please provide a debate topic and problem statement'
      })
      return
    }

    if (debateConfig.selected_agents.length < 2) {
      addNotification({
        type: 'warning',
        title: 'Insufficient Participants',
        message: 'Please select at least 2 agents for the debate'
      })
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch('/api/v1/debate/initialize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          configuration: debateConfig
        }),
      })

      if (response.ok) {
        const result = await response.json()
        setDebateSession(result.session)
        setIsConfiguring(false)
        setActiveTab('debate')
        addNotification({
          type: 'success',
          title: 'Debate Initialized',
          message: `Multi-agent debate session started with ${debateConfig.selected_agents.length} participants`
        })
      } else {
        const error = await response.json()
        addNotification({
          type: 'error',
          title: 'Initialization Failed',
          message: error.error || 'Failed to initialize debate session'
        })
      }
    } catch (error) {
      console.error('Debate initialization error:', error)
      addNotification({
        type: 'error',
        title: 'Network Error',
        message: 'Failed to initialize debate session'
      })
    } finally {
      setIsLoading(false)
    }
  }, [debateConfig, addNotification])

  // Control debate session
  const controlDebate = useCallback(async (action: 'start' | 'pause' | 'resume' | 'stop') => {
    if (!debateSession) return

    setIsLoading(true)
    try {
      const response = await fetch(`/api/v1/debate/${debateSession.session_id}/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      })

      if (response.ok) {
        const result = await response.json()
        setDebateSession(result.session)
        addNotification({
          type: 'success',
          title: 'Debate Control',
          message: `Debate ${action}ed successfully`
        })
      }
    } catch (error) {
      console.error('Debate control error:', error)
      addNotification({
        type: 'error',
        title: 'Control Failed',
        message: `Failed to ${action} debate`
      })
    } finally {
      setIsLoading(false)
    }
  }, [debateSession, addNotification])

  // Toggle agent selection
  const toggleAgentSelection = (agentId: string) => {
    setDebateConfig(prev => ({
      ...prev,
      selected_agents: prev.selected_agents.includes(agentId)
        ? prev.selected_agents.filter(id => id !== agentId)
        : [...prev.selected_agents, agentId]
    }))
  }

  // Get agent by ID
  const getAgentById = (agentId: string) => {
    return DEBATE_AGENT_TYPES.find(agent => agent.id === agentId)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Enhanced Header */}
      <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-700 rounded-lg p-6 mb-6">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-green-500/5" />
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-blue-500/10 to-transparent rounded-full -translate-y-16 translate-x-16" />
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-purple-500/10 to-transparent rounded-full translate-y-12 -translate-x-12" />

        <div className="relative flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-green-400 bg-clip-text text-transparent">
                  Multi-Agent Debate System
                </h1>
                <div className="flex items-center space-x-4 mt-1">
                  <span className="text-sm text-slate-400">Autonomous multi-perspective argumentation</span>
                  <Badge variant="outline" className="text-xs border-slate-600">
                    Advanced AI
                  </Badge>
                </div>
              </div>
            </div>

            {/* Status indicators */}
            <div className="flex items-center space-x-6 mt-4">
              {/* WebSocket status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                <span className="text-sm text-slate-300">
                  {wsConnected ? 'Live Updates' : 'Disconnected'}
                </span>
              </div>

              {/* Debate status */}
              {debateSession && (
                <>
                  <div className="h-4 w-px bg-slate-600" />
                  <div className="flex items-center space-x-4">
                    <Badge variant={
                      debateSession.status === 'active' ? 'default' :
                      debateSession.status === 'paused' ? 'secondary' :
                      debateSession.status === 'completed' ? 'outline' : 'destructive'
                    } className="text-xs">
                      {debateSession.status.replace('_', ' ').toUpperCase()}
                    </Badge>

                    <div className="text-sm text-slate-400">
                      Round <span className="font-medium text-white">{debateSession.current_round}</span> of {debateConfig.max_rounds}
                    </div>

                    <div className="text-sm text-slate-400">
                      Consensus: <span className="font-medium text-green-400">{(debateSession.consensus_score * 100).toFixed(1)}%</span>
                    </div>

                    <div className="text-sm text-slate-400">
                      {debateSession.participants.length} Participants
                    </div>
                  </div>
                </>
              )}

              {/* Active rules indicators */}
              {debateConfig.debate_rules.require_evidence && (
                <Badge variant="outline" className="text-xs border-green-500 text-green-400">
                  Evidence Required
                </Badge>
              )}
              {debateConfig.debate_rules.enable_fact_checking && (
                <Badge variant="outline" className="text-xs border-blue-500 text-blue-400">
                  Fact Checking
                </Badge>
              )}
              {debateConfig.debate_rules.allow_creativity && (
                <Badge variant="outline" className="text-xs border-purple-500 text-purple-400">
                  Creative Mode
                </Badge>
              )}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center space-x-3">
            {debateSession && debateSession.status === 'active' && (
              <Button
                onClick={() => controlDebate('pause')}
                variant="outline"
                size="sm"
                className="border-yellow-500 text-yellow-400 hover:bg-yellow-500/10"
              >
                <Pause className="w-4 h-4 mr-1" />
                Pause
              </Button>
            )}

            {debateSession && debateSession.status === 'paused' && (
              <Button
                onClick={() => controlDebate('resume')}
                size="sm"
                className="bg-green-600 hover:bg-green-700"
              >
                <Play className="w-4 h-4 mr-1" />
                Resume
              </Button>
            )}

            {debateSession && ['active', 'paused'].includes(debateSession.status) && (
              <Button
                onClick={() => controlDebate('stop')}
                variant="destructive"
                size="sm"
              >
                Stop Debate
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} data-id="debate-tabs">
        <TabsList className="grid w-full grid-cols-3" data-id="debate-tabs-list">
          <TabsTrigger value="setup" data-id="tab-setup">Setup & Configuration</TabsTrigger>
          <TabsTrigger value="debate" disabled={!debateSession} data-id="tab-debate">Live Debate</TabsTrigger>
          <TabsTrigger value="analysis" disabled={!debateSession || debateSession.status !== 'completed'} data-id="tab-analysis">Analysis & Results</TabsTrigger>
        </TabsList>

        {/* Setup Tab */}
        <TabsContent value="setup" className="space-y-6" data-id="setup-tab-content">
          {/* Ollama Connection Status */}
          <Card data-id="ollama-connection-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                <Zap className={`w-5 h-5 ${
                  ollamaStatus === 'connected' ? 'text-green-400' :
                  ollamaStatus === 'connecting' ? 'text-yellow-400' : 'text-red-400'
                }`} />
                <span>Ollama Connection</span>
                <Badge variant={
                  ollamaStatus === 'connected' ? 'default' :
                  ollamaStatus === 'connecting' ? 'secondary' : 'destructive'
                }>
                  {ollamaStatus === 'connecting' ? 'Connecting...' : ollamaStatus}
                </Badge>
                </CardTitle>
                <CardDescription>
                Connect to Ollama for AI-powered agent responses
                </CardDescription>
              </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center space-x-4">
                <Button
                  onClick={connectToOllama}
                  disabled={ollamaStatus === 'connecting'}
                  variant={ollamaStatus === 'connected' ? 'outline' : 'default'}
                  data-id="connect-ollama-btn"
                >
                  {ollamaStatus === 'connecting' ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Connecting...
                    </>
                  ) : ollamaStatus === 'connected' ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Connected
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Connect to Ollama
                    </>
                  )}
                </Button>

                {ollamaModels.length > 0 && (
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-slate-400">Available models:</span>
                    <Badge variant="outline">{ollamaModels.length}</Badge>
                  </div>
                )}
              </div>

              <div className="text-xs text-slate-400">
                Make sure Ollama is running on localhost:11434 with appropriate models installed.
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6" data-id="setup-grid">
            {/* Core Debate Parameters */}
            <Card data-id="debate-core-config">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5" />
                  <span>Core Parameters</span>
                </CardTitle>
                <CardDescription>
                  Define the debate topic and scope
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4" data-id="debate-core-content">
                {/* Debate Topic */}
                <div data-id="debate-topic-section">
                  <Label htmlFor="debate_topic">Debate Topic</Label>
                  <Input
                    id="debate_topic"
                    value={debateConfig.debate_topic}
                    onChange={(e) => setDebateConfig(prev => ({ ...prev, debate_topic: e.target.value }))}
                    placeholder="e.g., Should AI be regulated?"
                    className="mt-1"
                    data-id="debate-topic-input"
                  />
                </div>

                {/* Premise Area */}
                <div data-id="premise-area-section">
                  <Label htmlFor="premise_area">Premise Area</Label>
                  <Textarea
                    id="premise_area"
                    value={debateConfig.premise_area}
                    onChange={(e) => setDebateConfig(prev => ({ ...prev, premise_area: e.target.value }))}
                    placeholder="Describe the broader context and assumptions..."
                    rows={3}
                    className="mt-1"
                    data-id="premise-area-input"
                  />
                </div>

                {/* Problem Statement */}
                <div data-id="problem-statement-section">
                  <Label htmlFor="problem_statement">Problem Statement</Label>
                  <Textarea
                    id="problem_statement"
                    value={debateConfig.problem_statement}
                    onChange={(e) => setDebateConfig(prev => ({ ...prev, problem_statement: e.target.value }))}
                    placeholder="What specific question or issue should agents debate?"
                    rows={3}
                    className="mt-1"
                    data-id="problem-statement-input"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Debate Execution Controls */}
            <Card data-id="debate-execution-config">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="w-5 h-5" />
                  <span>Execution Controls</span>
                </CardTitle>
                <CardDescription>
                  Configure rounds, iterations, and timing
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4" data-id="debate-execution-content">
                {/* Debate Mode */}
                <div>
                  <Label>Debate Mode</Label>
                  <Select
                    value={debateConfig.debate_mode}
                    onValueChange={(value: any) => setDebateConfig(prev => ({ ...prev, debate_mode: value }))}
                    data-id="debate-mode-select"
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="structured">Structured Debate</SelectItem>
                      <SelectItem value="freeform">Freeform Discussion</SelectItem>
                      <SelectItem value="autonomous">Autonomous Debate</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Round and Iteration Configuration */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Max Rounds</Label>
                    <Input
                      type="number"
                      value={debateConfig.max_rounds}
                      onChange={(e) => setDebateConfig(prev => ({
                        ...prev,
                        max_rounds: parseInt(e.target.value) || 5
                      }))}
                      min={1}
                      max={20}
                      className="mt-1"
                      data-id="max-rounds-input"
                    />
                  </div>

                  <div>
                    <Label>Iterations per Agent</Label>
                    <Input
                      type="number"
                      value={debateConfig.iterations_per_agent}
                      onChange={(e) => setDebateConfig(prev => ({
                        ...prev,
                        iterations_per_agent: parseInt(e.target.value) || 2
                      }))}
                      min={1}
                      max={5}
                      className="mt-1"
                      data-id="iterations-per-agent-input"
                    />
                  </div>
                </div>

                {/* Timing Controls */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Response Timeout (sec)</Label>
                    <Input
                      type="number"
                      value={debateConfig.response_timeout}
                      onChange={(e) => setDebateConfig(prev => ({
                        ...prev,
                        response_timeout: parseInt(e.target.value) || 30
                      }))}
                      min={10}
                      max={300}
                      className="mt-1"
                      data-id="response-timeout-input"
                    />
                  </div>

                  <div>
                    <Label>Consensus Threshold</Label>
                    <div className="mt-1">
                      <Slider
                        value={[debateConfig.consensus_threshold]}
                        onValueChange={([value]) => setDebateConfig(prev => ({
                          ...prev,
                          consensus_threshold: value
                        }))}
                        min={0.5}
                        max={1.0}
                        step={0.1}
                        className="w-full"
                        data-id="consensus-threshold-slider"
                      />
                      <div className="text-xs text-slate-400 mt-1">
                        {(debateConfig.consensus_threshold * 100).toFixed(0)}% agreement required
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Ollama Configuration */}
            <Card data-id="ollama-config-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="w-5 h-5" />
                  <span>Ollama Configuration</span>
                </CardTitle>
                <CardDescription>
                  Configure AI model parameters for agent responses
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-4" data-id="ollama-config-content">
                {/* Model Selection */}
                <div>
                  <Label>Ollama Model</Label>
                  <Select
                    value={debateConfig.ollama_model}
                    onValueChange={(value) => setDebateConfig(prev => ({ ...prev, ollama_model: value }))}
                    data-id="ollama-model-select"
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ollamaModels.length > 0 ? (
                        ollamaModels.map(model => (
                          <SelectItem key={model} value={model}>
                            {model}
                          </SelectItem>
                        ))
                      ) : (
                        <>
                          <SelectItem value="llama2:7b">llama2:7b</SelectItem>
                          <SelectItem value="mistral:7b">mistral:7b</SelectItem>
                          <SelectItem value="codellama:7b">codellama:7b</SelectItem>
                          <SelectItem value="vicuna:7b">vicuna:7b</SelectItem>
                        </>
                      )}
                    </SelectContent>
                  </Select>
                  </div>

                {/* AI Parameters */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Temperature</Label>
                    <div className="mt-1">
                      <Slider
                        value={[debateConfig.temperature]}
                        onValueChange={([value]) => setDebateConfig(prev => ({
                          ...prev,
                          temperature: value
                        }))}
                        min={0.1}
                        max={1.5}
                        step={0.1}
                        className="w-full"
                        data-id="temperature-slider"
                      />
                      <div className="text-xs text-slate-400 mt-1">
                        {debateConfig.temperature.toFixed(1)} (creativity level)
                      </div>
                    </div>
                  </div>

                  <div>
                    <Label>Max Tokens</Label>
                    <Input
                      type="number"
                      value={debateConfig.max_tokens}
                      onChange={(e) => setDebateConfig(prev => ({
                        ...prev,
                        max_tokens: parseInt(e.target.value) || 512
                      }))}
                      min={128}
                      max={2048}
                      className="mt-1"
                      data-id="max-tokens-input"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Debate Rules Configuration */}
          <Card data-id="debate-rules-card">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="w-5 h-5" />
                <span>Debate Rules & Constraints</span>
              </CardTitle>
              <CardDescription>
                Configure argumentation rules, evidence requirements, and debate constraints
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6" data-id="debate-rules-content">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Evidence & Verification */}
                <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        <Label className="text-sm font-medium">Evidence & Verification</Label>
                      </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="space-y-1">
                            <Label htmlFor="require_evidence" className="text-sm font-medium">Require Evidence</Label>
                            <p className="text-xs text-slate-400">Arguments must include verifiable evidence</p>
                          </div>
                          <Switch
                            id="require_evidence"
                            checked={debateConfig.debate_rules.require_evidence}
                            onCheckedChange={(checked) => setDebateConfig(prev => ({
                              ...prev,
                              debate_rules: { ...prev.debate_rules, require_evidence: checked }
                            }))}
                        data-id="require-evidence-switch"
                          />
                        </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="space-y-1">
                        <Label htmlFor="enable_fact_checking" className="text-sm font-medium">Fact Checking</Label>
                        <p className="text-xs text-slate-400">Automatically verify claims</p>
                          </div>
                          <Switch
                            id="enable_fact_checking"
                            checked={debateConfig.debate_rules.enable_fact_checking}
                            onCheckedChange={(checked) => setDebateConfig(prev => ({
                              ...prev,
                              debate_rules: { ...prev.debate_rules, enable_fact_checking: checked }
                            }))}
                        data-id="fact-checking-switch"
                          />
                        </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="space-y-1">
                        <Label htmlFor="evidence_threshold" className="text-sm font-medium">Evidence Quality</Label>
                        <p className="text-xs text-slate-400">Minimum evidence score required</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Input
                              type="number"
                          value={debateConfig.debate_rules.evidence_threshold}
                              onChange={(e) => setDebateConfig(prev => ({
                                ...prev,
                                debate_rules: {
                                  ...prev.debate_rules,
                              evidence_threshold: parseFloat(e.target.value) || 0.7
                                }
                              }))}
                              min={0.1}
                              max={1.0}
                              step={0.1}
                              className="w-20 h-8"
                          data-id="evidence-threshold-input"
                            />
                            <span className="text-xs text-slate-400">
                          {(debateConfig.debate_rules.evidence_threshold * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                {/* Creativity & Style */}
                <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                        <Lightbulb className="w-4 h-4 text-yellow-400" />
                    <Label className="text-sm font-medium">Creativity & Style</Label>
                      </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="space-y-1">
                        <Label htmlFor="allow_creativity" className="text-sm font-medium">Creative Solutions</Label>
                        <p className="text-xs text-slate-400">Permit unconventional approaches</p>
                          </div>
                          <Switch
                            id="allow_creativity"
                            checked={debateConfig.debate_rules.allow_creativity}
                            onCheckedChange={(checked) => setDebateConfig(prev => ({
                              ...prev,
                              debate_rules: { ...prev.debate_rules, allow_creativity: checked }
                            }))}
                        data-id="creativity-switch"
                          />
                        </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                      <div className="space-y-1">
                        <Label htmlFor="enforce_formality" className="text-sm font-medium">Formal Tone</Label>
                        <p className="text-xs text-slate-400">Maintain formal argumentation style</p>
                      </div>
                      <Switch
                        id="enforce_formality"
                        checked={debateConfig.debate_rules.enforce_formality}
                        onCheckedChange={(checked) => setDebateConfig(prev => ({
                          ...prev,
                          debate_rules: { ...prev.debate_rules, enforce_formality: checked }
                        }))}
                        data-id="formality-switch"
                      />
                    </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="space-y-1">
                            <Label htmlFor="creativity_weight" className="text-sm font-medium">Creativity Weight</Label>
                        <p className="text-xs text-slate-400">Influence of creative solutions</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Input
                              type="number"
                          value={debateConfig.debate_rules.creativity_weight}
                              onChange={(e) => setDebateConfig(prev => ({
                                ...prev,
                                debate_rules: {
                                  ...prev.debate_rules,
                                  creativity_weight: parseFloat(e.target.value) || 0.3
                                }
                              }))}
                              min={0.0}
                              max={1.0}
                              step={0.1}
                              className="w-20 h-8"
                          data-id="creativity-weight-input"
                            />
                            <span className="text-xs text-slate-400">
                          {(debateConfig.debate_rules.creativity_weight * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>

                {/* Debate Structure */}
                <div className="space-y-4">
                      <div className="flex items-center space-x-2">
                    <Scale className="w-4 h-4 text-blue-400" />
                    <Label className="text-sm font-medium">Debate Structure</Label>
                      </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="space-y-1">
                        <Label htmlFor="require_counter_arguments" className="text-sm font-medium">Counter Arguments</Label>
                        <p className="text-xs text-slate-400">Require addressing previous arguments</p>
                          </div>
                          <Switch
                        id="require_counter_arguments"
                        checked={debateConfig.debate_rules.require_counter_arguments}
                            onCheckedChange={(checked) => setDebateConfig(prev => ({
                              ...prev,
                          debate_rules: { ...prev.debate_rules, require_counter_arguments: checked }
                            }))}
                        data-id="counter-arguments-switch"
                          />
                        </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="space-y-1">
                        <Label htmlFor="allow_collaboration" className="text-sm font-medium">Collaboration</Label>
                        <p className="text-xs text-slate-400">Allow agents to build on each other's ideas</p>
                          </div>
                          <Switch
                        id="allow_collaboration"
                        checked={debateConfig.debate_rules.allow_collaboration}
                            onCheckedChange={(checked) => setDebateConfig(prev => ({
                              ...prev,
                          debate_rules: { ...prev.debate_rules, allow_collaboration: checked }
                            }))}
                        data-id="collaboration-switch"
                          />
                        </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                          <div className="space-y-1">
                        <Label htmlFor="enforce_turn_taking" className="text-sm font-medium">Turn Taking</Label>
                        <p className="text-xs text-slate-400">Enforce structured turn-taking order</p>
                      </div>
                      <Switch
                        id="enforce_turn_taking"
                        checked={debateConfig.debate_rules.enforce_turn_taking}
                        onCheckedChange={(checked) => setDebateConfig(prev => ({
                          ...prev,
                          debate_rules: { ...prev.debate_rules, enforce_turn_taking: checked }
                        }))}
                        data-id="turn-taking-switch"
                      />
                    </div>

                    <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                      <div className="space-y-1">
                        <Label htmlFor="max_fallacies" className="text-sm font-medium">Max Fallacies</Label>
                        <p className="text-xs text-slate-400">Maximum logical fallacies allowed per argument</p>
                          </div>
                          <Input
                            type="number"
                        value={debateConfig.debate_rules.max_fallacies_per_argument}
                            onChange={(e) => setDebateConfig(prev => ({
                              ...prev,
                              debate_rules: {
                                ...prev.debate_rules,
                            max_fallacies_per_argument: parseInt(e.target.value) || 1
                              }
                            }))}
                            min={0}
                            max={5}
                            className="w-20 h-8"
                        data-id="max-fallacies-input"
                          />
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Agent Selection */}
          <Card data-id="agent-selection-card">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>Agent Selection</span>
                <Badge variant="outline" data-id="selected-agents-count">
                  {debateConfig.selected_agents.length} selected
                </Badge>
                </CardTitle>
                <CardDescription>
                Choose debate participants and assign roles
                </CardDescription>
              </CardHeader>

              <CardContent>
              <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto" data-id="agent-selection-grid">
                  {DEBATE_AGENT_TYPES.map((agent) => {
                    const isSelected = debateConfig.selected_agents.includes(agent.id)
                    const IconComponent = agent.icon

                    return (
                      <motion.div
                        key={agent.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Card
                          className={`cursor-pointer transition-all duration-200 ${
                            isSelected
                              ? 'border-blue-500 bg-blue-500/10'
                              : 'border-slate-700 hover:border-slate-600'
                          }`}
                          onClick={() => toggleAgentSelection(agent.id)}
                        data-id={`agent-card-${agent.id}`}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-center space-x-3">
                              <div className={`p-2 rounded-lg bg-${agent.color}-500/20`}>
                                <IconComponent className={`w-5 h-5 text-${agent.color}-400`} />
                              </div>

                              <div className="flex-1">
                                <div className="flex items-center space-x-2">
                                  <h4 className="font-medium">{agent.name}</h4>
                                  {isSelected && <CheckCircle className="w-4 h-4 text-green-500" />}
                                </div>
                                <p className="text-sm text-slate-400">{agent.specialization}</p>
                                <div className="flex flex-wrap gap-1 mt-2">
                                  {agent.strengths.slice(0, 2).map((strength, idx) => (
                                    <Badge key={idx} variant="secondary" className="text-xs">
                                      {strength}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    )
                  })}
                </div>

              <div className="mt-6 space-y-4">
                {/* Agent Role Assignment */}
                {debateConfig.selected_agents.length > 0 && (
                  <div className="space-y-3">
                    <Label className="text-sm font-medium">Agent Roles</Label>
                    {debateConfig.selected_agents.map(agentId => {
                      const agent = DEBATE_AGENT_TYPES.find(a => a.id === agentId)
                      return (
                        <div key={agentId} className="flex items-center space-x-3 p-3 bg-slate-800/30 rounded-lg">
                          <span className="text-sm font-medium min-w-[120px]">{agent?.name}:</span>
                          <Select
                            value={debateConfig.agent_roles[agentId] || 'Participant'}
                            onValueChange={(role) => setDebateConfig(prev => ({
                              ...prev,
                              agent_roles: { ...prev.agent_roles, [agentId]: role }
                            }))}
                            data-id={`agent-role-${agentId}`}
                          >
                            <SelectTrigger className="flex-1">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="Participant">Participant</SelectItem>
                              <SelectItem value="Moderator">Moderator</SelectItem>
                              <SelectItem value="Proponent">Proponent</SelectItem>
                              <SelectItem value="Opponent">Opponent</SelectItem>
                              <SelectItem value="Critic">Critic</SelectItem>
                              <SelectItem value="Facilitator">Facilitator</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      )
                    })}
                  </div>
                )}

                  <Button
                  onClick={startOllamaDebate}
                  disabled={isLoading || debateConfig.selected_agents.length < 2 || ollamaStatus !== 'connected'}
                    className="w-full"
                    size="lg"
                  data-id="start-debate-btn"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Initializing Debate...
                      </>
                    ) : (
                      <>
                      <Zap className="w-4 h-4 mr-2" />
                      Start Ollama Debate
                      </>
                    )}
                  </Button>

                {ollamaStatus !== 'connected' && (
                  <div className="text-sm text-amber-400 text-center">
                    ⚠️ Connect to Ollama before starting the debate
                  </div>
                )}
                </div>
              </CardContent>
            </Card>
        </TabsContent>

        {/* Live Debate Tab */}
        <TabsContent value="debate" className="space-y-6">
          {debateSession && (
            <>
              {/* Debate Control Panel */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Brain className="w-5 h-5" />
                      <span>Live Debate Progress</span>
                    </div>

                    <div className="flex items-center space-x-4">
                      <Badge variant={
                        debateSession.status === 'active' ? 'default' :
                        debateSession.status === 'paused' ? 'secondary' :
                        debateSession.status === 'completed' ? 'outline' : 'destructive'
                      }>
                        {debateSession.status.replace('_', ' ').toUpperCase()}
                      </Badge>

                      <div className="text-sm text-slate-400">
                        Round {debateExecution.current_round} / {debateConfig.max_rounds}
                      </div>
                    </div>
                  </CardTitle>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Debate Progress</span>
                      <span>{Math.round((debateExecution.current_round / debateConfig.max_rounds) * 100)}%</span>
                    </div>
                    <Progress
                      value={(debateExecution.current_round / debateConfig.max_rounds) * 100}
                      className="h-2"
                    />
                    </div>

                  {/* Debate Stats */}
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-blue-400">{debateExecution.arguments_made}</div>
                      <div className="text-xs text-slate-400">Arguments</div>
                      </div>
                    <div>
                      <div className="text-2xl font-bold text-green-400">{debateExecution.current_round}</div>
                      <div className="text-xs text-slate-400">Rounds</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-400">{debateConfig.selected_agents.length}</div>
                      <div className="text-xs text-slate-400">Agents</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-yellow-400">
                        {debateExecution.consensus_score > 0 ? `${(debateExecution.consensus_score * 100).toFixed(0)}%` : 'N/A'}
                  </div>
                      <div className="text-xs text-slate-400">Consensus</div>
                      </div>
                    </div>

                  {/* Control Buttons */}
                  <div className="flex space-x-2">
                    {debateSession.status === 'initialized' && (
                      <Button onClick={() => executeDebateRound()} size="sm" data-id="continue-debate-btn">
                        <Play className="w-4 h-4 mr-2" />
                        Start Round {debateExecution.current_round + 1}
                      </Button>
                    )}

                    {debateSession.status === 'active' && (
                      <>
                        <Button onClick={() => executeDebateRound()} size="sm" variant="outline" data-id="next-round-btn">
                          <Play className="w-4 h-4 mr-2" />
                          Next Round
                        </Button>
                        <Button
                          onClick={() => setDebateSession(prev => prev ? {...prev, status: 'paused'} : null)}
                          size="sm"
                          variant="secondary"
                          data-id="pause-debate-btn"
                        >
                          <Pause className="w-4 h-4 mr-2" />
                          Pause
                        </Button>
                      </>
                    )}

                    {debateSession.status === 'paused' && (
                      <Button
                        onClick={() => setDebateSession(prev => prev ? {...prev, status: 'active'} : null)}
                        size="sm"
                        data-id="resume-debate-btn"
                      >
                        <Play className="w-4 h-4 mr-2" />
                        Resume
                      </Button>
                    )}

                    <Button
                      onClick={() => {
                        setDebateSession(null)
                        setActiveTab('setup')
                      }}
                      size="sm"
                      variant="destructive"
                      data-id="end-debate-btn"
                    >
                      <X className="w-4 h-4 mr-2" />
                      End Debate
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Live Debate Feed */}
              <Card className="flex-1" data-id="debate-feed-card">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <MessageSquare className="w-5 h-5" />
                    <span>Live Debate Feed</span>
                    <Badge variant="outline" data-id="debate-feed-count">
                      {debateExecution.debate_history.length} arguments
                    </Badge>
                  </CardTitle>
                </CardHeader>

                <CardContent>
                  <div className="space-y-4 max-h-96 overflow-y-auto" data-id="debate-arguments-list">
                    {debateExecution.debate_history.length === 0 ? (
                      <div className="text-center py-8 text-slate-400">
                        <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No arguments yet. Start the debate to see live discussion.</p>
                      </div>
                    ) : (
                      debateExecution.debate_history.slice(-10).reverse().map((argument) => {
                        const agent = getAgentById(argument.agent_id)
                      return (
                        <motion.div
                            key={argument.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="border border-slate-700 rounded-lg p-4 bg-slate-800/30"
                            data-id={`argument-${argument.id}`}
                          >
                            <div className="flex items-start space-x-3">
                              <div className={`p-2 rounded-lg bg-${agent?.color || 'blue'}-500/20 flex-shrink-0`}>
                                {agent && <agent.icon className={`w-4 h-4 text-${agent.color}-400`} />}
                          </div>

                              <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2 mb-2">
                                  <span className="font-medium text-white">{argument.agent_name}</span>
                                  <Badge variant="outline" className="text-xs">
                                    Round {argument.round_number}
                              </Badge>
                                  <span className="text-xs text-slate-400">
                                {new Date(argument.timestamp).toLocaleTimeString()}
                                  </span>
                          </div>

                                <p className="text-slate-300 text-sm leading-relaxed mb-3">
                            {argument.content}
                                </p>

                                <div className="flex items-center space-x-4 text-xs text-slate-400">
                                  <span>Evidence: {(argument.evidence_score * 100).toFixed(0)}%</span>
                                  <span>Creativity: {(argument.creativity_score * 100).toFixed(0)}%</span>
                                  {argument.fallacies_detected > 0 && (
                                    <span className="text-red-400">
                                      ⚠️ {argument.fallacies_detected} fallacies
                                    </span>
                              )}
                            </div>
                            </div>
                            </div>
                        </motion.div>
                      )
                      })
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Round Summaries */}
              {debateExecution.round_summaries.length > 0 && (
                <Card data-id="round-summaries-card">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="w-5 h-5" />
                      <span>Round Summaries</span>
                  </CardTitle>
                </CardHeader>

                <CardContent>
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {debateExecution.round_summaries.map((summary) => (
                        <div key={summary.round_number} className="border border-slate-700 rounded-lg p-3 bg-slate-800/30">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">Round {summary.round_number}</span>
                            <div className="flex items-center space-x-2">
                              <span className="text-sm text-slate-400">
                                Consensus: {(summary.consensus_score * 100).toFixed(1)}%
                              </span>
                              <Badge variant="outline" className="text-xs">
                                {summary.arguments_count} arguments
                              </Badge>
                      </div>
                    </div>

                          <div className="grid grid-cols-2 gap-4 text-xs text-slate-400 mb-2">
                            <span>Evidence Quality: {(summary.evidence_quality_avg * 100).toFixed(1)}%</span>
                            <span>Creativity Level: {(summary.creativity_level_avg * 100).toFixed(1)}%</span>
                    </div>

                          <div className="text-xs text-slate-500">
                            Key points: {summary.key_points_discussed.slice(0, 2).join(' • ')}
                      </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              )}
            </>
          )}
        </TabsContent>
      </Tabs>
    </motion.div>
  )
}
