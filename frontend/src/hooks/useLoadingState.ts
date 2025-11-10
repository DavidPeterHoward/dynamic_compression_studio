import { useCallback, useEffect, useRef, useState } from 'react'

export interface LoadingState {
  isLoading: boolean
  error: Error | null
  progress?: number
  message?: string
  phase?: string
  startTime?: number
  estimatedDuration?: number
  subTasks?: Array<{
    id: string
    label: string
    progress: number
    status: 'pending' | 'running' | 'completed' | 'failed'
    startTime?: number
    duration?: number
  }>
  retryCount?: number
  canCancel?: boolean
}

export interface LoadingOptions {
  showProgress?: boolean
  message?: string
  timeout?: number
}

export const useLoadingState = (initialState: Partial<LoadingState> = {}) => {
  const [state, setState] = useState<LoadingState>({
    isLoading: false,
    error: null,
    progress: 0,
    message: '',
    phase: '',
    startTime: undefined,
    estimatedDuration: undefined,
    subTasks: [],
    retryCount: 0,
    canCancel: false,
    ...initialState,
  })

  const timeoutRef = useRef<NodeJS.Timeout>()
  const abortControllerRef = useRef<AbortController>()

  const startLoading = useCallback((options: LoadingOptions = {}) => {
    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController()

    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
      progress: options.showProgress ? 0 : undefined,
      message: options.message || prev.message,
      phase: options.phase || prev.phase || 'Initializing',
      startTime: Date.now(),
      estimatedDuration: options.estimatedDuration,
      subTasks: options.subTasks || prev.subTasks || [],
      retryCount: 0,
      canCancel: options.enableCancellation !== false,
    }))

    // Set timeout to prevent infinite loading
    if (options.timeout) {
      timeoutRef.current = setTimeout(() => {
        setError(new Error('Operation timed out'))
      }, options.timeout)
    }
  }, [])

  // Enhanced loading options interface
  interface EnhancedLoadingOptions extends LoadingOptions {
    phase?: string
    estimatedDuration?: number
    subTasks?: LoadingState['subTasks']
    enableCancellation?: boolean
    onCancel?: () => void
  }

  const stopLoading = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = undefined
    }

    // Abort any ongoing operations
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = undefined
    }

    setState(prev => ({
      ...prev,
      isLoading: false,
      progress: undefined,
      phase: 'Completed',
      canCancel: false,
    }))
  }, [])

  const cancelOperation = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    setState(prev => ({
      ...prev,
      isLoading: false,
      error: new Error('Operation cancelled by user'),
      message: 'Operation cancelled',
      phase: 'Cancelled',
      canCancel: false,
    }))
  }, [])

  const setPhase = useCallback((phase: string, message?: string) => {
    setState(prev => ({
      ...prev,
      phase,
      message: message || prev.message,
    }))
  }, [])

  const updateSubTask = useCallback((
    taskId: string,
    updates: Partial<LoadingState['subTasks'][0]>
  ) => {
    setState(prev => {
      if (!prev.subTasks) return prev

      const updatedTasks = prev.subTasks.map(task => {
        if (task.id === taskId) {
          const updatedTask = { ...task, ...updates }

          // Calculate duration if task completed
          if (updates.status === 'completed' && task.startTime && !updatedTask.duration) {
            updatedTask.duration = Date.now() - task.startTime
          }

          return updatedTask
        }
        return task
      })

      // Calculate overall progress from sub-tasks
      const completedTasks = updatedTasks.filter(task => task.status === 'completed').length
      const totalProgress = updatedTasks.length > 0 ? (completedTasks / updatedTasks.length) * 100 : 0

      return {
        ...prev,
        subTasks: updatedTasks,
        progress: Math.round(totalProgress),
      }
    })
  }, [])

  const addSubTask = useCallback((
    task: Omit<LoadingState['subTasks'][0], 'startTime'>
  ) => {
    setState(prev => ({
      ...prev,
      subTasks: [
        ...(prev.subTasks || []),
        {
          ...task,
          startTime: Date.now(),
        }
      ]
    }))
  }, [])

  const retryOperation = useCallback((maxRetries: number = 3) => {
    setState(prev => {
      if ((prev.retryCount || 0) >= maxRetries) {
        return {
          ...prev,
          error: new Error(`Maximum retry attempts (${maxRetries}) exceeded`),
        }
      }

      return {
        ...prev,
        error: null,
        isLoading: true,
        retryCount: (prev.retryCount || 0) + 1,
        message: `Retrying... (attempt ${(prev.retryCount || 0) + 1}/${maxRetries})`,
        phase: 'Retrying',
      }
    })
  }, [])

  const getElapsedTime = useCallback(() => {
    return state.startTime ? Date.now() - state.startTime : 0
  }, [state.startTime])

  const getEstimatedTimeRemaining = useCallback(() => {
    if (!state.isLoading || !state.progress || state.progress === 0) return 0

    const elapsed = getElapsedTime()
    const totalEstimated = elapsed / (state.progress / 100)
    return Math.max(0, totalEstimated - elapsed)
  }, [state.isLoading, state.progress, getElapsedTime])

  const getCompletionPercentage = useCallback(() => {
    if (!state.subTasks || state.subTasks.length === 0) {
      return state.progress || 0
    }

    const totalTasks = state.subTasks.length
    const completedTasks = state.subTasks.filter(task => task.status === 'completed').length
    return Math.round((completedTasks / totalTasks) * 100)
  }, [state.subTasks, state.progress])

  const setError = useCallback((error: Error | string) => {
    const errorObj = typeof error === 'string' ? new Error(error) : error

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = undefined
    }

    setState(prev => ({
      ...prev,
      isLoading: false,
      error: errorObj,
      progress: undefined,
    }))
  }, [])

  const clearError = useCallback(() => {
    setState(prev => ({
      ...prev,
      error: null,
    }))
  }, [])

  const updateProgress = useCallback((progress: number, message?: string) => {
    setState(prev => ({
      ...prev,
      progress: Math.max(0, Math.min(100, progress)),
      message: message || prev.message,
    }))
  }, [])

  const reset = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = undefined
    }

    setState({
      isLoading: false,
      error: null,
      progress: undefined,
      message: '',
    })
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  return {
    ...state,
    startLoading,
    stopLoading,
    cancelOperation,
    setPhase,
    updateSubTask,
    addSubTask,
    retryOperation,
    setError,
    clearError,
    updateProgress,
    reset,
    getElapsedTime,
    getEstimatedTimeRemaining,
    getCompletionPercentage,
  }
}

// Specialized hook for async operations
export const useAsyncOperation = <T extends any[], R>(
  operation: (...args: T) => Promise<R>,
  options: LoadingOptions = {}
) => {
  const loadingState = useLoadingState()

  const execute = useCallback(async (...args: T): Promise<R | null> => {
    try {
      loadingState.startLoading(options)
      const result = await operation(...args)
      loadingState.stopLoading()
      return result
    } catch (error) {
      loadingState.setError(error as Error)
      return null
    }
  }, [operation, options, loadingState])

  return {
    ...loadingState,
    execute,
  }
}

// Hook for managing multiple concurrent operations
export const useConcurrentOperations = () => {
  const [operations, setOperations] = useState<Map<string, LoadingState>>(new Map())

  const startOperation = useCallback((id: string, options: LoadingOptions = {}) => {
    setOperations(prev => {
      const newMap = new Map(prev)
      newMap.set(id, {
        isLoading: true,
        error: null,
        progress: options.showProgress ? 0 : undefined,
        message: options.message,
      })
      return newMap
    })
  }, [])

  const stopOperation = useCallback((id: string) => {
    setOperations(prev => {
      const newMap = new Map(prev)
      const operation = newMap.get(id)
      if (operation) {
        newMap.set(id, {
          ...operation,
          isLoading: false,
          progress: undefined,
        })
      }
      return newMap
    })
  }, [])

  const setOperationError = useCallback((id: string, error: Error | string) => {
    const errorObj = typeof error === 'string' ? new Error(error) : error

    setOperations(prev => {
      const newMap = new Map(prev)
      const operation = newMap.get(id)
      if (operation) {
        newMap.set(id, {
          ...operation,
          isLoading: false,
          error: errorObj,
          progress: undefined,
        })
      }
      return newMap
    })
  }, [])

  const updateOperationProgress = useCallback((id: string, progress: number, message?: string) => {
    setOperations(prev => {
      const newMap = new Map(prev)
      const operation = newMap.get(id)
      if (operation) {
        newMap.set(id, {
          ...operation,
          progress: Math.max(0, Math.min(100, progress)),
          message: message || operation.message,
        })
      }
      return newMap
    })
  }, [])

  const clearOperationError = useCallback((id: string) => {
    setOperations(prev => {
      const newMap = new Map(prev)
      const operation = newMap.get(id)
      if (operation) {
        newMap.set(id, {
          ...operation,
          error: null,
        })
      }
      return newMap
    })
  }, [])

  const removeOperation = useCallback((id: string) => {
    setOperations(prev => {
      const newMap = new Map(prev)
      newMap.delete(id)
      return newMap
    })
  }, [])

  const getOperationState = useCallback((id: string): LoadingState | undefined => {
    return operations.get(id)
  }, [operations])

  const getAllOperations = useCallback(() => {
    return Array.from(operations.entries()).map(([id, state]) => ({ id, ...state }))
  }, [operations])

  const hasActiveOperations = operations.size > 0 && Array.from(operations.values()).some(op => op.isLoading)
  const hasErrors = Array.from(operations.values()).some(op => op.error)

  return {
    operations,
    hasActiveOperations,
    hasErrors,
    startOperation,
    stopOperation,
    setOperationError,
    updateOperationProgress,
    clearOperationError,
    removeOperation,
    getOperationState,
    getAllOperations,
  }
}
