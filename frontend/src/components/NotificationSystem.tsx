'use client'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { AnimatePresence, motion } from 'framer-motion'
import {
    AlertTriangle,
    CheckCircle,
    Clock,
    Info,
    Shield,
    Wifi,
    X,
    XCircle,
    Zap
} from 'lucide-react'
import { createContext, ReactNode, useCallback, useContext, useEffect, useState } from 'react'

export type NotificationType =
  | 'success'
  | 'error'
  | 'warning'
  | 'info'
  | 'loading'
  | 'network'
  | 'security'
  | 'performance'

export type NotificationPriority = 'low' | 'normal' | 'high' | 'urgent'

export interface NotificationAction {
  label: string
  action: () => void
  variant?: 'default' | 'destructive' | 'outline' | 'secondary'
}

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  priority: NotificationPriority
  timestamp: Date
  duration?: number // in milliseconds
  actions?: NotificationAction[]
  persistent?: boolean // won't auto-dismiss
  category?: string // for grouping/filtering
  metadata?: Record<string, any>
}

interface NotificationContextType {
  notifications: Notification[]
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => string
  removeNotification: (id: string) => void
  clearNotifications: (type?: NotificationType) => void
  updateNotification: (id: string, updates: Partial<Notification>) => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider')
  }
  return context
}

const getNotificationIcon = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return CheckCircle
    case 'error':
      return XCircle
    case 'warning':
      return AlertTriangle
    case 'info':
      return Info
    case 'loading':
      return Clock
    case 'network':
      return Wifi
    case 'security':
      return Shield
    case 'performance':
      return Zap
    default:
      return Info
  }
}

const getNotificationColors = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return {
        bg: 'bg-green-950/20',
        border: 'border-green-800/30',
        icon: 'text-green-400',
        title: 'text-green-400',
        message: 'text-green-300'
      }
    case 'error':
      return {
        bg: 'bg-red-950/20',
        border: 'border-red-800/30',
        icon: 'text-red-400',
        title: 'text-red-400',
        message: 'text-red-300'
      }
    case 'warning':
      return {
        bg: 'bg-yellow-950/20',
        border: 'border-yellow-800/30',
        icon: 'text-yellow-400',
        title: 'text-yellow-400',
        message: 'text-yellow-300'
      }
    case 'info':
      return {
        bg: 'bg-blue-950/20',
        border: 'border-blue-800/30',
        icon: 'text-blue-400',
        title: 'text-blue-400',
        message: 'text-blue-300'
      }
    case 'loading':
      return {
        bg: 'bg-slate-950/20',
        border: 'border-slate-800/30',
        icon: 'text-slate-400',
        title: 'text-slate-400',
        message: 'text-slate-300'
      }
    case 'network':
      return {
        bg: 'bg-cyan-950/20',
        border: 'border-cyan-800/30',
        icon: 'text-cyan-400',
        title: 'text-cyan-400',
        message: 'text-cyan-300'
      }
    case 'security':
      return {
        bg: 'bg-purple-950/20',
        border: 'border-purple-800/30',
        icon: 'text-purple-400',
        title: 'text-purple-400',
        message: 'text-purple-300'
      }
    case 'performance':
      return {
        bg: 'bg-orange-950/20',
        border: 'border-orange-800/30',
        icon: 'text-orange-400',
        title: 'text-orange-400',
        message: 'text-orange-300'
      }
    default:
      return {
        bg: 'bg-slate-950/20',
        border: 'border-slate-800/30',
        icon: 'text-slate-400',
        title: 'text-slate-400',
        message: 'text-slate-300'
      }
  }
}

const getPriorityBadge = (priority: NotificationPriority) => {
  switch (priority) {
    case 'urgent':
      return <Badge variant="destructive" className="text-xs">URGENT</Badge>
    case 'high':
      return <Badge variant="destructive" className="text-xs bg-red-600">HIGH</Badge>
    case 'normal':
      return <Badge variant="secondary" className="text-xs">NORMAL</Badge>
    case 'low':
      return <Badge variant="outline" className="text-xs">LOW</Badge>
    default:
      return null
  }
}

interface NotificationItemProps {
  notification: Notification
  onRemove: (id: string) => void
  onAction?: (action: NotificationAction) => void
}

const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  onRemove,
  onAction
}) => {
  const colors = getNotificationColors(notification.type)
  const Icon = getNotificationIcon(notification.type)

  return (
    <motion.div
      initial={{ opacity: 0, y: -50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.95 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`relative max-w-md w-full ${colors.bg} border ${colors.border} rounded-lg p-4 shadow-xl backdrop-blur-sm pointer-events-auto`}
    >
      {/* Close button */}
      <button
        onClick={() => onRemove(notification.id)}
        className="absolute top-2 right-2 text-slate-400 hover:text-white transition-colors"
        aria-label="Close notification"
      >
        <X className="w-4 h-4" />
      </button>

      <div className="flex items-start space-x-3">
        {/* Icon */}
        <div className={`flex-shrink-0 ${colors.icon}`}>
          <Icon className="w-5 h-5" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <h4 className={`text-sm font-semibold ${colors.title} truncate`}>
              {notification.title}
            </h4>
            {getPriorityBadge(notification.priority)}
          </div>

          <p className={`text-sm ${colors.message} leading-relaxed`}>
            {notification.message}
          </p>

          {/* Timestamp */}
          <div className="flex items-center space-x-2 mt-2">
            <span className="text-xs text-slate-500">
              {notification.timestamp.toLocaleTimeString()}
            </span>
            {notification.category && (
              <Badge variant="outline" className="text-xs">
                {notification.category}
              </Badge>
            )}
          </div>

          {/* Actions */}
          {notification.actions && notification.actions.length > 0 && (
            <div className="flex space-x-2 mt-3">
              {notification.actions.map((action, index) => (
                <Button
                  key={index}
                  onClick={() => onAction?.(action)}
                  variant={action.variant || 'outline'}
                  size="sm"
                  className="text-xs h-7"
                >
                  {action.label}
                </Button>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export const NotificationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([])

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp'>): string => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: new Date(),
    }

    setNotifications(prev => {
      // Remove duplicate notifications of the same type and title
      const filtered = prev.filter(n =>
        !(n.type === notification.type && n.title === notification.title && n.message === notification.message)
      )
      return [...filtered, newNotification]
    })

    // Auto-dismiss non-persistent notifications
    if (!newNotification.persistent) {
      const duration = newNotification.duration ||
        (newNotification.priority === 'urgent' ? 10000 :
         newNotification.priority === 'high' ? 7000 :
         newNotification.priority === 'normal' ? 5000 : 3000)

      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }, [])

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const clearNotifications = useCallback((type?: NotificationType) => {
    if (type) {
      setNotifications(prev => prev.filter(n => n.type !== type))
    } else {
      setNotifications([])
    }
  }, [])

  const updateNotification = useCallback((id: string, updates: Partial<Notification>) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, ...updates } : n)
    )
  }, [])

  // Keyboard shortcut to clear all notifications (Ctrl+K)
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.ctrlKey && event.key === 'k') {
        event.preventDefault()
        clearNotifications()
      }
    }

    document.addEventListener('keydown', handleKeyPress)
    return () => document.removeEventListener('keydown', handleKeyPress)
  }, [clearNotifications])

  const value: NotificationContextType = {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    updateNotification,
  }

  return (
    <NotificationContext.Provider value={value}>
      {children}

      {/* Notification Container - Non-intrusive positioning */}
      <div
        className="fixed top-4 right-4 z-40 space-y-2 max-w-sm pointer-events-none"
        style={{ pointerEvents: 'auto' }}
      >
        <AnimatePresence>
          {notifications.map(notification => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onRemove={removeNotification}
              onAction={(action) => {
                action.action()
                removeNotification(notification.id)
              }}
            />
          ))}
        </AnimatePresence>
      </div>
    </NotificationContext.Provider>
  )
}

// Convenience hooks for common notification types
export const useSuccessNotification = () => {
  const { addNotification } = useNotifications()
  return useCallback((title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({
      type: 'success',
      title,
      message,
      priority: 'normal',
      ...options,
    })
  }, [addNotification])
}

export const useErrorNotification = () => {
  const { addNotification } = useNotifications()
  return useCallback((title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({
      type: 'error',
      title,
      message,
      priority: 'high',
      ...options,
    })
  }, [addNotification])
}

export const useWarningNotification = () => {
  const { addNotification } = useNotifications()
  return useCallback((title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({
      type: 'warning',
      title,
      message,
      priority: 'normal',
      ...options,
    })
  }, [addNotification])
}

export const useInfoNotification = () => {
  const { addNotification } = useNotifications()
  return useCallback((title: string, message: string, options?: Partial<Notification>) => {
    return addNotification({
      type: 'info',
      title,
      message,
      priority: 'low',
      ...options,
    })
  }, [addNotification])
}
