'use client'

import { AnimatePresence, motion } from 'framer-motion'
import {
    Activity,
    BarChart3,
    Check,
    Copy,
    Database,
    Download,
    Eye,
    FileArchive,
    FileCode as FileBinary,
    FileCode,
    FileCog as FileConfig,
    FileCode as FileCss,
    FileSpreadsheet as FileCsv,
    FileText as FileData,
    FileCode as FileHtml,
    FileText as FileIni,
    FileCode as FileJavascript,
    FileJson,
    FileText as FileLog,
    FileText as FileMarkdown,
    FileCode as FilePython,
    FileText,
    FileText as FileToml,
    FileCode as FileTypescript,
    FileX as FileXml,
    FileText as FileYaml,
    Gauge,
    Layers,
    Palette,
    Play,
    Settings,
    Target,
    TrendingUp,
    Zap
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { SyntheticDataManagement } from './SyntheticDataManagement'

interface SyntheticDataConfig {
  patterns: string[]
  complexity: number
  volume: number
  contentType: string
  extensions: string[]
  mixedContent: boolean
  entropy: number
  redundancy: number
  structure: string
  language: string
  encoding: string
  metadata: Record<string, any>
  customPatterns: string[]
  compressionChallenges: boolean
  learningOptimization: boolean
  diversityControl: boolean
}

interface GeneratedData {
  id: string
  name: string
  extension: string
  size: number
  content: string
  metadata: Record<string, any>
  timestamp: Date
  compressionStats?: {
    originalSize: number
    compressedSize: number
    ratio: number
    algorithm: string
  }
}

interface FileExtensionInfo {
  extension: string
  name: string
  category: string
  icon: React.ComponentType<any>
  description: string
  bestFor: string[]
  compressionRatio: string
  complexity: 'low' | 'medium' | 'high'
  examples: string[]
}

interface SyntheticDataTabProps {
  syntheticConfig: SyntheticDataConfig
  setSyntheticConfig: (config: SyntheticDataConfig) => void
  onGenerate: () => void
  isGenerating: boolean
}

export default function SyntheticDataTab({
  syntheticConfig,
  setSyntheticConfig,
  onGenerate,
  isGenerating
}: SyntheticDataTabProps) {
  const [generatedData, setGeneratedData] = useState<GeneratedData[]>([])
  const [selectedData, setSelectedData] = useState<GeneratedData | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [showDataManagement, setShowDataManagement] = useState(false)

  // Generate mock data when generation is triggered
  useEffect(() => {
    if (isGenerating) {
      // Simulate data generation
      setTimeout(() => {
        const mockData: GeneratedData[] = generateMockData(syntheticConfig)
        setGeneratedData(mockData)
        setShowDataManagement(true)
      }, 2000)
    }
  }, [isGenerating, syntheticConfig])

  // Generate mock data based on configuration
  const generateMockData = (config: SyntheticDataConfig): GeneratedData[] => {
    const data: GeneratedData[] = []
    const extensions = config.extensions.length > 0 ? config.extensions : ['.txt', '.json', '.csv']
    
    for (let i = 0; i < Math.min(config.volume / 100, 20); i++) {
      const extension = extensions[i % extensions.length]
      const extInfo = fileExtensions.find(e => e.extension === extension)
      
      data.push({
        id: `generated-${i + 1}`,
        name: `synthetic_data_${i + 1}${extension}`,
        extension,
        size: Math.floor(Math.random() * 5000) + 1000, // 1KB to 6KB
        content: generateContentForExtension(extension, config),
        metadata: {
          pattern: config.patterns[i % config.patterns.length],
          complexity: config.complexity,
          entropy: config.entropy,
          redundancy: config.redundancy
        },
        timestamp: new Date(),
        compressionStats: {
          originalSize: Math.floor(Math.random() * 5000) + 1000,
          compressedSize: Math.floor(Math.random() * 2000) + 500,
          ratio: Math.random() * 3 + 1,
          algorithm: ['gzip', 'lz4', 'zstd', 'lzma'][Math.floor(Math.random() * 4)]
        }
      })
    }
    
    return data
  }

  // Generate content based on file extension
  const generateContentForExtension = (extension: string, config: SyntheticDataConfig): string => {
    switch (extension) {
      case '.json':
        return JSON.stringify({
          id: Math.random().toString(36).substr(2, 9),
          data: Array.from({ length: 10 }, (_, i) => ({
            id: i,
            value: Math.random() * 100,
            timestamp: new Date().toISOString(),
            metadata: { pattern: config.patterns[0], complexity: config.complexity }
          })),
          metadata: { generated: true, pattern: config.patterns[0] }
        }, null, 2)
      
      case '.csv':
        return 'id,name,value,timestamp\n' + 
               Array.from({ length: 20 }, (_, i) => 
                 `${i},item_${i},${Math.random() * 100},${new Date().toISOString()}`
               ).join('\n')
      
      case '.xml':
        return `<?xml version="1.0" encoding="UTF-8"?>
<data>
  <items>
    ${Array.from({ length: 10 }, (_, i) => 
      `<item id="${i}" value="${Math.random() * 100}" />`
    ).join('\n    ')}
  </items>
</data>`
      
      case '.yaml':
        return `data:
  items:
${Array.from({ length: 10 }, (_, i) => 
  `    - id: ${i}
      value: ${Math.random() * 100}
      timestamp: ${new Date().toISOString()}`
).join('\n')}
  metadata:
    pattern: ${config.patterns[0]}
    complexity: ${config.complexity}`
      
      case '.log':
        return Array.from({ length: 50 }, (_, i) => 
          `${new Date().toISOString()} [INFO] Log entry ${i}: ${Math.random().toString(36).substr(2, 20)}`
        ).join('\n')
      
      case '.py':
        return `# Generated Python code
import random
import json
from datetime import datetime

def generate_data():
    data = []
    for i in range(${Math.floor(Math.random() * 100) + 10}):
        data.append({
            'id': i,
            'value': random.random() * 100,
            'timestamp': datetime.now().isoformat()
        })
    return data

if __name__ == "__main__":
    result = generate_data()
    print(json.dumps(result, indent=2))`
      
      default:
        return Array.from({ length: 100 }, (_, i) => 
          `Line ${i + 1}: This is synthetic data generated for testing compression algorithms. ` +
          `Pattern: ${config.patterns[0]}, Complexity: ${config.complexity}`
        ).join('\n')
    }
  }

  // Comprehensive file extension definitions
  const fileExtensions: FileExtensionInfo[] = [
    // Text Files
    {
      extension: '.txt',
      name: 'Plain Text',
      category: 'text',
      icon: FileText,
      description: 'Simple text files with basic formatting',
      bestFor: ['documentation', 'logs', 'notes'],
      compressionRatio: '2-5x',
      complexity: 'low',
      examples: ['readme.txt', 'notes.txt', 'documentation.txt']
    },
    {
      extension: '.md',
      name: 'Markdown',
      category: 'text',
      icon: FileMarkdown,
      description: 'Markdown formatted text with rich syntax',
      bestFor: ['documentation', 'blogs', 'technical writing'],
      compressionRatio: '2-4x',
      complexity: 'low',
      examples: ['README.md', 'documentation.md', 'blog-post.md']
    },
    {
      extension: '.log',
      name: 'Log Files',
      category: 'text',
      icon: FileLog,
      description: 'Application and system log files',
      bestFor: ['debugging', 'monitoring', 'audit trails'],
      compressionRatio: '3-8x',
      complexity: 'medium',
      examples: ['app.log', 'error.log', 'access.log']
    },

    // Data Files
    {
      extension: '.json',
      name: 'JSON Data',
      category: 'data',
      icon: FileJson,
      description: 'JavaScript Object Notation data format',
      bestFor: ['APIs', 'configuration', 'data exchange'],
      compressionRatio: '2-6x',
      complexity: 'medium',
      examples: ['config.json', 'data.json', 'api-response.json']
    },
    {
      extension: '.xml',
      name: 'XML Documents',
      category: 'data',
      icon: FileXml,
      description: 'Extensible Markup Language documents',
      bestFor: ['web services', 'documentation', 'data exchange'],
      compressionRatio: '3-7x',
      complexity: 'medium',
      examples: ['config.xml', 'data.xml', 'sitemap.xml']
    },
    {
      extension: '.csv',
      name: 'CSV Data',
      category: 'data',
      icon: FileCsv,
      description: 'Comma-separated values data format',
      bestFor: ['spreadsheets', 'data analysis', 'import/export'],
      compressionRatio: '2-5x',
      complexity: 'low',
      examples: ['data.csv', 'export.csv', 'analytics.csv']
    },
    {
      extension: '.yaml',
      name: 'YAML Configuration',
      category: 'data',
      icon: FileYaml,
      description: 'YAML Ain\'t Markup Language configuration files',
      bestFor: ['configuration', 'deployment', 'settings'],
      compressionRatio: '2-4x',
      complexity: 'low',
      examples: ['config.yaml', 'docker-compose.yaml', 'settings.yaml']
    },
    {
      extension: '.yml',
      name: 'YAML Alternative',
      category: 'data',
      icon: FileYaml,
      description: 'Alternative YAML file extension',
      bestFor: ['configuration', 'deployment', 'settings'],
      compressionRatio: '2-4x',
      complexity: 'low',
      examples: ['config.yml', 'travis.yml', 'gitlab-ci.yml']
    },
    {
      extension: '.toml',
      name: 'TOML Configuration',
      category: 'data',
      icon: FileToml,
      description: 'Tom\'s Obvious, Minimal Language configuration',
      bestFor: ['configuration', 'settings', 'metadata'],
      compressionRatio: '2-4x',
      complexity: 'low',
      examples: ['Cargo.toml', 'pyproject.toml', 'config.toml']
    },
    {
      extension: '.ini',
      name: 'INI Configuration',
      category: 'data',
      icon: FileIni,
      description: 'Initialization file format',
      bestFor: ['configuration', 'settings', 'legacy systems'],
      compressionRatio: '2-3x',
      complexity: 'low',
      examples: ['config.ini', 'settings.ini', 'database.ini']
    },
    {
      extension: '.cfg',
      name: 'Configuration Files',
      category: 'data',
      icon: FileConfig,
      description: 'General configuration file format',
      bestFor: ['configuration', 'settings', 'system files'],
      compressionRatio: '2-3x',
      complexity: 'low',
      examples: ['app.cfg', 'system.cfg', 'network.cfg']
    },
    {
      extension: '.conf',
      name: 'Configuration Files',
      category: 'data',
      icon: FileConfig,
      description: 'Configuration file format',
      bestFor: ['configuration', 'settings', 'system files'],
      compressionRatio: '2-3x',
      complexity: 'low',
      examples: ['nginx.conf', 'apache.conf', 'system.conf']
    },

    // Code Files
    {
      extension: '.py',
      name: 'Python Code',
      category: 'code',
      icon: FilePython,
      description: 'Python programming language source code',
      bestFor: ['web development', 'data science', 'automation'],
      compressionRatio: '2-4x',
      complexity: 'medium',
      examples: ['main.py', 'utils.py', 'test.py']
    },
    {
      extension: '.js',
      name: 'JavaScript Code',
      category: 'code',
      icon: FileJavascript,
      description: 'JavaScript programming language source code',
      bestFor: ['web development', 'frontend', 'backend'],
      compressionRatio: '2-4x',
      complexity: 'medium',
      examples: ['app.js', 'utils.js', 'index.js']
    },
    {
      extension: '.ts',
      name: 'TypeScript Code',
      category: 'code',
      icon: FileTypescript,
      description: 'TypeScript programming language source code',
      bestFor: ['web development', 'frontend', 'type-safe development'],
      compressionRatio: '2-4x',
      complexity: 'medium',
      examples: ['app.ts', 'types.ts', 'index.ts']
    },
    {
      extension: '.html',
      name: 'HTML Documents',
      category: 'code',
      icon: FileHtml,
      description: 'HyperText Markup Language documents',
      bestFor: ['web pages', 'templates', 'documentation'],
      compressionRatio: '2-5x',
      complexity: 'low',
      examples: ['index.html', 'template.html', 'page.html']
    },
    {
      extension: '.css',
      name: 'CSS Stylesheets',
      category: 'code',
      icon: FileCss,
      description: 'Cascading Style Sheets for web styling',
      bestFor: ['web styling', 'themes', 'design systems'],
      compressionRatio: '2-4x',
      complexity: 'low',
      examples: ['style.css', 'theme.css', 'main.css']
    },
    {
      extension: '.sql',
      name: 'SQL Scripts',
      category: 'code',
      icon: FileCode,
      description: 'Structured Query Language database scripts',
      bestFor: ['database operations', 'queries', 'migrations'],
      compressionRatio: '2-4x',
      complexity: 'medium',
      examples: ['schema.sql', 'queries.sql', 'migration.sql']
    },

    // Binary Files
    {
      extension: '.bin',
      name: 'Binary Data',
      category: 'binary',
      icon: FileBinary,
      description: 'Raw binary data files',
      bestFor: ['executables', 'firmware', 'raw data'],
      compressionRatio: '1-2x',
      complexity: 'high',
      examples: ['firmware.bin', 'data.bin', 'executable.bin']
    },
    {
      extension: '.dat',
      name: 'Data Files',
      category: 'binary',
      icon: FileData,
      description: 'Generic data files',
      bestFor: ['data storage', 'cache', 'temporary files'],
      compressionRatio: '1-3x',
      complexity: 'medium',
      examples: ['cache.dat', 'data.dat', 'temp.dat']
    },

    // Archive Files
    {
      extension: '.zip',
      name: 'ZIP Archives',
      category: 'archive',
      icon: FileArchive,
      description: 'ZIP compressed archive format',
      bestFor: ['file compression', 'archiving', 'distribution'],
      compressionRatio: '2-10x',
      complexity: 'medium',
      examples: ['backup.zip', 'archive.zip', 'distribution.zip']
    },
    {
      extension: '.tar',
      name: 'TAR Archives',
      category: 'archive',
      icon: FileArchive,
      description: 'Tape Archive format',
      bestFor: ['backup', 'distribution', 'system files'],
      compressionRatio: '1-2x',
      complexity: 'low',
      examples: ['backup.tar', 'source.tar', 'distribution.tar']
    },
    {
      extension: '.gz',
      name: 'Gzip Archives',
      category: 'archive',
      icon: FileArchive,
      description: 'GNU zip compressed format',
      bestFor: ['compression', 'backup', 'distribution'],
      compressionRatio: '2-10x',
      complexity: 'medium',
      examples: ['file.gz', 'backup.gz', 'archive.gz']
    },
    {
      extension: '.bz2',
      name: 'Bzip2 Archives',
      category: 'archive',
      icon: FileArchive,
      description: 'Bzip2 compressed format',
      bestFor: ['high compression', 'backup', 'archiving'],
      compressionRatio: '3-15x',
      complexity: 'high',
      examples: ['file.bz2', 'backup.bz2', 'archive.bz2']
    },
    {
      extension: '.xz',
      name: 'XZ Archives',
      category: 'archive',
      icon: FileArchive,
      description: 'XZ compressed format',
      bestFor: ['maximum compression', 'backup', 'archiving'],
      compressionRatio: '5-20x',
      complexity: 'high',
      examples: ['file.xz', 'backup.xz', 'archive.xz']
    }
  ]

  const availablePatterns = [
    'repetitive_text',
    'structured_data',
    'binary_data',
    'json_objects',
    'xml_documents',
    'log_files',
    'source_code',
    'markdown_content',
    'csv_data',
    'random_data',
    'compression_challenges',
    'edge_cases',
    'performance_tests',
    'stress_tests',
    'realistic_scenarios'
  ]

  const contentTypes = ['text', 'binary', 'mixed', 'structured', 'unstructured', 'code', 'data', 'archive']
  const structures = ['flat', 'hierarchical', 'nested', 'relational', 'graph', 'tree', 'network']
  const languages = ['english', 'code', 'mixed', 'technical', 'natural', 'multilingual', 'programming']
  const encodings = ['utf-8', 'ascii', 'latin-1', 'utf-16', 'binary', 'base64', 'hex']

  const updateConfig = (updates: Partial<SyntheticDataConfig>) => {
    setSyntheticConfig({ ...syntheticConfig, ...updates })
  }

  const togglePattern = (pattern: string) => {
    const newPatterns = syntheticConfig.patterns.includes(pattern)
      ? syntheticConfig.patterns.filter(p => p !== pattern)
      : [...syntheticConfig.patterns, pattern]
    updateConfig({ patterns: newPatterns })
  }

  const toggleExtension = (extension: string) => {
    const newExtensions = syntheticConfig.extensions.includes(extension)
      ? syntheticConfig.extensions.filter(e => e !== extension)
      : [...syntheticConfig.extensions, extension]
    updateConfig({ extensions: newExtensions })
  }

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
    }
  }

  const downloadData = (data: GeneratedData) => {
    const blob = new Blob([data.content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = data.name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const filteredExtensions = fileExtensions.filter(ext =>
    filterCategory === 'all' || ext.category === filterCategory
  )

  const filteredData = generatedData.filter(data =>
    data.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    data.extension.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const categories = [
    { id: 'all', name: 'All Types', icon: Layers },
    { id: 'text', name: 'Text Files', icon: FileText },
    { id: 'data', name: 'Data Files', icon: FileJson },
    { id: 'code', name: 'Code Files', icon: FileCode },
    { id: 'binary', name: 'Binary Files', icon: FileBinary },
    { id: 'archive', name: 'Archive Files', icon: FileArchive }
  ]

  // Show data management interface if data has been generated
  if (showDataManagement && generatedData.length > 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="space-y-6"
      >
        <div className="glass p-6 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold gradient-text">Generated Synthetic Data</h2>
                <p className="text-slate-400">
                  {generatedData.length} files generated • {syntheticConfig.patterns.length} patterns • {syntheticConfig.volume} KB volume
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowDataManagement(false)}
                className="btn-secondary flex items-center space-x-2"
              >
                <Settings className="w-4 h-4" />
                <span>Configure</span>
              </button>
            </div>
          </div>
        </div>
        
        <SyntheticDataManagement />
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      {/* Header Section */}
      <div className="glass p-6 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold gradient-text">Synthetic Data Generation</h2>
              <p className="text-slate-400">Advanced data generation for compression algorithm testing</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
              className="btn-secondary flex items-center space-x-2"
            >
              <Settings className="w-4 h-4" />
              <span>Advanced</span>
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="glass-dark p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-blue-400" />
              <span className="text-sm text-slate-400">Patterns</span>
            </div>
            <div className="text-2xl font-bold text-white">{syntheticConfig.patterns.length}</div>
          </div>
          <div className="glass-dark p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <Gauge className="w-5 h-5 text-green-400" />
              <span className="text-sm text-slate-400">Volume</span>
            </div>
            <div className="text-2xl font-bold text-white">{syntheticConfig.volume} KB</div>
          </div>
          <div className="glass-dark p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-purple-400" />
              <span className="text-sm text-slate-400">Complexity</span>
            </div>
            <div className="text-2xl font-bold text-white">{(syntheticConfig.complexity * 100).toFixed(0)}%</div>
          </div>
          <div className="glass-dark p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-orange-400" />
              <span className="text-sm text-slate-400">Extensions</span>
            </div>
            <div className="text-2xl font-bold text-white">{syntheticConfig.extensions.length}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Basic Configuration */}
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Settings className="w-5 h-5 text-blue-400" />
              <span>Basic Configuration</span>
            </h3>

            <div className="space-y-4">
              {/* Volume */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Data Volume (KB)
                </label>
                <input
                  type="range"
                  min="100"
                  max="10000"
                  step="100"
                  value={syntheticConfig.volume}
                  onChange={(e) => updateConfig({ volume: parseInt(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>100 KB</span>
                  <span>{syntheticConfig.volume} KB</span>
                  <span>10 MB</span>
                </div>
              </div>

              {/* Complexity */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Complexity Level
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={syntheticConfig.complexity}
                  onChange={(e) => updateConfig({ complexity: parseFloat(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>Simple</span>
                  <span>{(syntheticConfig.complexity * 100).toFixed(0)}%</span>
                  <span>Complex</span>
                </div>
              </div>

              {/* Content Type */}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Content Type
                </label>
                <select
                  value={syntheticConfig.contentType}
                  onChange={(e) => updateConfig({ contentType: e.target.value })}
                  className="input-field w-full"
                >
                  {contentTypes.map(type => (
                    <option key={type} value={type}>
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Mixed Content Toggle */}
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="mixedContent"
                  checked={syntheticConfig.mixedContent}
                  onChange={(e) => updateConfig({ mixedContent: e.target.checked })}
                  className="rounded border-slate-600 bg-slate-800 text-blue-500 focus:ring-blue-500"
                />
                <label htmlFor="mixedContent" className="text-sm text-slate-300">
                  Include Mixed Content Types
                </label>
              </div>
            </div>
          </div>

          {/* Advanced Configuration */}
          {showAdvancedSettings && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="glass p-6 rounded-xl"
            >
              <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
                <Zap className="w-5 h-5 text-purple-400" />
                <span>Advanced Configuration</span>
              </h3>

              <div className="space-y-4">
                {/* Entropy */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Entropy Level
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={syntheticConfig.entropy}
                    onChange={(e) => updateConfig({ entropy: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-slate-400 mt-1">
                    <span>Low</span>
                    <span>{(syntheticConfig.entropy * 100).toFixed(0)}%</span>
                    <span>High</span>
                  </div>
                </div>

                {/* Redundancy */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Redundancy Level
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={syntheticConfig.redundancy}
                    onChange={(e) => updateConfig({ redundancy: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-slate-400 mt-1">
                    <span>None</span>
                    <span>{(syntheticConfig.redundancy * 100).toFixed(0)}%</span>
                    <span>High</span>
                  </div>
                </div>

                {/* Structure */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Data Structure
                  </label>
                  <select
                    value={syntheticConfig.structure}
                    onChange={(e) => updateConfig({ structure: e.target.value })}
                    className="input-field w-full"
                  >
                    {structures.map(structure => (
                      <option key={structure} value={structure}>
                        {structure.charAt(0).toUpperCase() + structure.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Language */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Language Type
                  </label>
                  <select
                    value={syntheticConfig.language}
                    onChange={(e) => updateConfig({ language: e.target.value })}
                    className="input-field w-full"
                  >
                    {languages.map(lang => (
                      <option key={lang} value={lang}>
                        {lang.charAt(0).toUpperCase() + lang.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Encoding */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Encoding
                  </label>
                  <select
                    value={syntheticConfig.encoding}
                    onChange={(e) => updateConfig({ encoding: e.target.value })}
                    className="input-field w-full"
                  >
                    {encodings.map(encoding => (
                      <option key={encoding} value={encoding}>
                        {encoding.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </motion.div>
          )}

          {/* Generation Controls */}
          <div className="glass p-6 rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <Play className="w-5 h-5 text-green-400" />
                <span>Generation</span>
              </h3>
            </div>

            <div className="space-y-4">
              <div className="text-sm text-slate-400 space-y-1">
                <div>Volume: {syntheticConfig.volume} KB</div>
                <div>Patterns: {syntheticConfig.patterns.length} selected</div>
                <div>Complexity: {(syntheticConfig.complexity * 100).toFixed(0)}%</div>
                <div>Entropy: {(syntheticConfig.entropy * 100).toFixed(0)}%</div>
              </div>

              <button
                onClick={onGenerate}
                disabled={isGenerating || syntheticConfig.patterns.length === 0}
                className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Generate Data</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Pattern Selection */}
          <div className="glass p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-4 flex items-center space-x-2">
              <Palette className="w-5 h-5 text-orange-400" />
              <span>Data Patterns</span>
            </h3>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {availablePatterns.map(pattern => (
                <button
                  key={pattern}
                  onClick={() => togglePattern(pattern)}
                  className={`p-3 rounded-lg border transition-all duration-200 text-sm ${
                    syntheticConfig.patterns.includes(pattern)
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 border-blue-500 text-white shadow-lg'
                      : 'bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700 hover:border-slate-500'
                  }`}
                >
                  {pattern.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </button>
              ))}
            </div>
          </div>

          {/* File Extensions */}
          <div className="glass p-6 rounded-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <FileText className="w-5 h-5 text-green-400" />
                <span>File Extensions</span>
              </h3>
              <div className="flex space-x-2">
                {categories.map(category => (
                  <button
                    key={category.id}
                    onClick={() => setFilterCategory(category.id)}
                    className={`px-3 py-1 rounded-lg text-sm transition-all duration-200 ${
                      filterCategory === category.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    {category.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-h-96 overflow-y-auto">
              {filteredExtensions.map(ext => {
                const Icon = ext.icon
                return (
                  <button
                    key={ext.extension}
                    onClick={() => toggleExtension(ext.extension)}
                    className={`p-4 rounded-lg border transition-all duration-200 text-left ${
                      syntheticConfig.extensions.includes(ext.extension)
                        ? 'bg-gradient-to-r from-green-600 to-emerald-600 border-green-500 text-white shadow-lg'
                        : 'bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700 hover:border-slate-500'
                    }`}
                  >
                    <div className="flex items-center space-x-2 mb-2">
                      <Icon className="w-4 h-4" />
                      <span className="font-semibold">{ext.extension}</span>
                    </div>
                    <div className="text-xs opacity-80">{ext.name}</div>
                    <div className="text-xs opacity-60 mt-1">Ratio: {ext.compressionRatio}</div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Generated Data Display */}
          {generatedData.length > 0 && (
            <div className="glass p-6 rounded-xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5 text-purple-400" />
                  <span>Generated Data</span>
                </h3>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    placeholder="Search data..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="input-field w-48"
                  />
                  <button
                    onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                    className="btn-secondary"
                  >
                    {viewMode === 'grid' ? 'List' : 'Grid'}
                  </button>
                </div>
              </div>

              {viewMode === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredData.map(data => (
                    <div
                      key={data.id}
                      className="glass-dark p-4 rounded-lg cursor-pointer hover:bg-slate-700/50 transition-all duration-200"
                      onClick={() => setSelectedData(data)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <FileText className="w-4 h-4 text-blue-400" />
                          <span className="font-semibold">{data.name}</span>
                        </div>
                        <span className="text-xs text-slate-400">{data.extension}</span>
                      </div>
                      <div className="text-sm text-slate-400 mb-2">
                        Size: {(data.size / 1024).toFixed(2)} KB
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            copyToClipboard(data.content, data.id)
                          }}
                          className="p-1 rounded hover:bg-slate-600"
                        >
                          {copiedId === data.id ? (
                            <Check className="w-4 h-4 text-green-400" />
                          ) : (
                            <Copy className="w-4 h-4 text-slate-400" />
                          )}
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            downloadData(data)
                          }}
                          className="p-1 rounded hover:bg-slate-600"
                        >
                          <Download className="w-4 h-4 text-slate-400" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedData(data)
                          }}
                          className="p-1 rounded hover:bg-slate-600"
                        >
                          <Eye className="w-4 h-4 text-slate-400" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredData.map(data => (
                    <div
                      key={data.id}
                      className="glass-dark p-4 rounded-lg cursor-pointer hover:bg-slate-700/50 transition-all duration-200"
                      onClick={() => setSelectedData(data)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <FileText className="w-5 h-5 text-blue-400" />
                          <div>
                            <div className="font-semibold">{data.name}</div>
                            <div className="text-sm text-slate-400">
                              Size: {(data.size / 1024).toFixed(2)} KB • {data.extension}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              copyToClipboard(data.content, data.id)
                            }}
                            className="p-1 rounded hover:bg-slate-600"
                          >
                            {copiedId === data.id ? (
                              <Check className="w-4 h-4 text-green-400" />
                            ) : (
                              <Copy className="w-4 h-4 text-slate-400" />
                            )}
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              downloadData(data)
                            }}
                            className="p-1 rounded hover:bg-slate-600"
                          >
                            <Download className="w-4 h-4 text-slate-400" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setSelectedData(data)
                            }}
                            className="p-1 rounded hover:bg-slate-600"
                          >
                            <Eye className="w-4 h-4 text-slate-400" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Data Viewer Modal */}
      <AnimatePresence>
        {selectedData && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedData(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="glass max-w-4xl w-full max-h-[80vh] overflow-hidden rounded-xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-slate-600">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-6 h-6 text-blue-400" />
                    <div>
                      <h3 className="text-xl font-semibold">{selectedData.name}</h3>
                      <p className="text-slate-400">
                        Size: {(selectedData.size / 1024).toFixed(2)} KB • {selectedData.extension}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => copyToClipboard(selectedData.content, selectedData.id)}
                      className="btn-secondary"
                    >
                      {copiedId === selectedData.id ? (
                        <Check className="w-4 h-4" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                    <button
                      onClick={() => downloadData(selectedData)}
                      className="btn-secondary"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setSelectedData(null)}
                      className="btn-secondary"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
              <div className="p-6 overflow-auto max-h-[60vh]">
                <pre className="text-sm font-mono text-slate-300 whitespace-pre-wrap">
                  {selectedData.content}
                </pre>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
