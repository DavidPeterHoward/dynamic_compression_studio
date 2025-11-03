import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MetricsTab from '../components/MetricsTab';
import { useMetrics } from '../hooks/useMetrics';

// Mock the useMetrics hook
jest.mock('../hooks/useMetrics');

const mockUseMetrics = useMetrics as jest.MockedFunction<typeof useMetrics>;

describe('MetricsTab Component', () => {
  const mockMetrics = {
    cpu: 45.2,
    memory: 67.8,
    disk: 23.4,
    network: 12.1,
    compressionEfficiency: 85.5,
    algorithmPerformance: {
      gzip: 2.5,
      zstd: 3.2,
      lzma: 4.1
    },
    userSatisfaction: 92.3,
    systemHealth: 'healthy' as const,
    throughput: 1500,
    successRate: 98.7,
    averageCompressionRatio: 3.1,
    activeConnections: 245,
    queueLength: 5,
    errorRate: 1.3,
    responseTime: 125,
    temperature: 42.5,
    powerConsumption: 180,
    networkLatency: 25,
    bandwidth: 5000,
    diskIO: 150,
    memoryUsage: 67.8,
    swapUsage: 5.2,
    loadAverage: [1.2, 1.1, 0.9],
    uptime: 86400,
    processes: 156,
    threads: 892,
    openFiles: 2048,
    networkConnections: 245,
    diskSpace: {
      total: 1000000000000,
      used: 500000000000,
      free: 300000000000,
      available: 300000000000
    },
    memoryDetails: {
      total: 16000000000,
      used: 8000000000,
      free: 4000000000,
      available: 4000000000,
      cached: 2000000000,
      buffers: 100000000,
      swapTotal: 8000000000,
      swapUsed: 1000000000,
      swapFree: 7000000000
    },
    cpuDetails: {
      cores: 8,
      threads: 16,
      frequency: 3200,
      temperature: 42.5,
      load: [1.2, 1.1, 0.9],
      usage: [45, 52, 38, 41, 49, 43, 47, 44]
    },
    networkDetails: {
      bytesSent: 5000000000,
      bytesReceived: 8000000000,
      packetsSent: 5000000,
      packetsReceived: 8000000,
      errors: 5,
      dropped: 2,
      connections: 245,
      interfaces: {
        eth0: { bytesSent: 3000000000, bytesReceived: 5000000000 },
        wlan0: { bytesSent: 2000000000, bytesReceived: 3000000000 }
      }
    },
    compressionMetrics: {
      totalRequests: 1250,
      successfulRequests: 1230,
      failedRequests: 20,
      averageCompressionRatio: 3.1,
      averageProcessingTime: 0.045,
      throughput: 1500,
      algorithmUsage: {
        gzip: 40,
        zstd: 35,
        lzma: 25
      },
      contentTypeDistribution: {
        text: 45,
        binary: 30,
        structured: 20,
        mixed: 5
      },
      errorDistribution: {
        timeout: 5,
        invalid_input: 3,
        algorithm_error: 2,
        system_error: 1
      },
      performanceHistory: Array.from({ length: 24 }, (_, i) => ({
        timestamp: Date.now() - (23 - i) * 3600000,
        compressionRatio: 3.1 + Math.random() * 0.5,
        processingTime: 30 + Math.random() * 100,
        throughput: 1200 + Math.random() * 600,
        errorRate: Math.random() * 2
      }))
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering Tests', () => {
    test('renders loading state when metrics are loading', () => {
      mockUseMetrics.mockReturnValue({
        metrics: null,
        loading: true,
        error: null,
        lastUpdated: null,
        dashboardData: null,
        algorithmMetrics: null,
        trendsData: null,
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByText('Loading system metrics...')).toBeInTheDocument();
      expect(screen.getByRole('status')).toBeInTheDocument(); // Loading spinner
    });

    test('renders error state when metrics fail to load', () => {
      mockUseMetrics.mockReturnValue({
        metrics: null,
        loading: false,
        error: 'Failed to fetch metrics data',
        lastUpdated: null,
        dashboardData: null,
        algorithmMetrics: null,
        trendsData: null,
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByText('Failed to load metrics')).toBeInTheDocument();
      expect(screen.getByText('Failed to fetch metrics data')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    test('renders metrics dashboard when data is loaded', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date('2025-08-31T15:00:00Z'),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByText('System Metrics & Analytics')).toBeInTheDocument();
      expect(screen.getByText('CPU Usage')).toBeInTheDocument();
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
      expect(screen.getByText('Disk Usage')).toBeInTheDocument();
      expect(screen.getByText('Network Usage')).toBeInTheDocument();
    });

    test('displays correct metric values', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date('2025-08-31T15:00:00Z'),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByText('45.2%')).toBeInTheDocument(); // CPU
      expect(screen.getByText('67.8%')).toBeInTheDocument(); // Memory
      expect(screen.getByText('23.4%')).toBeInTheDocument(); // Disk
      expect(screen.getByText('12.1%')).toBeInTheDocument(); // Network
    });
  });

  describe('Data Loading Tests', () => {
    test('calls useMetrics hook with correct parameters', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date(),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(mockUseMetrics).toHaveBeenCalledWith({
        autoRefresh: true,
        refreshInterval: 10000,
        timeRange: 'day'
      });
    });

    test('handles stale data indicator', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date(Date.now() - 30000), // 30 seconds ago
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: true
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByText('(stale)')).toBeInTheDocument();
    });
  });

  describe('Error Handling Tests', () => {
    test('handles network errors gracefully', () => {
      mockUseMetrics.mockReturnValue({
        metrics: null,
        loading: false,
        error: 'Network Error: Failed to fetch',
        lastUpdated: null,
        dashboardData: null,
        algorithmMetrics: null,
        trendsData: null,
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByText('Failed to load metrics')).toBeInTheDocument();
      expect(screen.getByText('Network Error: Failed to fetch')).toBeInTheDocument();
    });

    test('handles API errors gracefully', () => {
      mockUseMetrics.mockReturnValue({
        metrics: null,
        loading: false,
        error: 'API Error: 500 Internal Server Error',
        lastUpdated: null,
        dashboardData: null,
        algorithmMetrics: null,
        trendsData: null,
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByText('Failed to load metrics')).toBeInTheDocument();
      expect(screen.getByText('API Error: 500 Internal Server Error')).toBeInTheDocument();
    });

    test('retry button calls refresh function', async () => {
      const mockRefresh = jest.fn();
      mockUseMetrics.mockReturnValue({
        metrics: null,
        loading: false,
        error: 'Test error',
        lastUpdated: null,
        dashboardData: null,
        algorithmMetrics: null,
        trendsData: null,
        refresh: mockRefresh,
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);
      
      expect(mockRefresh).toHaveBeenCalledTimes(1);
    });
  });

  describe('Refresh Functionality Tests', () => {
    test('displays last updated timestamp', () => {
      const lastUpdated = new Date('2025-08-31T15:00:00Z');
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated,
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
    });

    test('handles missing last updated timestamp', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: null,
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.queryByText(/Last updated:/)).not.toBeInTheDocument();
    });
  });

  describe('Metric Card Tests', () => {
    test('displays all metric cards with correct data', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date(),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      // Check for all metric cards
      expect(screen.getByText('CPU Usage')).toBeInTheDocument();
      expect(screen.getByText('Memory Usage')).toBeInTheDocument();
      expect(screen.getByText('Disk Usage')).toBeInTheDocument();
      expect(screen.getByText('Network Usage')).toBeInTheDocument();
      expect(screen.getByText('Compression Efficiency')).toBeInTheDocument();
      expect(screen.getByText('Throughput')).toBeInTheDocument();
      expect(screen.getByText('Success Rate')).toBeInTheDocument();
      expect(screen.getByText('Response Time')).toBeInTheDocument();
    });

    test('displays correct status indicators', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date(),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      // Check for status indicators (healthy/warning/error)
      const statusIcons = screen.getAllByTestId('status-icon');
      expect(statusIcons.length).toBeGreaterThan(0);
    });

    test('displays correct trend indicators', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date(),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      // Check for trend indicators (up/down/stable)
      const trendIcons = screen.getAllByTestId('trend-icon');
      expect(trendIcons.length).toBeGreaterThan(0);
    });
  });

  describe('Fallback Data Tests', () => {
    test('handles missing metrics data gracefully', () => {
      mockUseMetrics.mockReturnValue({
        metrics: null,
        loading: false,
        error: null,
        lastUpdated: new Date(),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      // Should render with fallback data (all zeros)
      expect(screen.getByText('0%')).toBeInTheDocument(); // CPU
      expect(screen.getByText('0%')).toBeInTheDocument(); // Memory
      expect(screen.getByText('0%')).toBeInTheDocument(); // Disk
      expect(screen.getByText('0%')).toBeInTheDocument(); // Network
    });

    test('handles partial metrics data', () => {
      const partialMetrics = {
        ...mockMetrics,
        cpu: undefined,
        memory: null,
        disk: 0
      };

      mockUseMetrics.mockReturnValue({
        metrics: partialMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date(),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      // Should handle undefined/null values gracefully
      expect(screen.getByText('0%')).toBeInTheDocument(); // CPU fallback
      expect(screen.getByText('0%')).toBeInTheDocument(); // Memory fallback
      expect(screen.getByText('0%')).toBeInTheDocument(); // Disk fallback
    });
  });

  describe('Accessibility Tests', () => {
    test('has proper ARIA labels', () => {
      mockUseMetrics.mockReturnValue({
        metrics: mockMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date(),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      // Check for accessibility attributes
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument();
    });

    test('loading state is accessible', () => {
      mockUseMetrics.mockReturnValue({
        metrics: null,
        loading: true,
        error: null,
        lastUpdated: null,
        dashboardData: null,
        algorithmMetrics: null,
        trendsData: null,
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByRole('status')).toBeInTheDocument();
      expect(screen.getByText('Loading system metrics...')).toBeInTheDocument();
    });

    test('error state is accessible', () => {
      mockUseMetrics.mockReturnValue({
        metrics: null,
        loading: false,
        error: 'Test error message',
        lastUpdated: null,
        dashboardData: null,
        algorithmMetrics: null,
        trendsData: null,
        refresh: jest.fn(),
        isStale: false
      });

      render(<MetricsTab state={{}} />);
      
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Test error message')).toBeInTheDocument();
    });
  });

  describe('Performance Tests', () => {
    test('renders efficiently with large datasets', () => {
      const largeMetrics = {
        ...mockMetrics,
        compressionMetrics: {
          ...mockMetrics.compressionMetrics,
          performanceHistory: Array.from({ length: 1000 }, (_, i) => ({
            timestamp: Date.now() - i * 60000,
            compressionRatio: 3.1 + Math.random() * 0.5,
            processingTime: 30 + Math.random() * 100,
            throughput: 1200 + Math.random() * 600,
            errorRate: Math.random() * 2
          }))
        }
      };

      mockUseMetrics.mockReturnValue({
        metrics: largeMetrics,
        loading: false,
        error: null,
        lastUpdated: new Date(),
        dashboardData: {},
        algorithmMetrics: {},
        trendsData: {},
        refresh: jest.fn(),
        isStale: false
      });

      const startTime = performance.now();
      render(<MetricsTab state={{}} />);
      const endTime = performance.now();

      // Should render within reasonable time (less than 100ms)
      expect(endTime - startTime).toBeLessThan(100);
    });
  });
});
