import { useCallback, useEffect, useRef, useState } from 'react'

export interface WebSocketTestMessage {
  id: string
  type: 'ping' | 'pong' | 'data' | 'error' | 'system'
  payload: any
  timestamp: Date
  direction: 'sent' | 'received'
  latency?: number
}

export interface WebSocketTestMetrics {
  messagesSent: number
  messagesReceived: number
  totalLatency: number
  averageLatency: number
  minLatency: number
  maxLatency: number
  connectionTime: number
  uptime: number
  reconnectCount: number
  errors: number
  throughput: number // messages per second
}

export interface WebSocketTestScenario {
  id: string
  name: string
  description: string
  messages: Array<{
    type: WebSocketTestMessage['type']
    payload: any
    delay?: number
    expectResponse?: boolean
    timeout?: number
  }>
  duration: number
  concurrentConnections?: number
}

export interface WebSocketTestResult {
  scenarioId: string
  success: boolean
  duration: number
  metrics: WebSocketTestMetrics
  messages: WebSocketTestMessage[]
  errors: string[]
  timestamp: Date
}

export const useWebSocketTesting = (wsHook: any) => {
  const [isTesting, setIsTesting] = useState(false)
  const [currentTest, setCurrentTest] = useState<WebSocketTestScenario | null>(null)
  const [testResults, setTestResults] = useState<WebSocketTestResult[]>([])
  const [testMessages, setTestMessages] = useState<WebSocketTestMessage[]>([])
  const [testMetrics, setTestMetrics] = useState<WebSocketTestMetrics>({
    messagesSent: 0,
    messagesReceived: 0,
    totalLatency: 0,
    averageLatency: 0,
    minLatency: Infinity,
    maxLatency: 0,
    connectionTime: 0,
    uptime: 0,
    reconnectCount: 0,
    errors: 0,
    throughput: 0,
  })

  const testStartTimeRef = useRef<number>(0)
  const messageCounterRef = useRef<number>(0)
  const pendingResponsesRef = useRef<Map<string, { sentAt: number, timeout: NodeJS.Timeout }>>(new Map())

  // Generate unique message ID
  const generateMessageId = useCallback(() => {
    return `test_msg_${++messageCounterRef.current}_${Date.now()}`
  }, [])

  // Record message
  const recordMessage = useCallback((
    type: WebSocketTestMessage['type'],
    payload: any,
    direction: WebSocketTestMessage['direction'],
    latency?: number
  ) => {
    const message: WebSocketTestMessage = {
      id: generateMessageId(),
      type,
      payload,
      timestamp: new Date(),
      direction,
      latency,
    }

    setTestMessages(prev => [...prev.slice(-100), message]) // Keep last 100 messages

    // Update metrics
    setTestMetrics(prev => {
      const newMetrics = { ...prev }

      if (direction === 'sent') {
        newMetrics.messagesSent++
      } else {
        newMetrics.messagesReceived++
      }

      if (latency !== undefined) {
        newMetrics.totalLatency += latency
        newMetrics.averageLatency = newMetrics.totalLatency / newMetrics.messagesReceived
        newMetrics.minLatency = Math.min(newMetrics.minLatency, latency)
        newMetrics.maxLatency = Math.max(newMetrics.maxLatency, latency)
      }

      // Calculate throughput
      const elapsed = Date.now() - testStartTimeRef.current
      if (elapsed > 0) {
        newMetrics.throughput = (newMetrics.messagesSent + newMetrics.messagesReceived) / (elapsed / 1000)
      }

      return newMetrics
    })

    return message
  }, [generateMessageId])

  // Send test message and track response
  const sendTestMessage = useCallback(async (
    type: WebSocketTestMessage['type'],
    payload: any,
    expectResponse = false,
    timeout = 5000
  ): Promise<WebSocketTestMessage | null> => {
    if (!wsHook.isConnected) {
      throw new Error('WebSocket not connected')
    }

    const messageId = generateMessageId()
    const sentAt = Date.now()

    // Record sent message
    recordMessage(type, { ...payload, _testId: messageId }, 'sent')

    // Send via WebSocket
    const success = wsHook.send({ type, data: payload, _testId: messageId })

    if (!success) {
      throw new Error('Failed to send WebSocket message')
    }

    if (!expectResponse) {
      return null
    }

    // Wait for response
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        pendingResponsesRef.current.delete(messageId)
        reject(new Error(`Response timeout for message ${messageId}`))
      }, timeout)

      pendingResponsesRef.current.set(messageId, {
        sentAt,
        timeout: timeoutId,
      })

      // Set up response listener (this would be integrated with the WebSocket hook)
      // For now, we'll simulate response handling
    })
  }, [wsHook, generateMessageId, recordMessage])

  // Handle incoming messages during testing
  useEffect(() => {
    if (!isTesting) return

    const handleMessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data)
        const testId = data._testId

        if (testId && pendingResponsesRef.current.has(testId)) {
          const pending = pendingResponsesRef.current.get(testId)!
          const latency = Date.now() - pending.sentAt

          // Clear timeout
          clearTimeout(pending.timeout)
          pendingResponsesRef.current.delete(testId)

          // Record received message
          recordMessage(data.type || 'data', data, 'received', latency)
        } else {
          // Record unsolicited message
          recordMessage(data.type || 'data', data, 'received')
        }
      } catch (error) {
        recordMessage('error', { error: error instanceof Error ? error.message : String(error) }, 'received')
      }
    }

    // This would need to be integrated with the actual WebSocket hook
    // For now, this is a placeholder for the integration

    return () => {
      // Cleanup
      pendingResponsesRef.current.forEach(pending => {
        clearTimeout(pending.timeout)
      })
      pendingResponsesRef.current.clear()
    }
  }, [isTesting, recordMessage])

  // Run test scenario
  const runTestScenario = useCallback(async (scenario: WebSocketTestScenario): Promise<WebSocketTestResult> => {
    if (isTesting) {
      throw new Error('Test already running')
    }

    setIsTesting(true)
    setCurrentTest(scenario)
    testStartTimeRef.current = Date.now()

    const startTime = Date.now()
    const errors: string[] = []
    const messages: WebSocketTestMessage[] = []

    try {
      // Reset metrics
      setTestMetrics({
        messagesSent: 0,
        messagesReceived: 0,
        totalLatency: 0,
        averageLatency: 0,
        minLatency: Infinity,
        maxLatency: 0,
        connectionTime: Date.now() - (wsHook.connectionTime || Date.now()),
        uptime: 0,
        reconnectCount: wsHook.connectionAttempts || 0,
        errors: 0,
        throughput: 0,
      })

      // Wait for connection
      if (!wsHook.isConnected) {
        await new Promise((resolve, reject) => {
          const timeout = setTimeout(() => reject(new Error('Connection timeout')), 10000)
          const checkConnection = () => {
            if (wsHook.isConnected) {
              clearTimeout(timeout)
              resolve(void 0)
            } else {
              setTimeout(checkConnection, 100)
            }
          }
          checkConnection()
        })
      }

      // Execute test messages
      for (const message of scenario.messages) {
        try {
          if (message.delay) {
            await new Promise(resolve => setTimeout(resolve, message.delay))
          }

          await sendTestMessage(
            message.type,
            message.payload,
            message.expectResponse,
            message.timeout
          )
        } catch (error) {
          errors.push(`Message ${message.type}: ${error instanceof Error ? error.message : String(error)}`)
        }
      }

      // Wait for scenario duration
      if (scenario.duration > 0) {
        await new Promise(resolve => setTimeout(resolve, scenario.duration))
      }

      // Calculate final metrics
      const endTime = Date.now()
      const duration = endTime - startTime

      const finalMetrics: WebSocketTestMetrics = {
        ...testMetrics,
        uptime: duration,
        errors: errors.length,
      }

      const result: WebSocketTestResult = {
        scenarioId: scenario.id,
        success: errors.length === 0,
        duration,
        metrics: finalMetrics,
        messages: testMessages,
        errors,
        timestamp: new Date(),
      }

      setTestResults(prev => [...prev.slice(-10), result]) // Keep last 10 results

      return result

    } catch (error) {
      errors.push(`Test execution failed: ${error instanceof Error ? error.message : String(error)}`)
      throw error
    } finally {
      setIsTesting(false)
      setCurrentTest(null)
    }
  }, [isTesting, wsHook, testMetrics, testMessages, sendTestMessage])

  // Predefined test scenarios
  const testScenarios: WebSocketTestScenario[] = [
    {
      id: 'basic-connectivity',
      name: 'Basic Connectivity Test',
      description: 'Test basic WebSocket connection and ping-pong',
      messages: [
        { type: 'ping', payload: { timestamp: Date.now() }, expectResponse: true },
        { type: 'ping', payload: { message: 'test' }, expectResponse: true },
      ],
      duration: 1000,
    },
    {
      id: 'load-test',
      name: 'Load Test',
      description: 'Send multiple messages to test throughput',
      messages: Array.from({ length: 50 }, (_, i) => ({
        type: 'data' as const,
        payload: { index: i, data: 'x'.repeat(100) },
        delay: 50, // 50ms between messages
      })),
      duration: 0,
    },
    {
      id: 'stress-test',
      name: 'Stress Test',
      description: 'Test connection under high frequency messaging',
      messages: Array.from({ length: 100 }, (_, i) => ({
        type: 'ping' as const,
        payload: { sequence: i },
        expectResponse: true,
        delay: 10, // 10ms between messages
      })),
      duration: 2000,
    },
    {
      id: 'reconnection-test',
      name: 'Reconnection Test',
      description: 'Test automatic reconnection after disconnection',
      messages: [
        { type: 'ping', payload: { phase: 'before_disconnect' }, expectResponse: true },
        // Note: Actual disconnection would need to be triggered externally
        { type: 'ping', payload: { phase: 'after_reconnect' }, expectResponse: true, delay: 5000 },
      ],
      duration: 10000,
    },
  ]

  // Export test data
  const exportTestResults = useCallback(() => {
    const exportData = {
      results: testResults,
      scenarios: testScenarios,
      timestamp: new Date().toISOString(),
      connectionInfo: {
        isConnected: wsHook.isConnected,
        state: wsHook.state,
        url: wsHook.url,
        connectionTime: wsHook.connectionTime,
      },
    }

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    })

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `websocket-test-results-${new Date().toISOString()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [testResults, wsHook])

  return {
    // Test state
    isTesting,
    currentTest,
    testResults,
    testMessages,
    testMetrics,

    // Test execution
    runTestScenario,
    testScenarios,

    // Utilities
    sendTestMessage,
    recordMessage,
    exportTestResults,

    // Cleanup
    clearTestData: () => {
      setTestMessages([])
      setTestResults([])
      setTestMetrics({
        messagesSent: 0,
        messagesReceived: 0,
        totalLatency: 0,
        averageLatency: 0,
        minLatency: Infinity,
        maxLatency: 0,
        connectionTime: 0,
        uptime: 0,
        reconnectCount: 0,
        errors: 0,
        throughput: 0,
      })
    },
  }
}

// Hook for real-time WebSocket monitoring
export const useWebSocketMonitoring = (wsHook: any) => {
  const [connectionHistory, setConnectionHistory] = useState<Array<{
    timestamp: Date
    event: 'connected' | 'disconnected' | 'error' | 'reconnecting'
    details?: any
  }>>([])

  const [performanceMetrics, setPerformanceMetrics] = useState({
    averageLatency: 0,
    messageRate: 0, // messages per second
    errorRate: 0,
    uptimePercentage: 100,
  })

  const previousWsStateRef = useRef<string>('')

  useEffect(() => {
    // Monitor connection state changes
    if (previousWsStateRef.current !== wsHook.state) {
      setConnectionHistory(prev => [...prev.slice(-50), {
        timestamp: new Date(),
        event: wsHook.state as any,
        details: wsHook.lastError || undefined,
      }])
      previousWsStateRef.current = wsHook.state
    }
  }, [wsHook.state, wsHook.lastError])

  // Calculate uptime percentage
  useEffect(() => {
    const history = connectionHistory.slice(-100) // Last 100 events
    const connectedTime = history.reduce((total, event, index) => {
      if (event.event === 'connected') {
        const nextEvent = history[index + 1]
        const duration = nextEvent
          ? nextEvent.timestamp.getTime() - event.timestamp.getTime()
          : Date.now() - event.timestamp.getTime()
        return total + duration
      }
      return total
    }, 0)

    const totalTime = history.length > 1
      ? history[history.length - 1].timestamp.getTime() - history[0].timestamp.getTime()
      : 0

    const uptimePercentage = totalTime > 0 ? (connectedTime / totalTime) * 100 : 100

    setPerformanceMetrics(prev => ({
      ...prev,
      uptimePercentage,
    }))
  }, [connectionHistory])

  return {
    connectionHistory,
    performanceMetrics,
    clearHistory: () => setConnectionHistory([]),
  }
}
