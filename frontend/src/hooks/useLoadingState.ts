import { useCallback, useRef, useState } from 'react'

export interface LoadingState {
  isLoading: boolean
  error: Error | null
  progress?: number
  message?: string
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
    ...initialState,
  })

  const timeoutRef = useRef<NodeJS.Timeout>()

  const startLoading = useCallback((options: LoadingOptions = {}) => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
      progress: options.showProgress ? 0 : undefined,
      message: options.message || prev.message,
    }))

    // Set timeout to prevent infinite loading
    if (options.timeout) {
      timeoutRef.current = setTimeout(() => {
        setError(new Error('Operation timed out'))
      }, options.timeout)
    }
  }, [])

  const stopLoading = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = undefined
    }

    setState(prev => ({
      ...prev,
      isLoading: false,
      progress: undefined,
    }))
  }, [])

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

  return {
    ...state,
    startLoading,
    stopLoading,
    setError,
    clearError,
    updateProgress,
    reset,
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
