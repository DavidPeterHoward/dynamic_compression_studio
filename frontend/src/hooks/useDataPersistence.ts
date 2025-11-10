import { useCallback, useEffect, useRef, useState } from 'react'

export type StorageType = 'localStorage' | 'sessionStorage' | 'indexedDB'

export interface PersistenceOptions {
  storageType?: StorageType
  key: string
  version?: number
  compress?: boolean
  encrypt?: boolean
  ttl?: number // Time to live in milliseconds
  maxSize?: number // Maximum size in bytes
  backupEnabled?: boolean
  recoveryEnabled?: boolean
}

export interface PersistenceMetadata {
  timestamp: number
  version: number
  size: number
  checksum?: string
  expiresAt?: number
}

export interface PersistedData<T = any> {
  data: T
  metadata: PersistenceMetadata
}

export interface RecoveryAction {
  type: 'restore' | 'merge' | 'overwrite' | 'discard'
  description: string
  data?: any
}

export const useDataPersistence = <T>(
  initialData: T,
  options: PersistenceOptions
) => {
  const {
    storageType = 'localStorage',
    key,
    version = 1,
    compress = false,
    encrypt = false,
    ttl,
    maxSize = 5 * 1024 * 1024, // 5MB default
    backupEnabled = true,
    recoveryEnabled = true,
  } = options || {}

  // Validate required parameters
  if (!key) {
    throw new Error('useDataPersistence: "key" is required in options')
  }

  const [data, setData] = useState<T>(initialData)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [recoveryActions, setRecoveryActions] = useState<RecoveryAction[]>([])

  const saveTimeoutRef = useRef<NodeJS.Timeout>()
  const isInitializedRef = useRef(false)

  // Get storage mechanism
  const getStorage = useCallback(() => {
    if (typeof window === 'undefined') {
      return null // Return null on server side
    }

    switch (storageType) {
      case 'sessionStorage':
        return sessionStorage
      case 'indexedDB':
        // IndexedDB implementation would go here
        throw new Error('IndexedDB not yet implemented')
      default:
        return localStorage
    }
  }, [storageType])

  // Generate checksum for data integrity
  const generateChecksum = useCallback((data: any): string => {
    const str = JSON.stringify(data)
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return hash.toString(16)
  }, [])

  // Compress data
  const compressData = useCallback(async (data: string): Promise<string> => {
    if (!compress) return data

    // Simple compression using built-in APIs
    const stream = new CompressionStream('gzip')
    const writer = stream.writable.getWriter()
    const reader = stream.readable.getReader()

    writer.write(new TextEncoder().encode(data))
    writer.close()

    const chunks = []
    let done = false

    while (!done) {
      const { value, done: readerDone } = await reader.read()
      done = readerDone
      if (value) chunks.push(value)
    }

    const compressed = new Uint8Array(chunks.reduce((acc, chunk) => acc + chunk.length, 0))
    let offset = 0
    for (const chunk of chunks) {
      compressed.set(chunk, offset)
      offset += chunk.length
    }

    return btoa(String.fromCharCode(...Array.from(compressed)))
  }, [compress])

  // Decompress data
  const decompressData = useCallback(async (compressedData: string): Promise<string> => {
    if (!compress) return compressedData

    try {
      const compressed = Uint8Array.from(atob(compressedData), c => c.charCodeAt(0))
      const stream = new DecompressionStream('gzip')
      const writer = stream.writable.getWriter()
      const reader = stream.readable.getReader()

      writer.write(compressed)
      writer.close()

      const chunks = []
      let done = false

      while (!done) {
        const { value, done: readerDone } = await reader.read()
        done = readerDone
        if (value) chunks.push(value)
      }

      const decompressed = new Uint8Array(chunks.reduce((acc, chunk) => acc + chunk.length, 0))
      let offset = 0
      for (const chunk of chunks) {
        decompressed.set(chunk, offset)
        offset += chunk.length
      }

      return new TextDecoder().decode(decompressed)
    } catch {
      // If decompression fails, return original data
      return compressedData
    }
  }, [compress])

  // Encrypt data (basic implementation)
  const encryptData = useCallback(async (data: string): Promise<string> => {
    if (!encrypt) return data

    // Simple XOR encryption for demonstration
    const key = 'dynamic-compression-key'
    let result = ''
    for (let i = 0; i < data.length; i++) {
      result += String.fromCharCode(data.charCodeAt(i) ^ key.charCodeAt(i % key.length))
    }
    return btoa(result)
  }, [encrypt])

  // Decrypt data
  const decryptData = useCallback(async (encryptedData: string): Promise<string> => {
    if (!encrypt) return encryptedData

    try {
      const decoded = atob(encryptedData)
      const key = 'dynamic-compression-key'
      let result = ''
      for (let i = 0; i < decoded.length; i++) {
        result += String.fromCharCode(decoded.charCodeAt(i) ^ key.charCodeAt(i % key.length))
      }
      return result
    } catch {
      return encryptedData
    }
  }, [encrypt])

  // Load data from storage
  const loadData = useCallback(async (): Promise<void> => {
    // Skip storage operations on server side
    if (typeof window === 'undefined') {
      setIsLoading(false)
      isInitializedRef.current = true
      return
    }

    try {
      const storage = getStorage()
      if (!storage) return // Skip if no storage available (server side)

      const storedData = storage.getItem(key)

      if (!storedData) {
        setIsLoading(false)
        isInitializedRef.current = true
        return
      }

      const parsed: PersistedData<T> = JSON.parse(storedData)

      // Check version compatibility
      if (parsed.metadata.version !== version) {
        if (recoveryEnabled) {
          setRecoveryActions(prev => [...prev, {
            type: 'merge',
            description: `Data version mismatch (${parsed.metadata.version} → ${version}). Merge or overwrite?`,
            data: parsed.data
          }])
        }
        setIsLoading(false)
        isInitializedRef.current = true
        return
      }

      // Check TTL
      if (ttl && parsed.metadata.expiresAt && Date.now() > parsed.metadata.expiresAt) {
        if (recoveryEnabled) {
          setRecoveryActions(prev => [...prev, {
            type: 'restore',
            description: 'Data has expired. Restore from backup?',
            data: parsed.data
          }])
        }
        storage.removeItem(key)
        setIsLoading(false)
        isInitializedRef.current = true
        return
      }

      // Verify checksum if available
      if (parsed.metadata.checksum) {
        const currentChecksum = generateChecksum(parsed.data)
        if (currentChecksum !== parsed.metadata.checksum) {
          if (recoveryEnabled) {
            setRecoveryActions(prev => [...prev, {
              type: 'discard',
              description: 'Data integrity check failed. Discard corrupted data?',
            }])
          }
          setIsLoading(false)
          isInitializedRef.current = true
          return
        }
      }

      // Decompress and decrypt if needed
      let processedData = JSON.stringify(parsed.data)
      processedData = await decompressData(processedData)
      processedData = await decryptData(processedData)

      const finalData: T = JSON.parse(processedData)
      setData(finalData)
      setLastSaved(new Date(parsed.metadata.timestamp))

    } catch (err) {
      setError(err as Error)
      if (recoveryEnabled) {
        setRecoveryActions(prev => [...prev, {
          type: 'overwrite',
          description: 'Failed to load data. Start with fresh data?',
        }])
      }
    } finally {
      setIsLoading(false)
      isInitializedRef.current = true
    }
  }, [key, version, ttl, recoveryEnabled, getStorage, generateChecksum, decompressData, decryptData])

  // Save data to storage
  const saveData = useCallback(async (newData: T, immediate = false): Promise<void> => {
    if (!isInitializedRef.current) return

    // Skip storage operations on server side
    if (typeof window === 'undefined') return

    const saveOperation = async () => {
      const storage = getStorage()
      if (!storage) return // Skip if no storage available (server side)

      try {
        let dataToStore = JSON.stringify(newData)

        // Compress and encrypt if enabled
        dataToStore = await compressData(dataToStore)
        dataToStore = await encryptData(dataToStore)

        // Check size limit
        const sizeInBytes = new Blob([dataToStore]).size
        if (sizeInBytes > maxSize) {
          throw new Error(`Data size (${sizeInBytes} bytes) exceeds limit (${maxSize} bytes)`)
        }

        const persistedData: PersistedData<T> = {
          data: newData,
          metadata: {
            timestamp: Date.now(),
            version,
            size: sizeInBytes,
            checksum: generateChecksum(newData),
            expiresAt: ttl ? Date.now() + ttl : undefined,
          }
        }

        storage.setItem(key, JSON.stringify(persistedData))

        // Create backup if enabled
        if (backupEnabled) {
          const backupKey = `${key}_backup_${Date.now()}`
          storage.setItem(backupKey, JSON.stringify(persistedData))

          // Clean old backups (keep last 3)
          const backupKeys = Object.keys(storage).filter(k => k.startsWith(`${key}_backup_`))
          if (backupKeys.length > 3) {
            backupKeys.sort().reverse().slice(3).forEach(k => storage.removeItem(k))
          }
        }

        setLastSaved(new Date())
        setError(null)

      } catch (err) {
        setError(err as Error)
        throw err
      }
    }

    if (immediate) {
      await saveOperation()
    } else {
      // Debounced save
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
      saveTimeoutRef.current = setTimeout(saveOperation, 1000)
    }
  }, [key, version, ttl, compress, encrypt, maxSize, backupEnabled, generateChecksum, compressData, encryptData, getStorage])

  // Execute recovery action
  const executeRecoveryAction = useCallback(async (action: RecoveryAction) => {
    switch (action.type) {
      case 'restore':
        if (action.data) {
          setData(action.data)
          await saveData(action.data, true)
        }
        break

      case 'merge':
        // Merge strategy would depend on data structure
        if (action.data) {
          setData(action.data) // For now, just restore
          await saveData(action.data, true)
        }
        break

      case 'overwrite':
        await saveData(initialData, true)
        setData(initialData)
        break

      case 'discard':
        const storage = getStorage()
        if (storage) {
          storage.removeItem(key)
        }
        setData(initialData)
        break
    }

    // Remove the action from recovery list
    setRecoveryActions(prev => prev.filter(a => a !== action))
  }, [initialData, saveData, getStorage, key])

  // Get backup data
  const getBackups = useCallback(() => {
    const storage = getStorage()
    if (!storage) return [] // Return empty array if no storage available

    const backups: Array<{ key: string, data: PersistedData<T>, timestamp: Date }> = []

    Object.keys(storage).forEach(storageKey => {
      if (storageKey.startsWith(`${key}_backup_`)) {
        try {
          const backupData = JSON.parse(storage.getItem(storageKey) || '{}')
          backups.push({
            key: storageKey,
            data: backupData,
            timestamp: new Date(parseInt(storageKey.split('_').pop() || '0'))
          })
        } catch {
          // Skip invalid backups
        }
      }
    })

    return backups.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  }, [key, getStorage])

  // Clear all data
  const clearData = useCallback(async () => {
    // Skip storage operations on server side
    if (typeof window === 'undefined') return

    const storage = getStorage()
    if (!storage) return // Skip if no storage available (server side)

    // Clear main data
    storage.removeItem(key)

    // Clear backups
    Object.keys(storage).forEach(storageKey => {
      if (storageKey.startsWith(`${key}_backup_`)) {
        storage.removeItem(storageKey)
      }
    })

    setData(initialData)
    setLastSaved(null)
    setError(null)
    setRecoveryActions([])
  }, [key, initialData, getStorage])

  // Initialize on mount
  useEffect(() => {
    loadData()
  }, [loadData])

  // Auto-save on data changes
  useEffect(() => {
    if (isInitializedRef.current && data !== initialData) {
      saveData(data)
    }
  }, [data, saveData, initialData])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current)
      }
    }
  }, [])

  return {
    data,
    setData,
    isLoading,
    error,
    lastSaved,
    recoveryActions,
    saveData: (immediate = false) => saveData(data, immediate),
    loadData,
    executeRecoveryAction,
    getBackups,
    clearData,
    hasBackups: getBackups().length > 0,
  }
}

// Specialized hooks for common use cases
export const useLocalStorage = <T>(key: string, initialData: T, options?: Omit<PersistenceOptions, 'key' | 'storageType'>) =>
  useDataPersistence(initialData, { ...options, key, storageType: 'localStorage' })

export const useSessionStorage = <T>(key: string, initialData: T, options?: Omit<PersistenceOptions, 'key' | 'storageType'>) =>
  useDataPersistence(initialData, { ...options, key, storageType: 'sessionStorage' })

// Hook for form persistence
export const useFormPersistence = <T extends Record<string, any>>(
  formKey: string,
  initialValues: T
) => {
  return useLocalStorage(formKey, initialValues, {
    version: 1,
    ttl: 24 * 60 * 60 * 1000, // 24 hours
    backupEnabled: true,
    recoveryEnabled: true,
  })
}
