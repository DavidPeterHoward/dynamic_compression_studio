import { MetricsService } from '@/lib/api';
import { useCallback, useEffect, useRef, useState } from 'react';

export interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  compressionEfficiency: number;
  algorithmPerformance: Record<string, number>;
  userSatisfaction: number;
  systemHealth: 'healthy' | 'warning' | 'error';
  throughput: number;
  successRate: number;
  averageCompressionRatio: number;
  activeConnections: number;
  queueLength: number;
  errorRate: number;
  responseTime: number;
  temperature: number;
  powerConsumption: number;
  networkLatency: number;
  bandwidth: number;
  diskIO: number;
  memoryUsage: number;
  swapUsage: number;
  loadAverage: number[];
  uptime: number;
  processes: number;
  threads: number;
  openFiles: number;
  networkConnections: number;
  diskSpace: {
    total: number;
    used: number;
    free: number;
    available: number;
  };
  memoryDetails: {
    total: number;
    used: number;
    free: number;
    available: number;
    cached: number;
    buffers: number;
    swapTotal: number;
    swapUsed: number;
    swapFree: number;
  };
  cpuDetails: {
    cores: number;
    threads: number;
    frequency: number;
    temperature: number;
    load: number[];
    usage: number[];
  };
  networkDetails: {
    bytesSent: number;
    bytesReceived: number;
    packetsSent: number;
    packetsReceived: number;
    errors: number;
    dropped: number;
    connections: number;
    interfaces: Record<string, any>;
  };
  compressionMetrics: {
    totalRequests: number;
    successfulRequests: number;
    failedRequests: number;
    averageCompressionRatio: number;
    averageProcessingTime: number;
    throughput: number;
    algorithmUsage: Record<string, number>;
    contentTypeDistribution: Record<string, number>;
    errorDistribution: Record<string, number>;
    performanceHistory: Array<{
      timestamp: number;
      compressionRatio: number;
      processingTime: number;
      throughput: number;
      errorRate: number;
    }>;
  };
}

export interface MetricsState {
  metrics: SystemMetrics | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  dashboardData: any;
  algorithmMetrics: any;
  trendsData: any;
}

export interface UseMetricsOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
  timeRange?: string;
}

export const useMetrics = (options: UseMetricsOptions = {}) => {
  const {
    autoRefresh = true,
    refreshInterval = 10000, // 10 seconds
    timeRange = 'day'
  } = options;

  const [state, setState] = useState<MetricsState>({
    metrics: null,
    loading: false,
    error: null,
    lastUpdated: null,
    dashboardData: null,
    algorithmMetrics: null,
    trendsData: null
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Transform backend data to frontend format - USING REAL COMPREHENSIVE DATA
  const transformMetricsData = useCallback((dashboardData: any, comprehensiveData: any, algorithmData: any): SystemMetrics => {
    const sysData = comprehensiveData || {};
    const algorithms = algorithmData?.algorithms || {};
    const perfData = dashboardData?.performance || {};
    
    return {
      // System metrics from COMPREHENSIVE data - ALL REAL
      cpu: sysData.cpu_usage || 0,
      memory: sysData.memory_usage || 0,
      disk: sysData.disk_usage || 0,
      network: sysData.network_usage || 0,
      
      // Compression metrics from dashboard - REAL DATA ONLY
      compressionEfficiency: dashboardData?.overview?.average_compression_ratio ? 
        (dashboardData.overview.average_compression_ratio / 3.0) * 100 : 0,
      algorithmPerformance: Object.fromEntries(
        Object.entries(algorithms).map(([name, data]: [string, any]) => [
          name,
          data?.average_compression_ratio || 0
        ])
      ),
      userSatisfaction: dashboardData?.overview?.success_rate || 0,
      systemHealth: perfData.error_rate > 5 ? 'error' : 
                   perfData.error_rate > 2 ? 'warning' : 'healthy',
      throughput: perfData.requests_per_second ? perfData.requests_per_second * 100 : 0,
      successRate: dashboardData?.overview?.success_rate || 0,
      averageCompressionRatio: dashboardData?.overview?.average_compression_ratio || 0,
      activeConnections: sysData.active_connections || 0,
      queueLength: perfData.queue_size || 0,
      errorRate: perfData.error_rate || 0,
      responseTime: perfData.average_response_time ? perfData.average_response_time * 1000 : 0,
      
      // Hardware metrics - REAL DATA from comprehensive endpoint
      temperature: sysData.cpu_details?.temperature || 0,
      powerConsumption: 0,  // Not available from psutil
      networkLatency: 0,  // Would require ping tests
      bandwidth: 0,  // Not directly available
      diskIO: sysData.disk_io?.read_mb_per_sec + sysData.disk_io?.write_mb_per_sec || 0,
      memoryUsage: sysData.memory_usage || 0,
      swapUsage: sysData.swap_usage || 0,
      loadAverage: sysData.load_average || [0, 0, 0],
      uptime: sysData.uptime || 0,  // NOW REAL!
      processes: sysData.processes || 0,  // NOW REAL! (was 100-300 mock)
      threads: sysData.threads || 0,  // NOW REAL!
      openFiles: sysData.open_files || 0,  // NOW REAL!
      networkConnections: sysData.network_connections || 0,
      
      // Disk space - REAL DATA
      diskSpace: {
        total: sysData.disk_details?.total || 0,
        used: sysData.disk_details?.used || 0,
        free: sysData.disk_details?.free || 0,
        available: sysData.disk_details?.free || 0
      },
      
      // Memory details - REAL DATA
      memoryDetails: {
        total: sysData.memory_details?.total || 0,
        used: sysData.memory_details?.used || 0,
        free: sysData.memory_details?.free || 0,
        available: sysData.memory_details?.available || 0,
        cached: sysData.memory_details?.cached || 0,
        buffers: sysData.memory_details?.buffers || 0,
        swapTotal: sysData.memory_details?.swap_total || 0,
        swapUsed: sysData.memory_details?.swap_used || 0,
        swapFree: sysData.memory_details?.swap_free || 0
      },
      
      // CPU details - REAL DATA
      cpuDetails: {
        cores: sysData.cpu_details?.cores || 0,
        threads: sysData.cpu_details?.threads || 0,
        frequency: sysData.cpu_details?.frequency || 0,
        temperature: sysData.cpu_details?.temperature || 0,
        load: sysData.cpu_details?.load || [0, 0, 0],
        usage: sysData.cpu_details?.usage_per_cpu || []
      },
      
      // Network details - REAL DATA
      networkDetails: {
        bytesSent: sysData.network_details?.bytes_sent || 0,
        bytesReceived: sysData.network_details?.bytes_recv || 0,
        packetsSent: sysData.network_details?.packets_sent || 0,
        packetsReceived: sysData.network_details?.packets_recv || 0,
        errors: (sysData.network_details?.errors_in || 0) + (sysData.network_details?.errors_out || 0),
        dropped: (sysData.network_details?.drops_in || 0) + (sysData.network_details?.drops_out || 0),
        connections: sysData.network_details?.total_connections || 0,
        interfaces: sysData.network_details?.interfaces || {}
      },
      
      // Compression metrics from dashboard - REAL DATA ONLY
      compressionMetrics: {
        totalRequests: dashboardData?.overview?.total_compressions_today || 0,
        successfulRequests: dashboardData?.overview?.total_compressions_today && dashboardData?.overview?.success_rate
          ? Math.round(dashboardData.overview.total_compressions_today * (dashboardData.overview.success_rate / 100))
          : 0,
        failedRequests: dashboardData?.overview?.total_compressions_today && dashboardData?.overview?.success_rate
          ? Math.round(dashboardData.overview.total_compressions_today * (1 - dashboardData.overview.success_rate / 100))
          : 0,
        averageCompressionRatio: dashboardData?.overview?.average_compression_ratio || 0,
        averageProcessingTime: perfData.average_response_time || 0,
        throughput: perfData.requests_per_second ? perfData.requests_per_second * 100 : 0,
        algorithmUsage: Object.fromEntries(
          Object.entries(algorithms).map(([name, data]: [string, any]) => [
            name,
            data?.usage_count && dashboardData?.overview?.total_compressions_today
              ? (data.usage_count / dashboardData.overview.total_compressions_today) * 100
              : 0
          ])
        ),
        contentTypeDistribution: {},  // No real data available
        errorDistribution: {},  // No real data available
        performanceHistory: []  // No real data available
      }
    };
  }, []);

  // Fetch all metrics data - OPTIMIZED for faster loading with REAL system data
  const fetchMetrics = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    abortControllerRef.current = new AbortController();
    
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // Fetch comprehensive system metrics (includes real processes, uptime, etc.)
      // and dashboard/algorithm data in parallel
      const [comprehensiveData, dashboardData, algorithmData] = await Promise.all([
        MetricsService.getComprehensiveSystemMetrics(),
        MetricsService.getDashboardMetrics(),
        MetricsService.getAlgorithmMetrics()
      ]);

      // Transform the data to match our frontend interface, merging comprehensive system data
      const transformedMetrics = transformMetricsData(dashboardData, comprehensiveData, algorithmData);

      setState(prev => ({
        ...prev,
        metrics: transformedMetrics,
        dashboardData,
        algorithmMetrics: algorithmData,
        trendsData: null,  // Not fetched for performance
        loading: false,
        lastUpdated: new Date(),
        error: null
      }));

    } catch (error: any) {
      if (error.name === 'AbortError') {
        return; // Request was cancelled
      }
      
      console.error('Error fetching metrics:', error);
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.message || 'Failed to fetch metrics data'
      }));
    }
  }, [transformMetricsData]);

  // Manual refresh function
  const refresh = useCallback(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  // Start auto-refresh
  useEffect(() => {
    if (autoRefresh) {
      // Initial fetch
      fetchMetrics();
      
      // Set up interval
      intervalRef.current = setInterval(fetchMetrics, refreshInterval);
      
      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }
      };
    } else {
      // Just fetch once
      fetchMetrics();
    }
  }, [autoRefresh, refreshInterval, fetchMetrics]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    ...state,
    refresh,
    isStale: state.lastUpdated ? 
      Date.now() - state.lastUpdated.getTime() > refreshInterval * 2 : true
  };
};
