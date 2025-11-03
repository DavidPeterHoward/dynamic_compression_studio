"use client";

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    Activity,
    AlertTriangle,
    BarChart3,
    Cloud,
    DollarSign,
    Server,
    Zap
} from 'lucide-react';
import { useEffect, useState } from 'react';

interface CloudProvider {
  id: number;
  name: string;
  display_name: string;
  logo_url?: string;
  is_active: boolean;
}

interface CloudAccount {
  id: number;
  account_name: string;
  provider_id: number;
  region: string;
  is_active: boolean;
  last_sync?: string;
  sync_status: string;
}

interface CloudResource {
  id: number;
  resource_name: string;
  resource_type: string;
  service_name: string;
  status: string;
  region: string;
  cost_per_hour?: number;
  is_monitored: boolean;
}

interface DashboardData {
  total_cost: number;
  cost_trend: number;
  total_resources: number;
  active_resources: number;
  alerts_count: number;
  critical_alerts: number;
  optimization_opportunities: number;
  potential_savings: number;
  top_services_by_cost: Array<{service: string; cost: number}>;
}

export default function CloudServicesTab() {
  const [providers, setProviders] = useState<CloudProvider[]>([]);
  const [accounts, setAccounts] = useState<CloudAccount[]>([]);
  const [resources, setResources] = useState<CloudResource[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedAccount, setSelectedAccount] = useState<number | null>(null);

  useEffect(() => {
    fetchCloudData();
  }, []);

  const fetchCloudData = async () => {
    try {
      setLoading(true);
      
      // Fetch providers
      const providersResponse = await fetch('/api/v1/cloud-services/providers');
      const providersData = await providersResponse.json();
      setProviders(providersData);

      // Fetch accounts
      const accountsResponse = await fetch('/api/v1/cloud-services/accounts');
      const accountsData = await accountsResponse.json();
      setAccounts(accountsData);

      // Fetch resources
      const resourcesResponse = await fetch('/api/v1/cloud-services/resources');
      const resourcesData = await resourcesResponse.json();
      setResources(resourcesData);

      // Fetch dashboard data
      const dashboardResponse = await fetch('/api/v1/cloud-services/analytics/dashboard');
      const dashboardData = await dashboardResponse.json();
      setDashboardData(dashboardData);

    } catch (error) {
      console.error('Error fetching cloud data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'running':
      case 'active':
        return 'bg-green-500';
      case 'stopped':
      case 'inactive':
        return 'bg-yellow-500';
      case 'terminated':
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Cloud className="h-8 w-8 text-blue-500" />
          <h1 className="text-3xl font-bold">Cloud Services</h1>
        </div>
        <Button onClick={fetchCloudData} className="bg-blue-500 hover:bg-blue-600">
          <Activity className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Dashboard Overview */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(dashboardData.total_cost)}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.cost_trend > 0 ? '+' : ''}{dashboardData.cost_trend.toFixed(1)}% from last period
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Resources</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.active_resources}/{dashboardData.total_resources}</div>
              <p className="text-xs text-muted-foreground">Active resources</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Alerts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.alerts_count}</div>
              <p className="text-xs text-muted-foreground">
                {dashboardData.critical_alerts} critical
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Optimization</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{dashboardData.optimization_opportunities}</div>
              <p className="text-xs text-muted-foreground">
                {formatCurrency(dashboardData.potential_savings)} potential savings
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="resources">Resources</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="optimization">Optimization</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Cloud Accounts */}
            <Card>
              <CardHeader>
                <CardTitle>Cloud Accounts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {accounts.map((account) => (
                    <div key={account.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                          <Cloud className="h-5 w-5 text-blue-500" />
                        </div>
                        <div>
                          <p className="font-medium">{account.account_name}</p>
                          <p className="text-sm text-muted-foreground">{account.region}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={account.is_active ? "default" : "secondary"}>
                          {account.sync_status}
                        </Badge>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setSelectedAccount(account.id)}
                        >
                          View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Top Services by Cost */}
            <Card>
              <CardHeader>
                <CardTitle>Top Services by Cost</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData?.top_services_by_cost.map((service, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                          <BarChart3 className="h-4 w-4 text-gray-500" />
                        </div>
                        <span className="font-medium">{service.service}</span>
                      </div>
                      <span className="font-bold">{formatCurrency(service.cost)}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="resources" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cloud Resources</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {resources.map((resource) => (
                  <div key={resource.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(resource.status)}`}></div>
                      <div>
                        <p className="font-medium">{resource.resource_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {resource.service_name} • {resource.resource_type} • {resource.region}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {resource.cost_per_hour && (
                        <span className="text-sm font-medium">
                          {formatCurrency(resource.cost_per_hour)}/hr
                        </span>
                      )}
                      <Badge variant="outline">{resource.status}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Cost Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-muted-foreground">
                  Cost trend chart would go here
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-muted-foreground">
                  Performance metrics chart would go here
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="optimization" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Optimization Opportunities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Unused Resources</h3>
                      <p className="text-sm text-muted-foreground">
                        Found 3 unused resources that could be terminated
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-green-600">$45.20/month savings</p>
                      <Button size="sm" className="mt-2">Implement</Button>
                    </div>
                  </div>
                </div>

                <div className="p-4 border rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">Oversized Resources</h3>
                      <p className="text-sm text-muted-foreground">
                        Found 2 resources that could be downsized
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-green-600">$23.50/month savings</p>
                      <Button size="sm" className="mt-2">Implement</Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cloud Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg border-red-200 bg-red-50">
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="h-5 w-5 text-red-500" />
                    <div>
                      <h3 className="font-medium text-red-900">High CPU Usage</h3>
                      <p className="text-sm text-red-700">
                        CPU utilization is above 90% for the last 15 minutes
                      </p>
                    </div>
                    <Badge variant="destructive">Critical</Badge>
                  </div>
                </div>

                <div className="p-4 border rounded-lg border-yellow-200 bg-yellow-50">
                  <div className="flex items-center space-x-3">
                    <DollarSign className="h-5 w-5 text-yellow-500" />
                    <div>
                      <h3 className="font-medium text-yellow-900">Cost Threshold Exceeded</h3>
                      <p className="text-sm text-yellow-700">
                        Monthly cost has exceeded the budget threshold
                      </p>
                    </div>
                    <Badge variant="secondary">Warning</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
