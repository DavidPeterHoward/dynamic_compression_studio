'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { motion } from 'framer-motion'
import {
    Eye,
    EyeOff,
    Network,
    Pause,
    Play,
    RotateCcw,
    ZoomIn,
    ZoomOut
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

interface AgentNode {
  id: string
  name: string
  type: string
  status: 'active' | 'inactive' | 'learning' | 'error'
  x: number
  y: number
  connections: string[]
  metrics: {
    activity: number
    collaboration: number
    performance: number
  }
}

interface AgentConnection {
  from: string
  to: string
  strength: number
  type: 'collaboration' | 'communication' | 'dependency'
}

interface AgentNetworkVisualizationProps {
  agents: AgentNode[]
  connections: AgentConnection[]
  onAgentClick?: (agentId: string) => void
  className?: string
}

export default function AgentNetworkVisualization({
  agents,
  connections,
  onAgentClick,
  className = ''
}: AgentNetworkVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [isPlaying, setIsPlaying] = useState(true)
  const [zoom, setZoom] = useState(1)
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 })
  const [showLabels, setShowLabels] = useState(true)
  const [showConnections, setShowConnections] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null)
  const [filterType, setFilterType] = useState<string>('all')

  // Animation state
  const animationRef = useRef<number>()
  const timeRef = useRef<number>(0)

  // Color schemes for different agent types
  const agentColors = {
    infrastructure: '#3b82f6', // blue
    database: '#10b981', // green
    core_engine: '#8b5cf6', // purple
    api_layer: '#f59e0b', // orange
    meta_learner: '#ef4444', // red
    security: '#06b6d4', // cyan
    analytics: '#eab308', // yellow
    communication: '#ec4899', // pink
    default: '#6b7280' // gray
  }

  const statusColors = {
    active: '#10b981',
    inactive: '#6b7280',
    learning: '#3b82f6',
    error: '#ef4444'
  }

  // Get agent color
  const getAgentColor = (agent: AgentNode) => {
    return agentColors[agent.type as keyof typeof agentColors] || agentColors.default
  }

  // Get status color
  const getStatusColor = (status: string) => {
    return statusColors[status as keyof typeof statusColors] || statusColors.inactive
  }

  // Filter agents based on type
  const filteredAgents = agents.filter(agent =>
    filterType === 'all' || agent.type === filterType
  )

  // Draw function
  const draw = (ctx: CanvasRenderingContext2D, timestamp: number) => {
    const canvas = ctx.canvas
    const centerX = canvas.width / 2
    const centerY = canvas.height / 2

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Apply zoom and pan
    ctx.save()
    ctx.translate(centerX + panOffset.x, centerY + panOffset.y)
    ctx.scale(zoom, zoom)

    // Draw connections first (behind nodes)
    if (showConnections) {
      connections.forEach(connection => {
        const fromAgent = filteredAgents.find(a => a.id === connection.from)
        const toAgent = filteredAgents.find(a => a.id === connection.to)

        if (fromAgent && toAgent) {
          const gradient = ctx.createLinearGradient(fromAgent.x, fromAgent.y, toAgent.x, toAgent.y)
          gradient.addColorStop(0, getAgentColor(fromAgent) + '40')
          gradient.addColorStop(1, getAgentColor(toAgent) + '40')

          ctx.strokeStyle = gradient
          ctx.lineWidth = Math.max(1, connection.strength * 3)
          ctx.globalAlpha = 0.6

          // Draw curved connection
          const dx = toAgent.x - fromAgent.x
          const dy = toAgent.y - fromAgent.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          const curvature = Math.min(distance * 0.3, 50)

          ctx.beginPath()
          ctx.moveTo(fromAgent.x, fromAgent.y)

          // Quadratic curve for smooth connection
          const cpX = (fromAgent.x + toAgent.x) / 2 + (dy / distance) * curvature
          const cpY = (fromAgent.y + toAgent.y) / 2 - (dx / distance) * curvature

          ctx.quadraticCurveTo(cpX, cpY, toAgent.x, toAgent.y)
          ctx.stroke()

          ctx.globalAlpha = 1
        }
      })
    }

    // Draw nodes
    filteredAgents.forEach(agent => {
      const isSelected = selectedAgent === agent.id
      const isHovered = hoveredAgent === agent.id

      // Calculate node size based on metrics
      const baseSize = 20
      const activitySize = baseSize + (agent.metrics.activity * 10)
      const size = isSelected ? activitySize * 1.2 : isHovered ? activitySize * 1.1 : activitySize

      // Pulsing effect for active agents
      const pulse = agent.status === 'active' ? Math.sin(timestamp * 0.005) * 0.1 + 1 : 1

      // Draw node glow
      const glowRadius = size * 1.5 * pulse
      const glowGradient = ctx.createRadialGradient(
        agent.x, agent.y, 0,
        agent.x, agent.y, glowRadius
      )
      glowGradient.addColorStop(0, getAgentColor(agent) + '60')
      glowGradient.addColorStop(1, getAgentColor(agent) + '00')

      ctx.fillStyle = glowGradient
      ctx.beginPath()
      ctx.arc(agent.x, agent.y, glowRadius, 0, Math.PI * 2)
      ctx.fill()

      // Draw main node
      ctx.fillStyle = getAgentColor(agent)
      ctx.strokeStyle = getStatusColor(agent.status)
      ctx.lineWidth = isSelected ? 3 : 2

      ctx.beginPath()
      ctx.arc(agent.x, agent.y, size * pulse, 0, Math.PI * 2)
      ctx.fill()
      ctx.stroke()

      // Draw status indicator
      ctx.fillStyle = getStatusColor(agent.status)
      ctx.beginPath()
      ctx.arc(agent.x + size * 0.7, agent.y - size * 0.7, 4, 0, Math.PI * 2)
      ctx.fill()

      // Draw labels
      if (showLabels && zoom > 0.5) {
        ctx.fillStyle = '#ffffff'
        ctx.font = `${Math.max(10, 12 * zoom)}px Inter, system-ui, sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'

        // Name
        ctx.fillText(agent.name, agent.x, agent.y + size + 15)

        // Type badge
        const typeText = agent.type.charAt(0).toUpperCase() + agent.type.slice(1)
        const textWidth = ctx.measureText(typeText).width
        const badgeWidth = textWidth + 8
        const badgeHeight = 16

        ctx.fillStyle = getAgentColor(agent) + '20'
        ctx.fillRect(agent.x - badgeWidth/2, agent.y + size + 25, badgeWidth, badgeHeight)

        ctx.strokeStyle = getAgentColor(agent) + '60'
        ctx.lineWidth = 1
        ctx.strokeRect(agent.x - badgeWidth/2, agent.y + size + 25, badgeWidth, badgeHeight)

        ctx.fillStyle = getAgentColor(agent)
        ctx.font = `${Math.max(8, 10 * zoom)}px Inter, system-ui, sans-serif`
        ctx.fillText(typeText, agent.x, agent.y + size + 33)
      }
    })

    ctx.restore()

    if (isPlaying) {
      animationRef.current = requestAnimationFrame((timestamp) => draw(ctx, timestamp))
    }
  }

  // Initialize canvas and start animation
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect()
      canvas.width = rect.width * window.devicePixelRatio
      canvas.height = rect.height * window.devicePixelRatio
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    }

    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)

    // Start animation
    const animate = (timestamp: number) => {
      timeRef.current = timestamp
      draw(ctx, timestamp)
    }

    if (isPlaying) {
      animationRef.current = requestAnimationFrame(animate)
    }

    return () => {
      window.removeEventListener('resize', resizeCanvas)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [agents, connections, zoom, panOffset, showLabels, showConnections, selectedAgent, hoveredAgent, filterType, isPlaying])

  // Mouse interaction handlers
  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = (event.clientX - rect.left - rect.width/2 - panOffset.x) / zoom
    const y = (event.clientY - rect.top - rect.height/2 - panOffset.y) / zoom

    // Find clicked agent
    const clickedAgent = filteredAgents.find(agent => {
      const distance = Math.sqrt((agent.x - x) ** 2 + (agent.y - y) ** 2)
      return distance < 25 / zoom
    })

    if (clickedAgent) {
      setSelectedAgent(clickedAgent.id)
      onAgentClick?.(clickedAgent.id)
    } else {
      setSelectedAgent(null)
    }
  }

  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = (event.clientX - rect.left - rect.width/2 - panOffset.x) / zoom
    const y = (event.clientY - rect.top - rect.height/2 - panOffset.y) / zoom

    // Find hovered agent
    const hoveredAgent = filteredAgents.find(agent => {
      const distance = Math.sqrt((agent.x - x) ** 2 + (agent.y - y) ** 2)
      return distance < 25 / zoom
    })

    setHoveredAgent(hoveredAgent?.id || null)
  }

  const resetView = () => {
    setZoom(1)
    setPanOffset({ x: 0, y: 0 })
  }

  const selectedAgentData = selectedAgent ? agents.find(a => a.id === selectedAgent) : null

  return (
    <div className={`relative ${className}`}>
      <Card className="bg-gradient-to-br from-slate-800/50 to-slate-700/50 border-slate-600/50 backdrop-blur-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Network className="w-5 h-5" />
              <span>Agent Network Visualization</span>
            </CardTitle>

            <div className="flex items-center space-x-2">
              {/* Controls */}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsPlaying(!isPlaying)}
                className="border-slate-600 hover:border-slate-500"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setZoom(Math.min(zoom * 1.2, 3))}
                className="border-slate-600 hover:border-slate-500"
              >
                <ZoomIn className="w-4 h-4" />
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setZoom(Math.max(zoom * 0.8, 0.3))}
                className="border-slate-600 hover:border-slate-500"
              >
                <ZoomOut className="w-4 h-4" />
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={resetView}
                className="border-slate-600 hover:border-slate-500"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowLabels(!showLabels)}
                className="border-slate-600 hover:border-slate-500"
              >
                {showLabels ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowConnections(!showConnections)}
                className="border-slate-600 hover:border-slate-500"
              >
                <Network className="w-4 h-4" />
              </Button>

              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="bg-slate-700/50 border border-slate-600 rounded px-2 py-1 text-sm"
              >
                <option value="all">All Types</option>
                <option value="infrastructure">Infrastructure</option>
                <option value="database">Database</option>
                <option value="core_engine">Core Engine</option>
                <option value="api_layer">API Layer</option>
                <option value="meta_learner">Meta-Learner</option>
                <option value="security">Security</option>
                <option value="analytics">Analytics</option>
                <option value="communication">Communication</option>
              </select>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <div className="relative">
            <canvas
              ref={canvasRef}
              className="w-full h-96 bg-slate-900/50 rounded-lg border border-slate-600 cursor-pointer"
              onClick={handleCanvasClick}
              onMouseMove={handleMouseMove}
              onMouseLeave={() => setHoveredAgent(null)}
            />

            {/* Legend */}
            <div className="absolute top-4 left-4 bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 border border-slate-600">
              <h4 className="text-sm font-medium text-slate-300 mb-2">Legend</h4>
              <div className="space-y-1 text-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-slate-400">Active</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-slate-400">Learning</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                  <span className="text-slate-400">Inactive</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-slate-400">Error</span>
                </div>
              </div>
            </div>

            {/* Selected Agent Details */}
            {selectedAgentData && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute bottom-4 right-4 bg-slate-800/90 backdrop-blur-sm rounded-lg p-4 border border-slate-600 min-w-64"
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-slate-200">{selectedAgentData.name}</h4>
                  <Badge variant="outline" className="border-slate-600">
                    {selectedAgentData.type}
                  </Badge>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Status:</span>
                    <Badge variant={selectedAgentData.status === 'active' ? 'default' : 'secondary'}>
                      {selectedAgentData.status}
                    </Badge>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Activity:</span>
                    <span className="text-slate-200">{selectedAgentData.metrics.activity.toFixed(1)}%</span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Collaboration:</span>
                    <span className="text-slate-200">{selectedAgentData.metrics.collaboration.toFixed(1)}%</span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Performance:</span>
                    <span className="text-slate-200">{selectedAgentData.metrics.performance}/100</span>
                  </div>

                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Connections:</span>
                    <span className="text-slate-200">{selectedAgentData.connections.length}</span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
