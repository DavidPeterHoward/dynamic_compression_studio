import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import EnhancedCompressionTabImproved from '../components/EnhancedCompressionTabImproved'

// Mock the API calls
global.fetch = jest.fn()

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: 'div',
  },
  AnimatePresence: 'div',
}))

describe('EnhancedCompressionTabImproved', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    global.fetch = jest.fn().mockResolvedValue({
      json: () => Promise.resolve({ success: true })
    })
  })

  it('renders the component correctly', () => {
    render(<EnhancedCompressionTabImproved />)
    
    expect(screen.getByText('Enhanced Compression')).toBeInTheDocument()
    expect(screen.getByText('AI-powered compression with meta-learning and advanced analytics')).toBeInTheDocument()
    expect(screen.getByText('Input & Analysis')).toBeInTheDocument()
    expect(screen.getByText('Results & Metrics')).toBeInTheDocument()
  })

  it('displays content input field', () => {
    render(<EnhancedCompressionTabImproved />)
    
    expect(screen.getByPlaceholderText('Enter content to compress...')).toBeInTheDocument()
    expect(screen.getByText('Content Input')).toBeInTheDocument()
  })

  it('shows meta-learning panel', () => {
    render(<EnhancedCompressionTabImproved />)
    
    expect(screen.getByText('Meta-Learning')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('shows real-time metrics panel', () => {
    render(<EnhancedCompressionTabImproved />)
    
    expect(screen.getByText('Real-time Metrics')).toBeInTheDocument()
    expect(screen.getByText('Throughput')).toBeInTheDocument()
    expect(screen.getByText('Success Rate')).toBeInTheDocument()
  })

  it('displays compression button', () => {
    render(<EnhancedCompressionTabImproved />)
    
    expect(screen.getByText('Compress Content')).toBeInTheDocument()
  })

  it('shows character count', () => {
    render(<EnhancedCompressionTabImproved />)
    
    expect(screen.getByText(/characters/)).toBeInTheDocument()
  })
})