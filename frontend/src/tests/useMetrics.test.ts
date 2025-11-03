import { renderHook, act, waitFor } from '@testing-library/react';
import { useMetrics } from '../hooks/useMetrics';
import { MetricsService } from '../lib/api';

// Mock the MetricsService
jest.mock('../lib/api', () => ({
  MetricsService: {
    getDashboardMetrics: jest.fn(),
    getPerformanceMetrics: jest.fn(),
    getAlgorithmMetrics: jest.fn(),
    getMetricsTrends: jest.fn()
  }
}));

const mockMetricsService = MetricsService as jest.Mocked<typeof MetricsService>;

describe('useMetrics Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  const mockDashboardData = {
    overview: {
      total_compressions_today: 1250,
      total_compressions_week: 8750,
      total_compressions_month: 37500,
      average_compression_ratio: 3.1,
      success_rate: 98.7,
      total_data_saved: 1500000000
    },
    performance: {
      cpu_usage: 45.2,
      memory_usage: 67.8,
      disk_usage: 23.4,
      requests_per_second: 15.5,
      average_response_time: 0.045,
      error_rate: 1.3
    },
    top_algorithms: [
      {
        algorithm: 'gzip',
        usage_count: 500,
        average_ratio: 2.5,
        success_rate: 99.2
      },
      {
        algorithm: 'zstd',
        usage_count: 350,
        average_ratio: 3.2,
        success_rate: 98.8
      }
    ]
  };

  const mockPerformanceData = {
    cpu_usage: 45.2,
    memory_usage: 67.8,
    disk_usage: 23.4,
    network_usage: 12.1,
    active_connections: 245,
    requests_per_second: 15.5,
    average_response_time: 0.045,
    error_rate: 1.3,
    queue_size: 5,
    queue_processing_rate: 15.5,
    average_wait_time: 0.032
  };

  const mockAlgorithmData = {
    algorithms: {
      gzip: {
        usage_count: 500,
        average_compression_ratio: 2.5,
        success_rate: 99.2,
        average_processing_time: 0.032
      },
      zstd: {
        usage_count: 350,
        average_compression_ratio: 3.2,
        success_rate: 98.8,
        average_processing_time: 0.045
      },
      lzma: {
        usage_count: 200,
        average_compression_ratio: 4.1,
        success_rate: 97.5,
        average_processing_time: 0.078
      }
    }
  };

  const mockTrendsData = {
    metric_type: 'compression_ratio',
    time_range: 'day',
    data: [
      { timestamp: '2025-08-31T14:00:00Z', value: 3.1 },
      { timestamp: '2025-08-31T15:00:00Z', value: 3.2 },
      { timestamp: '2025-08-31T16:00:00Z', value: 3.0 }
    ]
  };

  describe('Initial State', () => {
    test('returns initial state with default options', () => {
      const { result } = renderHook(() => useMetrics());

      expect(result.current.metrics).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.lastUpdated).toBeNull();
      expect(result.current.dashboardData).toBeNull();
      expect(result.current.algorithmMetrics).toBeNull();
      expect(result.current.trendsData).toBeNull();
      expect(typeof result.current.refresh).toBe('function');
      expect(result.current.isStale).toBe(true);
    });

    test('returns initial state with custom options', () => {
      const { result } = renderHook(() => useMetrics({
        autoRefresh: false,
        refreshInterval: 5000,
        timeRange: 'week'
      }));

      expect(result.current.metrics).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.lastUpdated).toBeNull();
    });
  });

  describe('Data Fetching', () => {
    test('fetches data successfully on mount with autoRefresh enabled', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics({ autoRefresh: true }));

      // Should start loading
      expect(result.current.loading).toBe(true);

      // Wait for data to be fetched
      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.metrics).not.toBeNull();
      expect(result.current.error).toBeNull();
      expect(result.current.lastUpdated).not.toBeNull();
      expect(result.current.dashboardData).toEqual(mockDashboardData);
      expect(result.current.algorithmMetrics).toEqual(mockAlgorithmData);
      expect(result.current.trendsData).toEqual(mockTrendsData);

      // Verify API calls
      expect(mockMetricsService.getDashboardMetrics).toHaveBeenCalledTimes(1);
      expect(mockMetricsService.getPerformanceMetrics).toHaveBeenCalledTimes(1);
      expect(mockMetricsService.getAlgorithmMetrics).toHaveBeenCalledTimes(1);
      expect(mockMetricsService.getMetricsTrends).toHaveBeenCalledWith('compression_ratio', 'day');
    });

    test('fetches data once when autoRefresh is disabled', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics({ autoRefresh: false }));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.metrics).not.toBeNull();
      expect(result.current.error).toBeNull();

      // Should not set up interval
      expect(setInterval).not.toHaveBeenCalled();
    });

    test('transforms data correctly', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const metrics = result.current.metrics;
      expect(metrics).not.toBeNull();

      if (metrics) {
        // Check transformed values
        expect(metrics.cpu).toBe(45.2);
        expect(metrics.memory).toBe(67.8);
        expect(metrics.disk).toBe(23.4);
        expect(metrics.network).toBe(12.1);
        expect(metrics.compressionEfficiency).toBeCloseTo(103.33, 1); // (3.1 / 3.0) * 100
        expect(metrics.successRate).toBe(98.7);
        expect(metrics.averageCompressionRatio).toBe(3.1);
        expect(metrics.activeConnections).toBe(245);
        expect(metrics.throughput).toBe(1550); // requests_per_second * 100
        expect(metrics.responseTime).toBe(45); // average_response_time * 1000
        expect(metrics.errorRate).toBe(1.3);
      }
    });
  });

  describe('Error Handling', () => {
    test('handles API errors gracefully', async () => {
      const errorMessage = 'Failed to fetch metrics';
      mockMetricsService.getDashboardMetrics.mockRejectedValue(new Error(errorMessage));

      const { result } = renderHook(() => useMetrics());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe(errorMessage);
      expect(result.current.metrics).toBeNull();
      expect(result.current.lastUpdated).toBeNull();
    });

    test('handles network errors', async () => {
      const networkError = new Error('Network Error');
      mockMetricsService.getDashboardMetrics.mockRejectedValue(networkError);

      const { result } = renderHook(() => useMetrics());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe('Network Error');
      expect(result.current.metrics).toBeNull();
    });

    test('handles partial API failures', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockRejectedValue(new Error('Performance API failed'));
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Should still have some data even if one API fails
      expect(result.current.metrics).not.toBeNull();
      expect(result.current.error).toBe('Failed to fetch metrics data');
    });
  });

  describe('Auto Refresh', () => {
    test('sets up auto refresh interval', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      renderHook(() => useMetrics({ autoRefresh: true, refreshInterval: 5000 }));

      // Wait for initial fetch
      await waitFor(() => {
        expect(mockMetricsService.getDashboardMetrics).toHaveBeenCalledTimes(1);
      });

      // Fast-forward time to trigger refresh
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      // Should fetch again
      await waitFor(() => {
        expect(mockMetricsService.getDashboardMetrics).toHaveBeenCalledTimes(2);
      });
    });

    test('cleans up interval on unmount', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { unmount } = renderHook(() => useMetrics({ autoRefresh: true }));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      unmount();

      // Fast-forward time - should not trigger another fetch
      act(() => {
        jest.advanceTimersByTime(10000);
      });

      expect(mockMetricsService.getDashboardMetrics).toHaveBeenCalledTimes(1);
    });
  });

  describe('Manual Refresh', () => {
    test('refresh function triggers new data fetch', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics({ autoRefresh: false }));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const initialLastUpdated = result.current.lastUpdated;

      // Call refresh
      act(() => {
        result.current.refresh();
      });

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.lastUpdated).not.toBe(initialLastUpdated);
      expect(mockMetricsService.getDashboardMetrics).toHaveBeenCalledTimes(2);
    });

    test('refresh cancels previous requests', async () => {
      // Make the first call slow
      mockMetricsService.getDashboardMetrics.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve(mockDashboardData), 1000))
      );
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics({ autoRefresh: false }));

      // Start first fetch
      act(() => {
        result.current.refresh();
      });

      // Start second fetch immediately (should cancel first)
      act(() => {
        result.current.refresh();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Should only have one successful fetch
      expect(mockMetricsService.getDashboardMetrics).toHaveBeenCalledTimes(2);
    });
  });

  describe('Data Staleness', () => {
    test('marks data as stale after refresh interval', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics({ 
        autoRefresh: false, 
        refreshInterval: 10000 
      }));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.isStale).toBe(false);

      // Fast-forward past the refresh interval
      act(() => {
        jest.advanceTimersByTime(20000); // 2x refresh interval
      });

      expect(result.current.isStale).toBe(true);
    });

    test('handles missing lastUpdated timestamp', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics({ autoRefresh: false }));

      // Before data is loaded
      expect(result.current.isStale).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.isStale).toBe(false);
    });
  });

  describe('Data Transformation', () => {
    test('handles missing or null data gracefully', async () => {
      const incompleteData = {
        overview: {
          total_compressions_today: 0,
          average_compression_ratio: 0,
          success_rate: 0
        },
        performance: {
          cpu_usage: null,
          memory_usage: undefined,
          disk_usage: 0,
          requests_per_second: 0,
          average_response_time: 0,
          error_rate: 0
        }
      };

      mockMetricsService.getDashboardMetrics.mockResolvedValue(incompleteData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue({});
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue({});
      mockMetricsService.getMetricsTrends.mockResolvedValue({});

      const { result } = renderHook(() => useMetrics());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const metrics = result.current.metrics;
      expect(metrics).not.toBeNull();

      if (metrics) {
        // Should handle null/undefined values
        expect(metrics.cpu).toBe(0);
        expect(metrics.memory).toBe(0);
        expect(metrics.disk).toBe(0);
        expect(metrics.compressionEfficiency).toBe(0);
        expect(metrics.successRate).toBe(0);
        expect(metrics.averageCompressionRatio).toBe(0);
      }
    });

    test('calculates derived metrics correctly', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const metrics = result.current.metrics;
      expect(metrics).not.toBeNull();

      if (metrics) {
        // Check derived calculations
        expect(metrics.throughput).toBe(1550); // 15.5 * 100
        expect(metrics.responseTime).toBe(45); // 0.045 * 1000
        expect(metrics.compressionEfficiency).toBeCloseTo(103.33, 1); // (3.1 / 3.0) * 100
        expect(metrics.systemHealth).toBe('healthy'); // error_rate < 2
      }
    });
  });

  describe('Performance', () => {
    test('handles rapid refresh calls efficiently', async () => {
      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(mockAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const { result } = renderHook(() => useMetrics({ autoRefresh: false }));

      // Call refresh multiple times rapidly
      act(() => {
        result.current.refresh();
        result.current.refresh();
        result.current.refresh();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // Should only make one successful API call
      expect(mockMetricsService.getDashboardMetrics).toHaveBeenCalledTimes(1);
    });

    test('handles large datasets efficiently', async () => {
      const largeAlgorithmData = {
        algorithms: Object.fromEntries(
          Array.from({ length: 100 }, (_, i) => [
            `algorithm_${i}`,
            {
              usage_count: 100 + i,
              average_compression_ratio: 2.0 + (i * 0.1),
              success_rate: 95 + (i * 0.1),
              average_processing_time: 0.03 + (i * 0.001)
            }
          ])
        )
      };

      mockMetricsService.getDashboardMetrics.mockResolvedValue(mockDashboardData);
      mockMetricsService.getPerformanceMetrics.mockResolvedValue(mockPerformanceData);
      mockMetricsService.getAlgorithmMetrics.mockResolvedValue(largeAlgorithmData);
      mockMetricsService.getMetricsTrends.mockResolvedValue(mockTrendsData);

      const startTime = performance.now();
      
      const { result } = renderHook(() => useMetrics({ autoRefresh: false }));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const endTime = performance.now();
      const processingTime = endTime - startTime;

      // Should process large datasets efficiently (less than 100ms)
      expect(processingTime).toBeLessThan(100);
      expect(result.current.metrics).not.toBeNull();
    });
  });
});
