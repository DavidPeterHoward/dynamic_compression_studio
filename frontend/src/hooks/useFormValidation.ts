import { useCallback, useMemo, useState } from 'react'

export type ValidationRule<T = any> = {
  validate: (value: T, formData?: Record<string, any>) => boolean | Promise<boolean>
  message: string
  type?: 'error' | 'warning' | 'info'
  priority?: number
}

export type FieldValidation = {
  isValid: boolean
  isDirty: boolean
  isTouched: boolean
  errors: string[]
  warnings: string[]
  infos: string[]
}

export type FormValidationState = Record<string, FieldValidation>

export type ValidationOptions = {
  validateOnChange?: boolean
  validateOnBlur?: boolean
  validateOnSubmit?: boolean
  debounceMs?: number
  showMultipleErrors?: boolean
}

export const useFormValidation = <T extends Record<string, any>>(
  initialValues: T,
  validationRules: Record<keyof T, ValidationRule[]>,
  options: ValidationOptions = {}
) => {
  const {
    validateOnChange = true,
    validateOnBlur = true,
    validateOnSubmit = true,
    debounceMs = 300,
    showMultipleErrors = true,
  } = options

  const [values, setValues] = useState<T>(initialValues)
  const [validationState, setValidationState] = useState<FormValidationState>(() =>
    Object.keys(initialValues).reduce((acc, key) => ({
      ...acc,
      [key]: {
        isValid: true,
        isDirty: false,
        isTouched: false,
        errors: [],
        warnings: [],
        infos: [],
      }
    }), {})
  )

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitCount, setSubmitCount] = useState(0)

  // Validate a single field
  const validateField = useCallback(async (fieldName: keyof T, value: any, formData: T = values) => {
    const rules = validationRules[fieldName] || []
    const errors: string[] = []
    const warnings: string[] = []
    const infos: string[] = []

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

    setValidationState(prev => ({
      ...prev,
      [fieldName]: {
        isValid,
        isDirty: true,
        isTouched: (prev as any)[fieldName]?.isTouched || false,
        errors,
        warnings,
        infos,
      }
    }))

    return { isValid, errors, warnings, infos }
  }, [validationRules, values, showMultipleErrors])

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
        }
      }), {})
    )
    setSubmitCount(0)
    setIsSubmitting(false)
  }, [initialValues])

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
    handleChange,
    handleBlur,
    handleSubmit,
    validateField,
    validateAll,
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
