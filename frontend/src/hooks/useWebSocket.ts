import { useCallback, useEffect, useRef, useState } from 'react'

export type WebSocketState = 'connecting' | 'connected' | 'disconnected' | 'error' | 'reconnecting'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: Date
}

export interface WebSocketOptions {
  url: string
  protocols?: string | string[]
  reconnectAttempts?: number
  reconnectInterval?: number
  reconnectBackoff?: number
  maxReconnectInterval?: number
  heartbeatInterval?: number
  heartbeatTimeout?: number
  onOpen?: (event: Event) => void
  onClose?: (event: CloseEvent) => void
  onError?: (event: Event) => void
  onMessage?: (event: MessageEvent) => void
  shouldReconnect?: (closeEvent: CloseEvent) => boolean
  onReconnectAttempt?: (attempt: number, maxAttempts: number) => void
  onReconnectSuccess?: () => void
  onReconnectFailure?: () => void
}

export interface WebSocketHookReturn {
  socket: WebSocket | null
  state: WebSocketState
  isConnected: boolean
  lastMessage: WebSocketMessage | null
  send: (data: any) => boolean
  close: (code?: number, reason?: string) => void
  reconnect: () => void
  connectionAttempts: number
  lastError: Event | null
  messages: WebSocketMessage[]
}

const DEFAULT_OPTIONS: Partial<WebSocketOptions> = {
  reconnectAttempts: 5,
  reconnectInterval: 1000,
  reconnectBackoff: 1.5,
  maxReconnectInterval: 30000,
  heartbeatInterval: 30000,
  heartbeatTimeout: 5000,
}

export const useWebSocket = (options: WebSocketOptions): WebSocketHookReturn => {
  const {
    url,
    protocols,
    reconnectAttempts = DEFAULT_OPTIONS.reconnectAttempts!,
    reconnectInterval = DEFAULT_OPTIONS.reconnectInterval!,
    reconnectBackoff = DEFAULT_OPTIONS.reconnectBackoff!,
    maxReconnectInterval = DEFAULT_OPTIONS.maxReconnectInterval!,
    heartbeatInterval = DEFAULT_OPTIONS.heartbeatInterval!,
    heartbeatTimeout = DEFAULT_OPTIONS.heartbeatTimeout!,
    onOpen,
    onClose,
    onError,
    onMessage,
    shouldReconnect = () => true,
    onReconnectAttempt,
    onReconnectSuccess,
    onReconnectFailure,
  } = { ...DEFAULT_OPTIONS, ...options }

  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [state, setState] = useState<WebSocketState>('disconnected')
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [lastError, setLastError] = useState<Event | null>(null)
  const [messages, setMessages] = useState<WebSocketMessage[]>([])
  const [connectionAttempts, setConnectionAttempts] = useState(0)

  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>()
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectIntervalRef = useRef(reconnectInterval)
  const isManualCloseRef = useRef(false)
  const isReconnectingRef = useRef(false)

  const isConnected = state === 'connected'

  // Clear all timers
  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = undefined
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = undefined
    }
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current)
      heartbeatTimeoutRef.current = undefined
    }
  }, [])

  // Start heartbeat
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) return

    heartbeatIntervalRef.current = setInterval(() => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        // Send ping
        socket.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }))

        // Set timeout for pong response
        heartbeatTimeoutRef.current = setTimeout(() => {
          console.warn('Heartbeat timeout - connection may be unstable')
          if (socket) {
            socket.close(1000, 'heartbeat timeout')
          }
        }, heartbeatTimeout)
      }
    }, heartbeatInterval)
  }, [socket, heartbeatInterval, heartbeatTimeout])

  // Stop heartbeat
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
      heartbeatIntervalRef.current = undefined
    }
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current)
      heartbeatTimeoutRef.current = undefined
    }
  }, [])

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (socket && socket.readyState === WebSocket.CONNECTING) return
    if (isManualCloseRef.current) return

    try {
      setState('connecting')
      setLastError(null)

      const ws = new WebSocket(url, protocols)
      setSocket(ws)

      ws.onopen = (event) => {
        console.log('WebSocket connected:', url)
        setState('connected')
        setConnectionAttempts(0)
        setLastError(null)
        reconnectIntervalRef.current = reconnectInterval

        if (isReconnectingRef.current) {
          onReconnectSuccess?.()
          isReconnectingRef.current = false
        }

        startHeartbeat()
        onOpen?.(event)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          const message: WebSocketMessage = {
            type: data.type || 'unknown',
            data,
            timestamp: new Date(),
          }

          setLastMessage(message)
          setMessages(prev => [...prev.slice(-49), message]) // Keep last 50 messages

          // Handle pong response
          if (data.type === 'pong') {
            if (heartbeatTimeoutRef.current) {
              clearTimeout(heartbeatTimeoutRef.current)
              heartbeatTimeoutRef.current = undefined
            }
          }

          onMessage?.(event)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error, event.data)
        }
      }

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        setState('disconnected')
        setSocket(null)
        stopHeartbeat()

        onClose?.(event)

        // Attempt reconnection if not manually closed and should reconnect
        if (!isManualCloseRef.current && shouldReconnect(event)) {
          scheduleReconnect()
        }
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        setState('error')
        setLastError(event)
        onError?.(event)
      }

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      setState('error')
      setLastError(error as Event)
      if (shouldReconnect({ code: 0, reason: '', wasClean: false } as CloseEvent)) {
        scheduleReconnect()
      }
    }
  }, [
    url,
    protocols,
    reconnectInterval,
    startHeartbeat,
    stopHeartbeat,
    onOpen,
    onClose,
    onError,
    onMessage,
    shouldReconnect,
    onReconnectSuccess,
  ])

  // Schedule reconnection with exponential backoff
  const scheduleReconnect = useCallback(() => {
    if (connectionAttempts >= reconnectAttempts) {
      console.error(`Max reconnection attempts (${reconnectAttempts}) reached`)
      setState('error')
      onReconnectFailure?.()
      return
    }

    setState('reconnecting')
    isReconnectingRef.current = true

    const attempt = connectionAttempts + 1
    setConnectionAttempts(attempt)
    onReconnectAttempt?.(attempt, reconnectAttempts)

    const delay = Math.min(
      reconnectIntervalRef.current * Math.pow(reconnectBackoff, attempt - 1),
      maxReconnectInterval
    )

    reconnectIntervalRef.current = delay

    console.log(`Scheduling reconnection attempt ${attempt}/${reconnectAttempts} in ${delay}ms`)

    reconnectTimeoutRef.current = setTimeout(() => {
      connect()
    }, delay)
  }, [
    connectionAttempts,
    reconnectAttempts,
    reconnectBackoff,
    maxReconnectInterval,
    onReconnectAttempt,
    onReconnectFailure,
    connect,
  ])

  // Send message
  const send = useCallback((data: any): boolean => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data)
        socket.send(message)
        return true
      } catch (error) {
        console.error('Failed to send WebSocket message:', error)
        return false
      }
    }
    return false
  }, [socket])

  // Close connection
  const close = useCallback((code = 1000, reason = 'Client disconnect') => {
    isManualCloseRef.current = true
    clearTimers()

    if (socket) {
      socket.close(code, reason)
    }

    setState('disconnected')
    setSocket(null)
  }, [socket, clearTimers])

  // Force reconnection
  const reconnect = useCallback(() => {
    if (socket) {
      socket.close(1000, 'Manual reconnect')
    }
    isManualCloseRef.current = false
    setConnectionAttempts(0)
    reconnectIntervalRef.current = reconnectInterval
    connect()
  }, [socket, reconnectInterval, connect])

  // Initial connection
  useEffect(() => {
    connect()

    return () => {
      clearTimers()
      if (socket) {
        socket.close()
      }
    }
  }, []) // Empty dependency array - only run once on mount

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimers()
      isManualCloseRef.current = true
      if (socket) {
        socket.close()
      }
    }
  }, [socket, clearTimers])

  return {
    socket,
    state,
    isConnected,
    lastMessage,
    send,
    close,
    reconnect,
    connectionAttempts,
    lastError,
    messages,
  }
}

// Specialized hook for agent updates WebSocket
export const useAgentWebSocket = (baseUrl = 'ws://localhost:8443') => {
  const [agentUpdates, setAgentUpdates] = useState<any[]>([])
  const [systemStatus, setSystemStatus] = useState<any>(null)
  const [taskUpdates, setTaskUpdates] = useState<any[]>([])

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data)

      switch (data.event_type || data.type) {
        case 'agent_status':
        case 'agent_update':
          setAgentUpdates(prev => [...prev.slice(-9), data]) // Keep last 10 updates
          break
        case 'system_status':
        case 'system_update':
          setSystemStatus(data.data || data)
          break
        case 'task_completed':
        case 'task_started':
        case 'task_failed':
          setTaskUpdates(prev => [...prev.slice(-9), data]) // Keep last 10 updates
          break
        default:
          console.log('Unknown WebSocket message type:', data.type || data.event_type)
      }
    } catch (error) {
      console.error('Failed to handle agent WebSocket message:', error)
    }
  }, [])

  const { socket, state, isConnected, send, reconnect, lastError } = useWebSocket({
    url: `${baseUrl}/ws/agent-updates`,
    reconnectAttempts: 10,
    reconnectInterval: 1000,
    heartbeatInterval: 30000,
    onMessage: handleMessage,
    shouldReconnect: (event) => {
      // Don't reconnect on normal closures or policy violations
      return event.code !== 1000 && event.code !== 1008
    },
  })

  return {
    socket,
    state,
    isConnected,
    agentUpdates,
    systemStatus,
    taskUpdates,
    send,
    reconnect,
    lastError,
  }
}

// Hook for managing multiple WebSocket connections
export const useWebSocketManager = () => {
  const [connections, setConnections] = useState<Map<string, WebSocketHookReturn>>(new Map())

  const addConnection = useCallback((id: string, options: WebSocketOptions) => {
    const connection = useWebSocket(options)
    setConnections(prev => new Map(prev.set(id, connection)))
    return connection
  }, [])

  const removeConnection = useCallback((id: string) => {
    setConnections(prev => {
      const newMap = new Map(prev)
      const connection = newMap.get(id)
      if (connection) {
        connection.close()
        newMap.delete(id)
      }
      return newMap
    })
  }, [])

  const getConnection = useCallback((id: string) => {
    return connections.get(id)
  }, [connections])

  const reconnectAll = useCallback(() => {
    connections.forEach(connection => connection.reconnect())
  }, [connections])

  const closeAll = useCallback(() => {
    connections.forEach(connection => connection.close())
  }, [connections])

  const getAllConnections = useCallback(() => {
    return Array.from(connections.entries()).map(([id, connection]) => ({ id, ...connection }))
  }, [connections])

  const hasActiveConnections = Array.from(connections.values()).some(conn => conn.isConnected)
  const hasErrors = Array.from(connections.values()).some(conn => conn.lastError)

  return {
    connections,
    hasActiveConnections,
    hasErrors,
    addConnection,
    removeConnection,
    getConnection,
    reconnectAll,
    closeAll,
    getAllConnections,
  }
}
