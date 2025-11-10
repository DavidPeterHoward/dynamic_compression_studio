import { useCallback, useEffect, useMemo, useState } from 'react'

export type ValidationRule<T = any> = {
  validate: (value: T, formData?: Record<string, any>) => boolean | Promise<boolean>
  message: string
  type?: 'error' | 'warning' | 'info'
  priority?: number
  field?: string // For cross-field validation
  debounceMs?: number // Individual field debounce
}

export type ValidationResult = {
  isValid: boolean
  message: string
  type: 'error' | 'warning' | 'info'
  field?: string
}

export type FormRecoveryAction = {
  type: 'clear' | 'reset' | 'restore' | 'retry'
  field?: string
  value?: any
  description: string
}

export type FieldValidation = {
  isValid: boolean
  isDirty: boolean
  isTouched: boolean
  errors: string[]
  warnings: string[]
  infos: string[]
  recoveryActions: FormRecoveryAction[]
  lastValidated: Date | null
  validationAttempts: number
}

export type FormValidationState = Record<string, FieldValidation>

export type ValidationOptions = {
  validateOnChange?: boolean
  validateOnBlur?: boolean
  validateOnSubmit?: boolean
  debounceMs?: number
  showMultipleErrors?: boolean
}

export interface EnhancedValidationOptions extends ValidationOptions {
  enableRealTimeValidation?: boolean
  recoverySuggestions?: boolean
  persistState?: boolean
  storageKey?: string
  maxRecoveryAttempts?: number
}

export const useFormValidation = <T extends Record<string, any>>(
  initialValues: T,
  validationRules: Record<keyof T, ValidationRule[]>,
  options: EnhancedValidationOptions = {}
) => {
  const {
    validateOnChange = true,
    validateOnBlur = true,
    validateOnSubmit = true,
    debounceMs = 300,
    showMultipleErrors = true,
    enableRealTimeValidation = true,
    recoverySuggestions = true,
    persistState = false,
    storageKey,
    maxRecoveryAttempts = 3,
  } = options

  // Load persisted state
  const getPersistedState = useCallback(() => {
    if (persistState && storageKey && typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem(storageKey)
        return stored ? JSON.parse(stored) : null
      } catch {
        return null
      }
    }
    return null
  }, [persistState, storageKey])

  const [values, setValues] = useState<T>(() => {
    const persisted = getPersistedState()
    return persisted?.values || initialValues
  })

  const [validationState, setValidationState] = useState<FormValidationState>(() => {
    const persisted = getPersistedState()
    return persisted?.validationState || Object.keys(initialValues).reduce((acc, key) => ({
      ...acc,
      [key]: {
        isValid: true,
        isDirty: false,
        isTouched: false,
        errors: [],
        warnings: [],
        infos: [],
        recoveryActions: [],
        lastValidated: null,
        validationAttempts: 0,
      }
    }), {})
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitCount, setSubmitCount] = useState(0)
  const [recoveryHistory, setRecoveryHistory] = useState<FormRecoveryAction[]>([])

  // Generate recovery suggestions based on validation errors
  const generateRecoveryActions = useCallback((
    fieldName: keyof T,
    value: any,
    errors: string[]
  ): FormRecoveryAction[] => {
    const actions: FormRecoveryAction[] = []

    // Common recovery patterns
    if (errors.some(e => e.includes('required'))) {
      actions.push({
        type: 'clear',
        field: String(fieldName),
        description: 'Clear field and start over'
      })
    }

    if (errors.some(e => e.includes('email'))) {
      actions.push({
        type: 'restore',
        field: String(fieldName),
        value: value?.replace(/[^a-zA-Z0-9@._-]/g, '') || '',
        description: 'Remove special characters from email'
      })
    }

    if (errors.some(e => e.includes('JSON'))) {
      actions.push({
        type: 'reset',
        field: String(fieldName),
        value: '{}',
        description: 'Reset to valid JSON structure'
      })
    }

    if (errors.some(e => e.includes('length') || e.includes('characters'))) {
      const fieldRules = validationRules[fieldName] || []
      const minLengthRule = fieldRules.find(r => r.message.includes('at least'))
      if (minLengthRule) {
        actions.push({
          type: 'restore',
          field: String(fieldName),
          value: value || '',
          description: 'Field requires minimum length - please add more content'
        })
      }
    }

    return actions.slice(0, 3) // Limit to 3 suggestions
  }, [validationRules])

  // Validate a single field
  const validateField = useCallback(async (fieldName: keyof T, value: any, formData: T = values) => {
    const rules = validationRules[fieldName] || []
    const errors: string[] = []
    const warnings: string[] = []
    const infos: string[] = []

    const startTime = Date.now()

    for (const rule of rules) {
      try {
        const isValid = await rule.validate(value, formData)

        if (!isValid) {
          const message = rule.message
          switch (rule.type) {
            case 'warning':
              warnings.push(message)
              break
            case 'info':
              infos.push(message)
              break
            default:
              errors.push(message)
              break
          }

          // Stop at first error if not showing multiple errors
          if (!showMultipleErrors && errors.length > 0) break
        }
      } catch (error) {
        console.error(`Validation error for field ${String(fieldName)}:`, error)
        errors.push('Validation failed')
      }
    }

    const isValid = errors.length === 0
    const recoveryActions = recoverySuggestions && errors.length > 0
      ? generateRecoveryActions(fieldName, value, errors)
      : []

    setValidationState(prev => ({
      ...prev,
      [fieldName]: {
        isValid,
        isDirty: true,
        isTouched: (prev as any)[fieldName]?.isTouched || false,
        errors,
        warnings,
        infos,
        recoveryActions,
        lastValidated: new Date(),
        validationAttempts: ((prev as any)[fieldName]?.validationAttempts || 0) + 1,
      }
    }))

    // Persist state if enabled
    if (persistState && storageKey) {
      try {
        const stateToPersist = {
          values,
          validationState: {
            ...validationState,
            [fieldName]: {
              isValid,
              isDirty: true,
              isTouched: (validationState as any)[fieldName]?.isTouched || false,
              errors,
              warnings,
              infos,
              recoveryActions,
              lastValidated: new Date(),
              validationAttempts: ((validationState as any)[fieldName]?.validationAttempts || 0) + 1,
            }
          },
          timestamp: Date.now()
        }
        localStorage.setItem(storageKey, JSON.stringify(stateToPersist))
      } catch (error) {
        console.warn('Failed to persist form state:', error)
      }
    }

    return { isValid, errors, warnings, infos, recoveryActions }
  }, [validationRules, values, showMultipleErrors, recoverySuggestions, generateRecoveryActions, persistState, storageKey, validationState])

  // Validate all fields
  const validateAll = useCallback(async () => {
    const results = await Promise.all(
      Object.keys(values).map(async (fieldName) => {
        const key = fieldName as keyof T
        return { fieldName: key, ...await validateField(key, values[key]) }
      })
    )

    const allValid = results.every(result => result.isValid)
    const hasErrors = results.some(result => result.errors.length > 0)

    return { allValid, hasErrors, results }
  }, [values, validateField])

  // Handle field change
  const handleChange = useCallback(async (fieldName: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [fieldName]: value }))

    if (validateOnChange) {
      // Debounce validation
      setTimeout(() => {
        validateField(fieldName, value)
      }, debounceMs)
    }

    // Mark field as dirty
    setValidationState(prev => ({
      ...prev,
      [fieldName]: {
        ...(prev as any)[fieldName],
        isDirty: true,
      }
    }))
  }, [validateOnChange, debounceMs, validateField])

  // Handle field blur
  const handleBlur = useCallback(async (fieldName: keyof T) => {
    setValidationState(prev => ({
      ...prev,
      [fieldName]: {
        ...(prev as any)[fieldName],
        isTouched: true,
      }
    }))

    if (validateOnBlur) {
      await validateField(fieldName, values[fieldName])
    }
  }, [validateOnBlur, validateField, values])

  // Handle form submission
  const handleSubmit = useCallback(async (onSubmit: (values: T) => Promise<void> | void) => {
    setSubmitCount(prev => prev + 1)
    setIsSubmitting(true)

    try {
      let shouldSubmit = true

      if (validateOnSubmit) {
        const { allValid } = await validateAll()
        shouldSubmit = allValid
      }

      if (shouldSubmit) {
        await onSubmit(values)
      }
    } catch (error) {
      console.error('Form submission error:', error)
      // Error handling will be done by the caller
    } finally {
      setIsSubmitting(false)
    }
  }, [validateOnSubmit, validateAll, values])

  // Execute recovery action
  const executeRecoveryAction = useCallback((action: FormRecoveryAction) => {
    setRecoveryHistory(prev => [...prev, action])

    switch (action.type) {
      case 'clear':
        if (action.field) {
          setValues(prev => ({ ...prev, [action.field!]: '' }))
          setValidationState(prev => ({
            ...prev,
            [action.field!]: {
              ...prev[action.field!],
              isDirty: true,
              errors: [],
              warnings: [],
              infos: [],
              recoveryActions: [],
            }
          }))
        }
        break

      case 'reset':
        if (action.field && action.value !== undefined) {
          setValues(prev => ({ ...prev, [action.field!]: action.value }))
        }
        break

      case 'restore':
        if (action.field && action.value !== undefined) {
          setValues(prev => ({ ...prev, [action.field!]: action.value }))
        }
        break

      case 'retry':
        // Re-validate the field
        if (action.field) {
          const fieldValue = values[action.field as keyof T]
          validateField(action.field as keyof T, fieldValue)
        }
        break
    }
  }, [values, validateField])

  // Get recovery suggestions for a field
  const getRecoverySuggestions = useCallback((fieldName: keyof T) => {
    return validationState[fieldName]?.recoveryActions || []
  }, [validationState])

  // Get all recovery suggestions
  const getAllRecoverySuggestions = useCallback(() => {
    const suggestions: Array<{ field: string, actions: FormRecoveryAction[] }> = []

    Object.entries(validationState).forEach(([field, state]) => {
      if (state.recoveryActions.length > 0) {
        suggestions.push({ field, actions: state.recoveryActions })
      }
    })

    return suggestions
  }, [validationState])

  // Auto-recover common issues
  const autoRecover = useCallback(async () => {
    const allSuggestions = getAllRecoverySuggestions()
    const autoRecoverableActions = allSuggestions
      .flatMap(s => s.actions)
      .filter(action => ['clear', 'reset', 'restore'].includes(action.type))

    for (const action of autoRecoverableActions.slice(0, maxRecoveryAttempts)) {
      executeRecoveryAction(action)
      await new Promise(resolve => setTimeout(resolve, 100)) // Small delay
    }
  }, [getAllRecoverySuggestions, executeRecoveryAction, maxRecoveryAttempts])

  // Reset form
  const reset = useCallback((newValues?: Partial<T>) => {
    setValues({ ...initialValues, ...newValues })
    setValidationState(
      Object.keys(initialValues).reduce((acc, key) => ({
        ...acc,
        [key]: {
          isValid: true,
          isDirty: false,
          isTouched: false,
          errors: [],
          warnings: [],
          infos: [],
          recoveryActions: [],
          lastValidated: null,
          validationAttempts: 0,
        }
      }), {})
    )
    setSubmitCount(0)
    setIsSubmitting(false)
    setRecoveryHistory([])

    // Clear persisted state
    if (persistState && storageKey) {
      try {
        localStorage.removeItem(storageKey)
      } catch {
        // Ignore cleanup errors
      }
    }
  }, [initialValues, persistState, storageKey])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (persistState && storageKey) {
        // Optional: Keep state on unmount for session recovery
      }
    }
  }, [persistState, storageKey])

  // Computed values
  const isValid = useMemo(() =>
    Object.values(validationState).every(field => field.isValid),
    [validationState]
  )

  const isDirty = useMemo(() =>
    Object.values(validationState).some(field => field.isDirty),
    [validationState]
  )

  const isTouched = useMemo(() =>
    Object.values(validationState).some(field => field.isTouched),
    [validationState]
  )

  const hasErrors = useMemo(() =>
    Object.values(validationState).some(field => field.errors.length > 0),
    [validationState]
  )

  const hasWarnings = useMemo(() =>
    Object.values(validationState).some(field => field.warnings.length > 0),
    [validationState]
  )

  return {
    values,
    validationState,
    isValid,
    isDirty,
    isTouched,
    hasErrors,
    hasWarnings,
    isSubmitting,
    submitCount,
    recoveryHistory,
    handleChange,
    handleBlur,
    handleSubmit,
    validateField,
    validateAll,
    executeRecoveryAction,
    getRecoverySuggestions,
    getAllRecoverySuggestions,
    autoRecover,
    reset,
    setValues,
  }
}

// Common validation rules
export const validationRules = {
  required: (message = 'This field is required'): ValidationRule => ({
    validate: (value) => {
      if (typeof value === 'string') return value.trim().length > 0
      if (Array.isArray(value)) return value.length > 0
      return value != null && value !== ''
    },
    message,
    type: 'error',
    priority: 1,
  }),

  minLength: (min: number, message?: string): ValidationRule => ({
    validate: (value) => typeof value === 'string' && value.length >= min,
    message: message || `Must be at least ${min} characters`,
    type: 'error',
    priority: 2,
  }),

  maxLength: (max: number, message?: string): ValidationRule => ({
    validate: (value) => typeof value === 'string' && value.length <= max,
    message: message || `Must be no more than ${max} characters`,
    type: 'error',
    priority: 2,
  }),

  email: (message = 'Please enter a valid email address'): ValidationRule => ({
    validate: (value) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return typeof value === 'string' && emailRegex.test(value)
    },
    message,
    type: 'error',
    priority: 2,
  }),

  url: (message = 'Please enter a valid URL'): ValidationRule => ({
    validate: (value) => {
      try {
        new URL(value as string)
        return true
      } catch {
        return false
      }
    },
    message,
    type: 'error',
    priority: 2,
  }),

  pattern: (regex: RegExp, message: string): ValidationRule => ({
    validate: (value) => regex.test(value as string),
    message,
    type: 'error',
    priority: 2,
  }),

  numeric: (message = 'Please enter a valid number'): ValidationRule => ({
    validate: (value) => {
      const num = Number(value)
      return !isNaN(num) && isFinite(num)
    },
    message,
    type: 'error',
    priority: 2,
  }),

  min: (min: number, message?: string): ValidationRule => ({
    validate: (value) => Number(value) >= min,
    message: message || `Must be at least ${min}`,
    type: 'error',
    priority: 2,
  }),

  max: (max: number, message?: string): ValidationRule => ({
    validate: (value) => Number(value) <= max,
    message: message || `Must be no more than ${max}`,
    type: 'error',
    priority: 2,
  }),

  oneOf: (options: any[], message?: string): ValidationRule => ({
    validate: (value) => options.includes(value),
    message: message || `Must be one of: ${options.join(', ')}`,
    type: 'error',
    priority: 2,
  }),

  json: (message = 'Please enter valid JSON'): ValidationRule => ({
    validate: (value) => {
      try {
        JSON.parse(value as string)
        return true
      } catch {
        return false
      }
    },
    message,
    type: 'error',
    priority: 2,
  }),

  custom: (
    validator: (value: any, formData?: Record<string, any>) => boolean | Promise<boolean>,
    message: string,
    type: 'error' | 'warning' | 'info' = 'error'
  ): ValidationRule => ({
    validate: validator,
    message,
    type,
    priority: 3,
  }),
}
