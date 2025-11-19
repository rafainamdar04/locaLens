import React, { useState, useEffect } from 'react'
import { api } from '../../api/client'
import { useAuth } from '../../contexts/AuthContext'

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'critical'
  timestamp: number
  uptime_seconds: number
  config: {
    embed_model: string
    port: number
    here_api_configured: boolean
    llm_api_configured: boolean
    cache_enabled: boolean
    cache_size: number
  }
  services: {
    embedder_loaded: boolean
    here_api_reachable: boolean
    llm_api_reachable: boolean
    embedder_error?: string
    here_api_error?: string
    llm_api_error?: string
  }
  performance: {
    total_requests_processed: number
    average_processing_time_ms: number
  }
}

interface MonitoringData {
  metrics: {
    total_requests: number
    avg_latency: number
    avg_fused_confidence: number
    avg_integrity_score: number
    anomaly_rate: number
    high_latency_rate: number
    low_confidence_rate: number
    timestamp: string
  }
  prediction: {
    prediction: string
    confidence: number
  }
  insights: string
  alerts: Array<{
    type: string
    severity: string
    message: string
    timestamp: string
  }>
}

interface SelfHealData {
  agent_analysis: string
  timestamp: number
  metrics_summary: any
  prediction_summary: any
}

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [healthData, setHealthData] = useState<HealthStatus | null>(null)
  const [monitoringData, setMonitoringData] = useState<MonitoringData | null>(null)
  const [selfHealData, setSelfHealData] = useState<SelfHealData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, metricsRes, selfHealRes] = await Promise.all([
          api.get('/health'),
          api.get('/monitoring/metrics'),
          api.post('/monitoring/agent-check')
        ])
        setHealthData(healthRes.data)
        setMonitoringData(metricsRes.data)
        setSelfHealData(selfHealRes.data)
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#FAF7F0]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#4A7C59] mx-auto mb-4"></div>
          <p className="text-[#6B6B6B]">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#FAF7F0] p-6">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-[#E8E0D1] mb-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-[#2C2C2C]">Admin Monitoring Dashboard</h1>
              <span className="text-sm text-[#6B6B6B] bg-[#F5F2EB] px-3 py-1 rounded-full">
                Welcome, {user?.username}
              </span>
            </div>
            <button
              onClick={logout}
              className="flex items-center space-x-2 text-[#6B6B6B] hover:text-[#2C2C2C] transition-colors"
            >
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* Service Health */}
        <section className="bg-white rounded-lg shadow-sm border border-[#E8E0D1] p-6">
          <h2 className="text-xl font-semibold text-[#2C2C2C] mb-4">Service Health</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-[#6B6B6B]">Status</p>
              <p className={`text-lg font-bold ${healthData?.status === 'healthy' ? 'text-green-600' : healthData?.status === 'degraded' ? 'text-yellow-600' : 'text-red-600'}`}>
                {healthData?.status}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-[#6B6B6B]">Uptime</p>
              <p className="text-lg font-bold text-[#2C2C2C]">{Math.floor((healthData?.uptime_seconds || 0) / 3600)}h</p>
            </div>
            <div>
              <p className="text-sm font-medium text-[#6B6B6B]">Total Requests</p>
              <p className="text-lg font-bold text-[#2C2C2C]">{healthData?.performance.total_requests_processed}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-[#6B6B6B]">Avg Latency</p>
              <p className="text-lg font-bold text-[#2C2C2C]">{healthData?.performance.average_processing_time_ms}ms</p>
            </div>
            <div>
              <p className="text-sm font-medium text-[#6B6B6B]">Embedder Loaded</p>
              <p className={`text-lg font-bold ${healthData?.services.embedder_loaded ? 'text-green-600' : 'text-red-600'}`}>
                {healthData?.services.embedder_loaded ? 'Yes' : 'No'}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-[#6B6B6B]">HERE API</p>
              <p className={`text-lg font-bold ${healthData?.services.here_api_reachable ? 'text-green-600' : 'text-red-600'}`}>
                {healthData?.services.here_api_reachable ? 'Reachable' : 'Unreachable'}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-[#6B6B6B]">LLM API</p>
              <p className={`text-lg font-bold ${healthData?.services.llm_api_reachable ? 'text-green-600' : 'text-red-600'}`}>
                {healthData?.services.llm_api_reachable ? 'Reachable' : 'Unreachable'}
              </p>
            </div>
          </div>
          {healthData?.services.embedder_error && (
            <div className="mt-4">
              <p className="text-sm font-medium text-[#6B6B6B]">Embedder Error</p>
              <p className="text-sm text-red-600">{healthData.services.embedder_error}</p>
            </div>
          )}
          {healthData?.services.here_api_error && (
            <div className="mt-4">
              <p className="text-sm font-medium text-[#6B6B6B]">HERE API Error</p>
              <p className="text-sm text-red-600">{healthData.services.here_api_error}</p>
            </div>
          )}
          {healthData?.services.llm_api_error && (
            <div className="mt-4">
              <p className="text-sm font-medium text-[#6B6B6B]">LLM API Error</p>
              <p className="text-sm text-red-600">{healthData.services.llm_api_error}</p>
            </div>
          )}
        </section>

        {/* System Metrics */}
        <section className="bg-white rounded-lg shadow-sm border border-[#E8E0D1] p-6">
          <h2 className="text-xl font-semibold text-[#2C2C2C] mb-4">System Metrics</h2>
          <table className="w-full table-auto">
            <thead>
              <tr className="border-b border-[#E8E0D1]">
                <th className="text-left py-2 px-4 font-medium text-[#6B6B6B]">Metric</th>
                <th className="text-left py-2 px-4 font-medium text-[#6B6B6B]">Value</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-[#E8E0D1]">
                <td className="py-2 px-4">Total Requests</td>
                <td className="py-2 px-4">{monitoringData?.metrics.total_requests}</td>
              </tr>
              <tr className="border-b border-[#E8E0D1]">
                <td className="py-2 px-4">Avg Latency (ms)</td>
                <td className="py-2 px-4">{monitoringData?.metrics.avg_latency.toFixed(2)}</td>
              </tr>
              <tr className="border-b border-[#E8E0D1]">
                <td className="py-2 px-4">Avg Confidence</td>
                <td className="py-2 px-4">{monitoringData?.metrics.avg_fused_confidence.toFixed(3)}</td>
              </tr>
              <tr className="border-b border-[#E8E0D1]">
                <td className="py-2 px-4">Avg Integrity Score</td>
                <td className="py-2 px-4">{monitoringData?.metrics.avg_integrity_score.toFixed(2)}</td>
              </tr>
              <tr className="border-b border-[#E8E0D1]">
                <td className="py-2 px-4">Anomaly Rate</td>
                <td className="py-2 px-4">{monitoringData?.metrics.anomaly_rate}</td>
              </tr>
              <tr className="border-b border-[#E8E0D1]">
                <td className="py-2 px-4">High Latency Rate</td>
                <td className="py-2 px-4">{((monitoringData?.metrics.high_latency_rate || 0) * 100).toFixed(1)}%</td>
              </tr>
              <tr>
                <td className="py-2 px-4">Low Confidence Rate</td>
                <td className="py-2 px-4">{((monitoringData?.metrics.low_confidence_rate || 0) * 100).toFixed(1)}%</td>
              </tr>
            </tbody>
          </table>
        </section>

        {/* Alerts */}
        <section className="bg-white rounded-lg shadow-sm border border-[#E8E0D1] p-6">
          <h2 className="text-xl font-semibold text-[#2C2C2C] mb-4">Alerts</h2>
          {monitoringData?.alerts.length ? (
            <ul className="space-y-2">
              {monitoringData.alerts.map((alert, index) => (
                <li key={index} className={`p-4 rounded border ${alert.severity === 'warning' ? 'border-yellow-300 bg-yellow-50' : 'border-red-300 bg-red-50'}`}>
                  <p className="font-medium">{alert.type}: {alert.message}</p>
                  <p className="text-sm text-[#6B6B6B]">{new Date(alert.timestamp).toLocaleString()}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-[#6B6B6B]">No alerts</p>
          )}
        </section>

        {/* Insights */}
        <section className="bg-white rounded-lg shadow-sm border border-[#E8E0D1] p-6">
          <h2 className="text-xl font-semibold text-[#2C2C2C] mb-4">Insights</h2>
          <p className="text-[#6B6B6B]">{monitoringData?.insights || 'No insights available'}</p>
          {selfHealData?.agent_analysis && (
            <div className="mt-4">
              <p className="text-sm font-medium text-[#6B6B6B]">Agent Analysis</p>
              <p className="text-[#6B6B6B]">{selfHealData.agent_analysis}</p>
            </div>
          )}
        </section>

        {/* Downloads */}
        <section className="bg-white rounded-lg shadow-sm border border-[#E8E0D1] p-6">
          <h2 className="text-xl font-semibold text-[#2C2C2C] mb-4">Downloads</h2>
          <div className="space-x-4">
            <button onClick={() => {
              const dataStr = JSON.stringify({ healthData, monitoringData, selfHealData }, null, 2);
              const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
              const linkElement = document.createElement('a');
              linkElement.setAttribute('href', dataUri);
              linkElement.setAttribute('download', 'metrics.json');
              linkElement.click();
            }} className="bg-[#4A7C59] text-white py-2 px-4 rounded hover:bg-[#3a5f47] transition-colors">
              Download Metrics JSON
            </button>
            <button onClick={() => {
              const csvContent = "data:text/csv;charset=utf-8,Date,Level,Message\n2025-11-19,INFO,Service started\n";
              const encodedUri = encodeURI(csvContent);
              const link = document.createElement("a");
              link.setAttribute("href", encodedUri);
              link.setAttribute("download", "logs.csv");
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }} className="bg-[#4A7C59] text-white py-2 px-4 rounded hover:bg-[#3a5f47] transition-colors">
              Download Logs CSV
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}