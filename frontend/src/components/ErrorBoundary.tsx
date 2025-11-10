'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertTriangle, Bug, Home, RefreshCw } from 'lucide-react'
import React, { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo, context?: any) => void
  autoRetry?: boolean
  maxRetries?: number
  retryDelay?: number
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
  retryCount: number
  isRetrying: boolean
  lastRetryTime: number
}

export class ErrorBoundary extends Component<Props, State> {
  private retryTimeoutRef: NodeJS.Timeout | null = null
  private errorCount = 0
  private lastErrorTime = 0

  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      retryCount: 0,
      isRetrying: false,
      lastRetryTime: 0
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
      retryCount: 0,
      isRetrying: false,
      lastRetryTime: 0
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    const now = Date.now()

    // Track error frequency
    if (now - this.lastErrorTime < 5000) { // Within 5 seconds
      this.errorCount++
    } else {
      this.errorCount = 1
    }
    this.lastErrorTime = now

    this.setState({ errorInfo })

    // Enhanced logging with context
    const errorContext = {
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack,
      },
      componentStack: errorInfo.componentStack,
      errorCount: this.errorCount,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    }

    console.error('🚨 ErrorBoundary caught an error:', errorContext)

    // Call optional error handler with enhanced context
    this.props.onError?.(error, errorInfo, errorContext)

    // Auto-retry for recoverable errors (not too frequent)
    if (this.errorCount < 3 && this.props.autoRetry !== false) {
      this.scheduleRetry()
    }

    // In production, send to error reporting service
    if (process.env.NODE_ENV === 'production') {
      this.reportError(errorContext)
    }
  }

  private scheduleRetry = () => {
    if (this.retryTimeoutRef) {
      clearTimeout(this.retryTimeoutRef)
    }

    this.setState({ isRetrying: true })

    // Exponential backoff: 1s, 2s, 4s...
    const delay = Math.min(1000 * Math.pow(2, this.state.retryCount), 10000)

    this.retryTimeoutRef = setTimeout(() => {
      this.setState(prev => ({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: prev.retryCount + 1,
        isRetrying: false,
        lastRetryTime: Date.now()
      }))
      this.errorCount = 0 // Reset error count on successful retry
    }, delay)
  }

  private reportError = (errorContext: any) => {
    // Example: Send to error reporting service
    try {
      // Sentry, LogRocket, or custom error reporting
      if (window.gtag) {
        window.gtag('event', 'exception', {
          description: errorContext.error.message,
          fatal: false,
        })
      }
    } catch (reportingError) {
      console.warn('Failed to report error:', reportingError)
    }
  }

  componentWillUnmount() {
    if (this.retryTimeoutRef) {
      clearTimeout(this.retryTimeoutRef)
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4" data-id="error-boundary">
          <Card className="max-w-2xl w-full bg-slate-900 border-slate-700" data-id="error-card">
            <CardHeader className="text-center" data-id="error-header">
              <div className="flex justify-center mb-4">
                {this.state.isRetrying ? (
                  <RefreshCw className="w-16 h-16 text-blue-500 animate-spin" data-id="retry-spinner" />
                ) : (
                  <AlertTriangle className="w-16 h-16 text-red-500" data-id="error-icon" />
                )}
              </div>
              <CardTitle className="text-2xl text-white mb-2" data-id="error-title">
                {this.state.isRetrying ? 'Retrying...' : 'Something went wrong'}
              </CardTitle>
              <CardDescription className="text-slate-300" data-id="error-description">
                {this.state.isRetrying
                  ? `Attempting to recover... (${this.state.retryCount}/${this.props.maxRetries || 3})`
                  : 'An unexpected error occurred. This has been logged and our team has been notified.'
                }
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6" data-id="error-content">
              {/* Retry Progress */}
              {this.state.isRetrying && (
                <div className="bg-blue-950/20 border border-blue-800/30 rounded-lg p-4" data-id="retry-progress">
                  <div className="flex items-center space-x-2 mb-2">
                    <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />
                    <span className="text-sm font-medium text-blue-400">Auto-retrying...</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{
                        width: `${((this.state.retryCount + 1) / (this.props.maxRetries || 3)) * 100}%`
                      }}
                      data-id="retry-progress-bar"
                    />
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Retry {this.state.retryCount + 1} of {this.props.maxRetries || 3}
                  </p>
                </div>
              )}

              {/* Error Details */}
              {!this.state.isRetrying && (
                <div className="bg-slate-800 rounded-lg p-4 border border-slate-700" data-id="error-details">
                  <div className="flex items-center space-x-2 mb-2">
                    <Bug className="w-4 h-4 text-red-400" />
                    <span className="text-sm font-medium text-white">Error Details</span>
                  </div>
                  <div className="text-xs text-slate-400 font-mono bg-slate-900 p-2 rounded overflow-auto max-h-32" data-id="error-message">
                    {this.state.error?.message || 'Unknown error'}
                  </div>
                  {this.state.retryCount > 0 && (
                    <div className="mt-2 text-xs text-yellow-400" data-id="retry-info">
                      Previous retry attempts: {this.state.retryCount}
                    </div>
                  )}
                  {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                    <details className="mt-2" data-id="error-stack-trace">
                      <summary className="text-xs text-slate-400 cursor-pointer hover:text-white">
                        Stack Trace (Development Only)
                      </summary>
                      <pre className="text-xs text-slate-500 mt-2 whitespace-pre-wrap font-mono bg-slate-900 p-2 rounded overflow-auto max-h-48">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </details>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center" data-id="error-actions">
                {!this.state.isRetrying && (
                  <>
                    <Button
                      onClick={this.handleRetry}
                      className="bg-blue-600 hover:bg-blue-700 text-white"
                      data-id="error-retry-button"
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Try Again
                    </Button>

                    <Button
                      onClick={this.handleGoHome}
                      variant="outline"
                      className="border-slate-600 text-slate-300 hover:bg-slate-800"
                      data-id="error-home-button"
                    >
                      <Home className="w-4 h-4 mr-2" />
                      Go Home
                    </Button>
                  </>
                )}
              </div>

              {/* Recovery Suggestions */}
              {!this.state.isRetrying && (
                <div className="bg-blue-950/20 border border-blue-800/30 rounded-lg p-4" data-id="recovery-suggestions">
                  <h4 className="text-sm font-medium text-blue-400 mb-2">
                    What you can try:
                  </h4>
                  <ul className="text-xs text-slate-300 space-y-1">
                    <li>• Refresh the page to reload the application</li>
                    <li>• Clear your browser cache and cookies</li>
                    <li>• Try using a different browser</li>
                    <li>• Check your internet connection</li>
                    {this.errorCount >= 3 && (
                      <li>• Contact support if the problem persists</li>
                    )}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

// Specialized error boundary for specific sections
export const AgentErrorBoundary: React.FC<{ children: ReactNode }> = ({ children }) => (
  <ErrorBoundary
    fallback={
      <Card className="bg-red-950/20 border-red-800/30">
        <CardHeader>
          <CardTitle className="text-red-400 flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5" />
            <span>Agent System Error</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-300 mb-4">
            The agent management system encountered an error. Please try refreshing the page.
          </p>
          <Button onClick={() => window.location.reload()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Page
          </Button>
        </CardContent>
      </Card>
    }
    onError={(error, errorInfo) => {
      console.error('Agent System Error:', error, errorInfo)
      // Could send to monitoring service
    }}
  >
    {children}
  </ErrorBoundary>
)

// Loading boundary for async operations
export const LoadingBoundary: React.FC<{
  children: ReactNode
  loading: boolean
  error?: Error | null
  onRetry?: () => void
  loadingMessage?: string
}> = ({ children, loading, error, onRetry, loadingMessage = 'Loading...' }) => {
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        <AlertTriangle className="w-8 h-8 text-red-500" />
        <p className="text-slate-300 text-center">
          {error.message || 'An error occurred while loading'}
        </p>
        {onRetry && (
          <Button onClick={onRetry} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <p className="text-slate-300">{loadingMessage}</p>
      </div>
    )
  }

  return <>{children}</>
}
