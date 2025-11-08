import { RefObject, useCallback, useEffect, useRef } from 'react'

export type FocusableElement = HTMLElement | SVGElement

export interface KeyboardNavigationOptions {
  loop?: boolean
  vertical?: boolean
  horizontal?: boolean
  activateOnFocus?: boolean
  preventDefault?: boolean
  onEnter?: (element: FocusableElement) => void
  onEscape?: (element: FocusableElement) => void
  onArrowUp?: (element: FocusableElement) => void
  onArrowDown?: (element: FocusableElement) => void
  onArrowLeft?: (element: FocusableElement) => void
  onArrowRight?: (element: FocusableElement) => void
  onTab?: (element: FocusableElement) => void
  onShiftTab?: (element: FocusableElement) => void
}

export const FOCUSABLE_SELECTORS = [
  'a[href]',
  'area[href]',
  'input:not([disabled]):not([type="hidden"])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  'button:not([disabled])',
  'iframe',
  'object',
  'embed',
  '[contenteditable]',
  '[tabindex]:not([tabindex="-1"])'
].join(', ')

// Get all focusable elements within a container
export const getFocusableElements = (
  container: Element | Document = document
): FocusableElement[] => {
  return Array.from(container.querySelectorAll(FOCUSABLE_SELECTORS))
    .filter((element) => {
      const htmlElement = element as HTMLElement
      return !htmlElement.hasAttribute('inert') &&
             !htmlElement.hasAttribute('aria-hidden') &&
             htmlElement.offsetWidth > 0 &&
             htmlElement.offsetHeight > 0 &&
             window.getComputedStyle(htmlElement).visibility !== 'hidden'
    }) as FocusableElement[]
}

// Focus management utilities
export const focusElement = (element: FocusableElement | null) => {
  if (element && typeof element.focus === 'function') {
    element.focus()
  }
}

export const isFocusable = (element: Element): boolean => {
  return getFocusableElements().includes(element as FocusableElement)
}

export const getNextFocusableElement = (
  currentElement: FocusableElement,
  direction: 'next' | 'previous' = 'next',
  container?: Element
): FocusableElement | null => {
  const focusableElements = getFocusableElements(container)
  const currentIndex = focusableElements.indexOf(currentElement)

  if (currentIndex === -1) return null

  if (direction === 'next') {
    return focusableElements[currentIndex + 1] || focusableElements[0] || null
  } else {
    return focusableElements[currentIndex - 1] || focusableElements[focusableElements.length - 1] || null
  }
}

// Hook for keyboard navigation within a container
export const useKeyboardNavigation = (
  containerRef: RefObject<HTMLElement>,
  options: KeyboardNavigationOptions = {}
) => {
  const {
    loop = true,
    vertical = true,
    horizontal = false,
    activateOnFocus = false,
    preventDefault = true,
    onEnter,
    onEscape,
    onArrowUp,
    onArrowDown,
    onArrowLeft,
    onArrowRight,
    onTab,
    onShiftTab,
  } = options

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    const target = event.target as FocusableElement
    const container = containerRef.current

    if (!container || !container.contains(target)) return

    const focusableElements = getFocusableElements(container)
    const currentIndex = focusableElements.indexOf(target)

    switch (event.key) {
      case 'Enter':
        if (onEnter) {
          onEnter(target)
          if (preventDefault) event.preventDefault()
        }
        break

      case 'Escape':
        if (onEscape) {
          onEscape(target)
          if (preventDefault) event.preventDefault()
        }
        break

      case 'ArrowUp':
        if (vertical) {
          const nextElement = getNextFocusableElement(target, 'previous', container)
          if (nextElement) {
            focusElement(nextElement)
            onArrowUp?.(nextElement)
            if (preventDefault) event.preventDefault()
          } else if (loop && focusableElements.length > 0) {
            focusElement(focusableElements[focusableElements.length - 1])
            onArrowUp?.(focusableElements[focusableElements.length - 1])
            if (preventDefault) event.preventDefault()
          }
        }
        break

      case 'ArrowDown':
        if (vertical) {
          const nextElement = getNextFocusableElement(target, 'next', container)
          if (nextElement) {
            focusElement(nextElement)
            onArrowDown?.(nextElement)
            if (preventDefault) event.preventDefault()
          } else if (loop && focusableElements.length > 0) {
            focusElement(focusableElements[0])
            onArrowDown?.(focusableElements[0])
            if (preventDefault) event.preventDefault()
          }
        }
        break

      case 'ArrowLeft':
        if (horizontal) {
          const nextElement = getNextFocusableElement(target, 'previous', container)
          if (nextElement) {
            focusElement(nextElement)
            onArrowLeft?.(nextElement)
            if (preventDefault) event.preventDefault()
          } else if (loop && focusableElements.length > 0) {
            focusElement(focusableElements[focusableElements.length - 1])
            onArrowLeft?.(focusableElements[focusableElements.length - 1])
            if (preventDefault) event.preventDefault()
          }
        }
        break

      case 'ArrowRight':
        if (horizontal) {
          const nextElement = getNextFocusableElement(target, 'next', container)
          if (nextElement) {
            focusElement(nextElement)
            onArrowRight?.(nextElement)
            if (preventDefault) event.preventDefault()
          } else if (loop && focusableElements.length > 0) {
            focusElement(focusableElements[0])
            onArrowRight?.(focusableElements[0])
            if (preventDefault) event.preventDefault()
          }
        }
        break

      case 'Tab':
        if (event.shiftKey) {
          if (onShiftTab) {
            onShiftTab(target)
          }
        } else {
          if (onTab) {
            onTab(target)
          }
        }
        break
    }
  }, [
    containerRef,
    loop,
    vertical,
    horizontal,
    preventDefault,
    onEnter,
    onEscape,
    onArrowUp,
    onArrowDown,
    onArrowLeft,
    onArrowRight,
    onTab,
    onShiftTab,
  ])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    container.addEventListener('keydown', handleKeyDown)
    return () => {
      container.removeEventListener('keydown', handleKeyDown)
    }
  }, [containerRef, handleKeyDown])

  // Focus management methods
  const focusFirst = useCallback(() => {
    const container = containerRef.current
    if (!container) return

    const focusableElements = getFocusableElements(container)
    if (focusableElements.length > 0) {
      focusElement(focusableElements[0])
    }
  }, [containerRef])

  const focusLast = useCallback(() => {
    const container = containerRef.current
    if (!container) return

    const focusableElements = getFocusableElements(container)
    if (focusableElements.length > 0) {
      focusElement(focusableElements[focusableElements.length - 1])
    }
  }, [containerRef])

  const focusNext = useCallback(() => {
    const container = containerRef.current
    if (!container) return

    const activeElement = document.activeElement as FocusableElement
    if (!activeElement || !container.contains(activeElement)) {
      focusFirst()
      return
    }

    const nextElement = getNextFocusableElement(activeElement, 'next', container)
    if (nextElement) {
      focusElement(nextElement)
    } else if (loop) {
      focusFirst()
    }
  }, [containerRef, focusFirst, loop])

  const focusPrevious = useCallback(() => {
    const container = containerRef.current
    if (!container) return

    const activeElement = document.activeElement as FocusableElement
    if (!activeElement || !container.contains(activeElement)) {
      focusLast()
      return
    }

    const previousElement = getNextFocusableElement(activeElement, 'previous', container)
    if (previousElement) {
      focusElement(previousElement)
    } else if (loop) {
      focusLast()
    }
  }, [containerRef, focusLast, loop])

  return {
    focusFirst,
    focusLast,
    focusNext,
    focusPrevious,
  }
}

// Hook for managing focus traps (modals, dropdowns, etc.)
export const useFocusTrap = (
  containerRef: RefObject<HTMLElement>,
  options: {
    active?: boolean
    restoreFocus?: boolean
    initialFocusRef?: RefObject<HTMLElement>
  } = {}
) => {
  const { active = true, restoreFocus = true, initialFocusRef } = options
  const previouslyFocusedElementRef = useRef<FocusableElement | null>(null)

  const trapFocus = useCallback((event: KeyboardEvent) => {
    if (!active || event.key !== 'Tab') return

    const container = containerRef.current
    if (!container) return

    const focusableElements = getFocusableElements(container)
    if (focusableElements.length === 0) return

    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]
    const activeElement = document.activeElement as FocusableElement

    if (event.shiftKey) {
      // Shift + Tab
      if (activeElement === firstElement) {
        event.preventDefault()
        focusElement(lastElement)
      }
    } else {
      // Tab
      if (activeElement === lastElement) {
        event.preventDefault()
        focusElement(firstElement)
      }
    }
  }, [active, containerRef])

  const activateTrap = useCallback(() => {
    if (!active) return

    // Store the currently focused element to restore later
    if (restoreFocus) {
      previouslyFocusedElementRef.current = document.activeElement as FocusableElement
    }

    // Focus the initial element
    const container = containerRef.current
    if (container) {
      let elementToFocus: HTMLElement | null = initialFocusRef?.current || null

      if (!elementToFocus) {
        const focusableElements = getFocusableElements(container)
        elementToFocus = (focusableElements[0] as HTMLElement) || container
      }

      if (elementToFocus) {
        focusElement(elementToFocus)
      }
    }

    // Add global keydown listener for tab navigation
    document.addEventListener('keydown', trapFocus)
  }, [active, restoreFocus, initialFocusRef, containerRef, trapFocus])

  const deactivateTrap = useCallback(() => {
    document.removeEventListener('keydown', trapFocus)

    // Restore focus to the previously focused element
    if (restoreFocus && previouslyFocusedElementRef.current) {
      focusElement(previouslyFocusedElementRef.current)
      previouslyFocusedElementRef.current = null
    }
  }, [restoreFocus, trapFocus])

  useEffect(() => {
    if (active) {
      activateTrap()
    } else {
      deactivateTrap()
    }

    return () => {
      deactivateTrap()
    }
  }, [active, activateTrap, deactivateTrap])

  return {
    activateTrap,
    deactivateTrap,
  }
}

// Hook for managing skip links (accessibility)
export const useSkipLinks = () => {
  const skipToContent = useCallback((targetId: string) => {
    const target = document.getElementById(targetId)
    if (target) {
      target.focus()
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, [])

  const skipToNavigation = useCallback(() => {
    skipToContent('main-navigation')
  }, [skipToContent])

  const skipToMain = useCallback(() => {
    skipToContent('main-content')
  }, [skipToContent])

  return {
    skipToContent,
    skipToNavigation,
    skipToMain,
  }
}

// Hook for announcing content changes to screen readers
export const useScreenReaderAnnouncement = () => {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div')
    announcement.setAttribute('aria-live', priority)
    announcement.setAttribute('aria-atomic', 'true')
    announcement.style.position = 'absolute'
    announcement.style.left = '-10000px'
    announcement.style.width = '1px'
    announcement.style.height = '1px'
    announcement.style.overflow = 'hidden'

    document.body.appendChild(announcement)
    announcement.textContent = message

    // Remove after announcement
    setTimeout(() => {
      if (announcement.parentNode) {
        announcement.parentNode.removeChild(announcement)
      }
    }, 1000)
  }, [])

  const announceError = useCallback((message: string) => {
    announce(`Error: ${message}`, 'assertive')
  }, [announce])

  const announceSuccess = useCallback((message: string) => {
    announce(`Success: ${message}`, 'polite')
  }, [announce])

  const announceLoading = useCallback((message: string) => {
    announce(`Loading: ${message}`, 'polite')
  }, [announce])

  const announceNavigation = useCallback((location: string) => {
    announce(`Navigated to ${location}`, 'polite')
  }, [announce])

  return {
    announce,
    announceError,
    announceSuccess,
    announceLoading,
    announceNavigation,
  }
}

// Global keyboard shortcuts hook
export const useKeyboardShortcuts = (
  shortcuts: Record<string, (event: KeyboardEvent) => void>
) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const keys = []

      if (event.ctrlKey || event.metaKey) keys.push('ctrl')
      if (event.shiftKey) keys.push('shift')
      if (event.altKey) keys.push('alt')
      keys.push(event.key.toLowerCase())

      const shortcut = keys.join('+')
      const handler = shortcuts[shortcut]

      if (handler) {
        event.preventDefault()
        handler(event)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [shortcuts])
}
