/**
 * Cloud Services API Client
 * 
 * This module provides the frontend API client for cloud services,
 * including cloud providers, accounts, resources, metrics, and optimization.
 */

export interface CloudProvider {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  api_endpoint?: string;
  documentation_url?: string;
  logo_url?: string;
  supported_regions?: Record<string, any>;
  supported_services?: Record<string, any>;
  pricing_model?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CloudAccount {
  id: number;
  provider_id: number;
  account_name: string;
  account_id: string;
  region: string;
  is_active: boolean;
  last_sync?: string;
  sync_status: string;
  error_message?: string;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface CloudResource {
  id: number;
  provider_id: number;
  account_id: number;
  resource_id: string;
  resource_name: string;
  resource_type: string;
  service_name: string;
  region: string;
  status: string;
  size?: string;
  cost_per_hour?: number;
  tags?: Record<string, any>;
  metadata?: Record<string, any>;
  is_monitored: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CloudMetrics {
  id: number;
  provider_id: number;
  account_id: number;
  resource_id?: number;
  metric_name: string;
  metric_value: number;
  metric_unit: string;
  timestamp: string;
  dimensions?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at?: string;
}

export interface CloudCosts {
  id: number;
  provider_id: number;
  account_id: number;
  resource_id?: number;
  cost_date: string;
  service_name: string;
  cost_amount: number;
  currency: string;
  cost_category?: string;
  tags?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at?: string;
}

export interface CloudAlerts {
  id: number;
  account_id: number;
  alert_type: string;
  alert_name: string;
  alert_description?: string;
  threshold_value?: number;
  current_value?: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: string;
  is_enabled: boolean;
  notification_channels?: Record<string, any>;
  conditions?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  triggered_at?: string;
  resolved_at?: string;
}

export interface CloudOptimization {
  id: number;
  account_id: number;
  optimization_type: string;
  title: string;
  description?: string;
  potential_savings?: number;
  implementation_effort?: 'low' | 'medium' | 'high';
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: string;
  recommendations?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
  implemented_at?: string;
}

export interface DashboardData {
  total_cost: number;
  cost_trend: number;
  total_resources: number;
  active_resources: number;
  alerts_count: number;
  critical_alerts: number;
  optimization_opportunities: number;
  potential_savings: number;
  top_services_by_cost: Array<{service: string; cost: number}>;
  recent_alerts: CloudAlerts[];
  recent_optimizations: CloudOptimization[];
}

export interface CostTrends {
  daily_costs: Array<{date: string; cost: number}>;
  monthly_costs: Array<{month: string; cost: number}>;
  cost_by_service: Array<{service: string; cost: number}>;
  cost_by_region: Array<{region: string; cost: number}>;
  cost_prediction: Array<{date: string; predicted_cost: number}>;
}

export interface PerformanceAnalytics {
  cpu_utilization: Array<{timestamp: string; value: number; resource_id: number}>;
  memory_utilization: Array<{timestamp: string; value: number; resource_id: number}>;
  network_utilization: Array<{timestamp: string; metric_name: string; value: number; resource_id: number}>;
  storage_utilization: Array<{timestamp: string; value: number; resource_id: number}>;
  performance_metrics: Record<string, any>;
  resource_efficiency: Array<{
    resource_id: number;
    resource_name: string;
    resource_type: string;
    avg_cpu: number;
    avg_memory: number;
    efficiency_status: string;
    recommendation: string;
  }>;
}

class CloudServiceAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Cloud Providers
  async getProviders(params?: {
    skip?: number;
    limit?: number;
    active_only?: boolean;
  }): Promise<CloudProvider[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.active_only !== undefined) searchParams.append('active_only', params.active_only.toString());

    const queryString = searchParams.toString();
    return this.request<CloudProvider[]>(`/api/v1/cloud-services/providers${queryString ? `?${queryString}` : ''}`);
  }

  async createProvider(provider: Omit<CloudProvider, 'id' | 'created_at' | 'updated_at'>): Promise<CloudProvider> {
    return this.request<CloudProvider>('/api/v1/cloud-services/providers', {
      method: 'POST',
      body: JSON.stringify(provider),
    });
  }

  // Cloud Accounts
  async getAccounts(params?: {
    skip?: number;
    limit?: number;
    provider_id?: number;
    active_only?: boolean;
  }): Promise<CloudAccount[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.provider_id) searchParams.append('provider_id', params.provider_id.toString());
    if (params?.active_only !== undefined) searchParams.append('active_only', params.active_only.toString());

    const queryString = searchParams.toString();
    return this.request<CloudAccount[]>(`/api/v1/cloud-services/accounts${queryString ? `?${queryString}` : ''}`);
  }

  async createAccount(account: Omit<CloudAccount, 'id' | 'created_at' | 'updated_at'>): Promise<CloudAccount> {
    return this.request<CloudAccount>('/api/v1/cloud-services/accounts', {
      method: 'POST',
      body: JSON.stringify(account),
    });
  }

  async syncAccountResources(accountId: number): Promise<{message: string; account_id: number}> {
    return this.request<{message: string; account_id: number}>(`/api/v1/cloud-services/accounts/${accountId}/sync`, {
      method: 'POST',
    });
  }

  // Cloud Resources
  async getResources(params?: {
    skip?: number;
    limit?: number;
    account_id?: number;
    provider_id?: number;
    resource_type?: string;
    status?: string;
    monitored_only?: boolean;
  }): Promise<CloudResource[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.account_id) searchParams.append('account_id', params.account_id.toString());
    if (params?.provider_id) searchParams.append('provider_id', params.provider_id.toString());
    if (params?.resource_type) searchParams.append('resource_type', params.resource_type);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.monitored_only !== undefined) searchParams.append('monitored_only', params.monitored_only.toString());

    const queryString = searchParams.toString();
    return this.request<CloudResource[]>(`/api/v1/cloud-services/resources${queryString ? `?${queryString}` : ''}`);
  }

  // Cloud Metrics
  async getMetrics(params?: {
    skip?: number;
    limit?: number;
    account_id?: number;
    resource_id?: number;
    metric_name?: string;
    start_time?: string;
    end_time?: string;
  }): Promise<CloudMetrics[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.account_id) searchParams.append('account_id', params.account_id.toString());
    if (params?.resource_id) searchParams.append('resource_id', params.resource_id.toString());
    if (params?.metric_name) searchParams.append('metric_name', params.metric_name);
    if (params?.start_time) searchParams.append('start_time', params.start_time);
    if (params?.end_time) searchParams.append('end_time', params.end_time);

    const queryString = searchParams.toString();
    return this.request<CloudMetrics[]>(`/api/v1/cloud-services/metrics${queryString ? `?${queryString}` : ''}`);
  }

  // Cloud Costs
  async getCosts(params?: {
    skip?: number;
    limit?: number;
    account_id?: number;
    start_date?: string;
    end_date?: string;
    service_name?: string;
  }): Promise<CloudCosts[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.account_id) searchParams.append('account_id', params.account_id.toString());
    if (params?.start_date) searchParams.append('start_date', params.start_date);
    if (params?.end_date) searchParams.append('end_date', params.end_date);
    if (params?.service_name) searchParams.append('service_name', params.service_name);

    const queryString = searchParams.toString();
    return this.request<CloudCosts[]>(`/api/v1/cloud-services/costs${queryString ? `?${queryString}` : ''}`);
  }

  // Cloud Alerts
  async getAlerts(params?: {
    skip?: number;
    limit?: number;
    account_id?: number;
    alert_type?: string;
    severity?: string;
    status?: string;
  }): Promise<CloudAlerts[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.account_id) searchParams.append('account_id', params.account_id.toString());
    if (params?.alert_type) searchParams.append('alert_type', params.alert_type);
    if (params?.severity) searchParams.append('severity', params.severity);
    if (params?.status) searchParams.append('status', params.status);

    const queryString = searchParams.toString();
    return this.request<CloudAlerts[]>(`/api/v1/cloud-services/alerts${queryString ? `?${queryString}` : ''}`);
  }

  // Cloud Optimizations
  async getOptimizations(params?: {
    skip?: number;
    limit?: number;
    account_id?: number;
    optimization_type?: string;
    priority?: string;
    status?: string;
  }): Promise<CloudOptimization[]> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.append('skip', params.skip.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.account_id) searchParams.append('account_id', params.account_id.toString());
    if (params?.optimization_type) searchParams.append('optimization_type', params.optimization_type);
    if (params?.priority) searchParams.append('priority', params.priority);
    if (params?.status) searchParams.append('status', params.status);

    const queryString = searchParams.toString();
    return this.request<CloudOptimization[]>(`/api/v1/cloud-services/optimizations${queryString ? `?${queryString}` : ''}`);
  }

  // Analytics
  async getDashboard(accountId?: number, days: number = 30): Promise<DashboardData> {
    const searchParams = new URLSearchParams();
    if (accountId) searchParams.append('account_id', accountId.toString());
    searchParams.append('days', days.toString());

    const queryString = searchParams.toString();
    return this.request<DashboardData>(`/api/v1/cloud-services/analytics/dashboard?${queryString}`);
  }

  async getCostTrends(accountId?: number, days: number = 30): Promise<CostTrends> {
    const searchParams = new URLSearchParams();
    if (accountId) searchParams.append('account_id', accountId.toString());
    searchParams.append('days', days.toString());

    const queryString = searchParams.toString();
    return this.request<CostTrends>(`/api/v1/cloud-services/analytics/cost-trends?${queryString}`);
  }

  async getPerformanceAnalytics(accountId?: number, days: number = 7): Promise<PerformanceAnalytics> {
    const searchParams = new URLSearchParams();
    if (accountId) searchParams.append('account_id', accountId.toString());
    searchParams.append('days', days.toString());

    const queryString = searchParams.toString();
    return this.request<PerformanceAnalytics>(`/api/v1/cloud-services/analytics/performance?${queryString}`);
  }

  // Optimization
  async runOptimizationAnalysis(accountId: number): Promise<{message: string; account_id: number}> {
    return this.request<{message: string; account_id: number}>(`/api/v1/cloud-services/optimize`, {
      method: 'POST',
      body: JSON.stringify({ account_id: accountId }),
    });
  }

  // Health Check
  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    services: Record<string, string>;
  }> {
    return this.request<{
      status: string;
      timestamp: string;
      services: Record<string, string>;
    }>('/api/v1/cloud-services/health');
  }
}

// Export singleton instance
export const cloudServiceAPI = new CloudServiceAPI();
export default cloudServiceAPI;
