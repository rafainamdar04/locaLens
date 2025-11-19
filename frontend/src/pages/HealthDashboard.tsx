import React, { useState, useEffect } from 'react';
import { api } from '../api/client';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'critical';
  timestamp: number;
  uptime_seconds: number;
  system?: {
    cpu_percent: number;
    memory_percent: number;
    disk_usage: number;
  };
  config: {
    embed_model: string;
    port: number;
    here_api_configured: boolean;
    llm_api_configured: boolean;
    cache_enabled: boolean;
    cache_size: number;
  };
  services: {
    embedder_loaded: boolean;
    here_api_reachable: boolean;
    llm_api_reachable: boolean;
    embedder_error?: string;
    here_api_error?: string;
    llm_api_error?: string;
  };
  performance: {
    total_requests_processed: number;
    average_processing_time_ms: number;
  };
}

interface MonitoringData {
  metrics: {
    total_requests: number;
    avg_latency: number;
    avg_fused_confidence: number;
    avg_integrity_score: number;
    anomaly_rate: number;
    high_latency_rate: number;
    low_confidence_rate: number;
    timestamp: string;
  };
  prediction: {
    prediction: string;
    confidence: number;
    threshold: number;
  };
  insights: string;
  alerts: Array<{
    type: string;
    severity: string;
    message: string;
    timestamp: string;
  }>;
}

interface AgentAnalysis {
  agent_analysis: string;
  timestamp: number;
  metrics_summary: any;
  prediction_summary: any;
}

const HealthDashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [monitoring, setMonitoring] = useState<MonitoringData | null>(null);
  const [agentAnalysis, setAgentAnalysis] = useState<AgentAnalysis | null>(null);
  const [alerts, setAlerts] = useState<any>(null);
  const [metrics, setMetrics] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchHealth = async () => {
    try {
      const response = await api.get('/health');
      setHealth(response.data);
    } catch (err: any) {
      console.error('Health fetch error:', err);
    }
  };

  const fetchMonitoring = async () => {
    try {
      const response = await api.get('/monitoring/metrics');
      setMonitoring(response.data);
    } catch (err: any) {
      console.error('Monitoring fetch error:', err);
    }
  };

  const fetchAgentAnalysis = async () => {
    try {
      const response = await api.post('/monitoring/agent-check');
      setAgentAnalysis(response.data);
    } catch (err: any) {
      console.error('Agent analysis fetch error:', err);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await api.get('/monitoring/alerts');
      setAlerts(response.data);
    } catch (err: any) {
      console.error('Alerts fetch error:', err);
    }
  };

  const fetchPrometheusMetrics = async () => {
    try {
      const response = await api.get('/metrics');
      setMetrics(response.data);
    } catch (err: any) {
      console.error('Metrics fetch error:', err);
    }
  };

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      await Promise.all([
        fetchHealth(),
        fetchMonitoring(),
        fetchAgentAnalysis(),
        fetchAlerts(),
        fetchPrometheusMetrics()
      ]);
    } catch (err: any) {
      setError('Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    // Refresh every 60 seconds
    const interval = setInterval(fetchAllData, 60000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getServiceStatusColor = (status: boolean) => {
    return status ? 'text-green-600' : 'text-red-600';
  };

  const getAlertSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAF7F0] p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4A7C59] mx-auto"></div>
            <p className="mt-4 text-[#6B6B6B]">Loading admin dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#FAF7F0] p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-red-800 font-semibold mb-2">Dashboard Error</h2>
            <p className="text-red-700">{error}</p>
            <button
              onClick={fetchAllData}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAF7F0] p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#2C2C2C] mb-2">Admin Dashboard</h1>
          <p className="text-[#6B6B6B]">Advanced monitoring and AI-powered insights for LocalLens</p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <nav className="flex space-x-1 bg-white p-1 rounded-lg shadow-sm">
            {[
              { id: 'overview', label: 'System Overview' },
              { id: 'monitoring', label: 'Proactive Monitoring' },
              { id: 'predictive', label: 'Predictive AI' },
              { id: 'agentic', label: 'Agentic AI' },
              { id: 'observability', label: 'Observability' },
              { id: 'automation', label: 'Self-Healing' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-[#4A7C59] text-white'
                    : 'text-[#6B6B6B] hover:text-[#2C2C2C] hover:bg-[#F5F2EB]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && health && (
          <div className="space-y-6">
            {/* Overall Status */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-[#2C2C2C] mb-2">System Status</h2>
                  <div className="flex items-center space-x-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(health.status)}`}>
                      {health.status.toUpperCase()}
                    </span>
                    <span className="text-gray-600">
                      Last updated: {new Date(health.timestamp * 1000).toLocaleString()}
                    </span>
                  </div>
                </div>
                <button
                  onClick={fetchAllData}
                  className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Refresh All
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* System Resources */}
              {health.system && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">System Resources</h2>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>CPU Usage</span>
                        <span>{health.system.cpu_percent.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${Math.min(health.system.cpu_percent, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Memory Usage</span>
                        <span>{health.system.memory_percent.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${health.system.memory_percent > 80 ? 'bg-red-600' : 'bg-green-600'}`}
                          style={{ width: `${health.system.memory_percent}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Disk Usage</span>
                        <span>{health.system.disk_usage.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${health.system.disk_usage > 90 ? 'bg-red-600' : 'bg-yellow-600'}`}
                          style={{ width: `${health.system.disk_usage}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="pt-2 border-t">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Uptime:</span>
                        <span className="font-medium">{formatUptime(health.uptime_seconds)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Service Status */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Service Status</h2>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span>Embedder Model</span>
                    <span className={`font-medium ${getServiceStatusColor(health.services.embedder_loaded)}`}>
                      {health.services.embedder_loaded ? '✓ Loaded' : '✗ Failed'}
                    </span>
                  </div>
                  {health.services.embedder_error && (
                    <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                      {health.services.embedder_error}
                    </div>
                  )}

                  <div className="flex justify-between items-center">
                    <span>HERE Maps API</span>
                    <span className={`font-medium ${getServiceStatusColor(health.services.here_api_reachable)}`}>
                      {health.services.here_api_reachable ? '✓ Reachable' : '✗ Unreachable'}
                    </span>
                  </div>
                  {health.services.here_api_error && (
                    <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                      {health.services.here_api_error}
                    </div>
                  )}

                  <div className="flex justify-between items-center">
                    <span>LLM API</span>
                    <span className={`font-medium ${getServiceStatusColor(health.services.llm_api_reachable)}`}>
                      {health.services.llm_api_reachable ? '✓ Available' : '✗ Unavailable'}
                    </span>
                  </div>
                  {health.services.llm_api_error && (
                    <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                      {health.services.llm_api_error}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'monitoring' && monitoring && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Proactive Service Health Monitoring</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{monitoring.metrics.total_requests}</div>
                  <div className="text-sm text-blue-800">Total Requests (24h)</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{monitoring.metrics.avg_latency.toFixed(0)}ms</div>
                  <div className="text-sm text-green-800">Avg Latency</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{(monitoring.metrics.avg_fused_confidence * 100).toFixed(1)}%</div>
                  <div className="text-sm text-purple-800">Avg Confidence</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{(monitoring.metrics.anomaly_rate * 100).toFixed(1)}%</div>
                  <div className="text-sm text-orange-800">Anomaly Rate</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">AI-Generated Insights</h2>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-gray-700 whitespace-pre-line">{monitoring.insights}</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'predictive' && monitoring && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Predictive Capabilities - ML Anomaly Forecasting</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-900 mb-2">Prediction Status</h3>
                  <div className={`text-2xl font-bold mb-2 ${
                    monitoring.prediction.prediction === 'anomaly' ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {monitoring.prediction.prediction.toUpperCase()}
                  </div>
                  <p className="text-blue-800">
                    Confidence: {(monitoring.prediction.confidence * 100).toFixed(1)}%
                  </p>
                </div>

                <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-900 mb-2">Risk Metrics</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-green-800">High Latency Rate:</span>
                      <span className="font-medium">{(monitoring.metrics.high_latency_rate * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-800">Low Confidence Rate:</span>
                      <span className="font-medium">{(monitoring.metrics.low_confidence_rate * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'agentic' && agentAnalysis && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Agentic AI - Autonomous Decision-Making</h2>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg">
                <h3 className="text-lg font-semibold text-purple-900 mb-4">AI Agent Analysis</h3>
                <div className="bg-white p-4 rounded-lg shadow-sm">
                  <p className="text-gray-700 whitespace-pre-line">{agentAnalysis.agent_analysis}</p>
                </div>
                <div className="mt-4 text-sm text-purple-700">
                  Last analysis: {new Date(agentAnalysis.timestamp * 1000).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'observability' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Advanced Observability - Prometheus Metrics Export</h2>
              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto">
                <pre>{metrics || 'Loading metrics...'}</pre>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'automation' && alerts && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Data-Driven Automation - Self-Healing & Predictive Alerts</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-medium">Active Alerts: {alerts.total_alerts}</span>
                  <button
                    onClick={fetchAlerts}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Refresh Alerts
                  </button>
                </div>

                <div className="space-y-3">
                  {alerts.alerts.map((alert: any, index: number) => (
                    <div key={index} className={`p-4 rounded-lg border ${getAlertSeverityColor(alert.severity)}`}>
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium capitalize">{alert.type.replace('_', ' ')}</div>
                          <div className="text-sm mt-1">{alert.message}</div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(alert.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HealthDashboard;