'use client'

import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { FieldValidation } from '@/hooks/useFormValidation'
import { cn } from '@/lib/utils'
import { AlertCircle, AlertTriangle, CheckCircle, Info } from 'lucide-react'
import React, { ReactNode, useId } from 'react'

interface FormFieldProps {
  label?: string
  description?: string
  error?: string
  warning?: string
  info?: string
  required?: boolean
  children: ReactNode
  className?: string
  validation?: FieldValidation
  helpText?: string
  tooltip?: string
  layout?: 'vertical' | 'horizontal'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  description,
  error,
  warning,
  info,
  required,
  children,
  className,
  validation,
  helpText,
  tooltip,
  layout = 'vertical',
  size = 'md',
  disabled,
}) => {
  const fieldId = useId()
  const labelId = `${fieldId}-label`
  const descriptionId = `${fieldId}-description`
  const errorId = `${fieldId}-error`
  const helpId = `${fieldId}-help`

  const hasError = error || (validation?.errors && validation.errors.length > 0)
  const hasWarning = warning || (validation?.warnings && validation.warnings.length > 0)
  const hasInfo = info || (validation?.infos && validation.infos.length > 0)
  const isValid = validation?.isValid && validation.isDirty
  const isTouched = validation?.isTouched

  const sizeClasses = {
    sm: 'space-y-1',
    md: 'space-y-2',
    lg: 'space-y-3',
  }

  const layoutClasses = {
    vertical: 'flex flex-col',
    horizontal: 'flex flex-col sm:flex-row sm:items-start sm:space-x-4',
  }

  return (
    <div className={cn(
      'form-field',
      sizeClasses[size],
      layoutClasses[layout],
      disabled && 'opacity-60 cursor-not-allowed',
      className
    )}>
      {/* Label */}
      {label && (
        <Label
          id={labelId}
          htmlFor={fieldId}
          className={cn(
            'text-sm font-medium text-slate-200 flex items-center space-x-2',
            hasError && 'text-red-400',
            hasWarning && !hasError && 'text-yellow-400',
            isValid && !hasError && !hasWarning && 'text-green-400'
          )}
        >
          <span>{label}</span>
          {required && (
            <Badge variant="destructive" className="text-xs px-1 py-0 h-4">
              *
            </Badge>
          )}
          {tooltip && (
            <span title={tooltip}>
              <Info className="w-3 h-3 text-slate-400" />
            </span>
          )}
        </Label>
      )}

      {/* Field Container */}
      <div className="flex-1">
        {/* Description */}
        {description && (
          <p
            id={descriptionId}
            className="text-sm text-slate-400 mb-2"
          >
            {description}
          </p>
        )}

        {/* Input Field with Status Indicator */}
        <div className="relative">
          {React.cloneElement(children as React.ReactElement, {
            id: fieldId,
            'aria-labelledby': label ? labelId : undefined,
            'aria-describedby': [
              description && descriptionId,
              hasError && errorId,
              helpText && helpId,
            ].filter(Boolean).join(' ') || undefined,
            'aria-invalid': hasError,
            'aria-required': required,
            disabled,
            className: cn(
              (children as React.ReactElement).props.className,
              hasError && 'border-red-500 focus:border-red-500 focus:ring-red-500',
              hasWarning && !hasError && 'border-yellow-500 focus:border-yellow-500 focus:ring-yellow-500',
              isValid && !hasError && !hasWarning && 'border-green-500 focus:border-green-500 focus:ring-green-500',
            )
          })}

          {/* Status Icon */}
          {(hasError || hasWarning || isValid) && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              {hasError && <AlertCircle className="w-4 h-4 text-red-500" />}
              {hasWarning && !hasError && <AlertTriangle className="w-4 h-4 text-yellow-500" />}
              {isValid && !hasError && !hasWarning && <CheckCircle className="w-4 h-4 text-green-500" />}
            </div>
          )}
        </div>

        {/* Validation Messages */}
        <div className="mt-2 space-y-1">
          {/* Errors */}
          {hasError && (
            <div id={errorId} className="flex items-start space-x-2 text-sm">
              <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
              <div className="text-red-400">
                {error || validation?.errors[0]}
              </div>
            </div>
          )}

          {/* Warnings */}
          {hasWarning && !hasError && (
            <div className="flex items-start space-x-2 text-sm">
              <AlertTriangle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
              <div className="text-yellow-400">
                {warning || validation?.warnings[0]}
              </div>
            </div>
          )}

          {/* Info */}
          {hasInfo && (
            <div className="flex items-start space-x-2 text-sm">
              <Info className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
              <div className="text-blue-400">
                {info || validation?.infos[0]}
              </div>
            </div>
          )}

          {/* Success */}
          {isValid && isTouched && !hasError && !hasWarning && (
            <div className="flex items-start space-x-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
              <div className="text-green-400">
                Looks good!
              </div>
            </div>
          )}

          {/* Help Text */}
          {helpText && (
            <div id={helpId} className="flex items-start space-x-2 text-sm">
              <Info className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
              <div className="text-slate-400">
                {helpText}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Specialized form field for different input types
export const TextField: React.FC<Omit<FormFieldProps, 'children'> & {
  type?: 'text' | 'email' | 'password' | 'url' | 'tel' | 'search'
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onBlur?: () => void
  icon?: ReactNode
  maxLength?: number
}> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  onBlur,
  icon,
  maxLength,
  ...fieldProps
}) => {
  const fieldId = useId()

  return (
    <FormField {...fieldProps}>
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {icon}
          </div>
        )}
        <input
          id={fieldId}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          onBlur={onBlur}
          maxLength={maxLength}
          className={cn(
            "flex h-10 w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white ring-offset-slate-900 file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors",
            icon && "pl-10"
          )}
        />
        {maxLength && value && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500">
            {value.length}/{maxLength}
          </div>
        )}
      </div>
    </FormField>
  )
}

export const TextareaField: React.FC<Omit<FormFieldProps, 'children'> & {
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onBlur?: () => void
  rows?: number
  maxLength?: number
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
}> = ({
  placeholder,
  value,
  onChange,
  onBlur,
  rows = 3,
  maxLength,
  resize = 'vertical',
  ...fieldProps
}) => {
  const fieldId = useId()

  return (
    <FormField {...fieldProps}>
      <div className="relative">
        <textarea
          id={fieldId}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          onBlur={onBlur}
          rows={rows}
          maxLength={maxLength}
          className={cn(
            "flex min-h-[80px] w-full rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white ring-offset-slate-900 placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors",
            resize === 'none' && 'resize-none',
            resize === 'vertical' && 'resize-vertical',
            resize === 'horizontal' && 'resize-horizontal',
            resize === 'both' && 'resize'
          )}
        />
        {maxLength && value && (
          <div className="absolute right-3 bottom-3 text-xs text-slate-500">
            {value.length}/{maxLength}
          </div>
        )}
      </div>
    </FormField>
  )
}

export const SelectField: React.FC<Omit<FormFieldProps, 'children'> & {
  placeholder?: string
  value?: string
  onChange?: (value: string) => void
  onBlur?: () => void
  options: Array<{ value: string; label: string; disabled?: boolean }>
  multiple?: boolean
}> = ({
  placeholder,
  value,
  onChange,
  onBlur,
  options,
  multiple = false,
  ...fieldProps
}) => {
  const fieldId = useId()

  return (
    <FormField {...fieldProps}>
      <select
        id={fieldId}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        onBlur={onBlur}
        multiple={multiple}
        className="flex h-10 w-full items-center justify-between rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1 hover:bg-slate-700 transition-colors"
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
            className="bg-slate-800 text-white hover:bg-slate-700"
          >
            {option.label}
          </option>
        ))}
      </select>
    </FormField>
  )
}
