import React, { useState, useEffect } from 'react';
import { MetricsSummary } from '@/types';
import Button from '@/components/ui/Button';
import RestaurantAPI from '@/lib/api';

const StatusPage: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [safetyStatus, setSafetyStatus] = useState<any>(null);
  const [testResults, setTestResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hours, setHours] = useState(24);

  useEffect(() => {
    loadSystemStatus();
  }, [hours]);

  const loadSystemStatus = async () => {
    setLoading(true);
    setError('');
    try {
      const [metricsData, safetyData] = await Promise.all([
        RestaurantAPI.getMetrics(hours),
        RestaurantAPI.getSafetyStatus()
      ]);
      setMetrics(metricsData);
      setSafetyStatus(safetyData);
    } catch (err: any) {
      setError(err.message || 'Failed to load system status');
    } finally {
      setLoading(false);
    }
  };

  const runTests = async () => {
    setLoading(true);
    try {
      const results = await RestaurantAPI.runTests();
      setTestResults(results);
    } catch (err: any) {
      setError(err.message || 'Failed to run tests');
    } finally {
      setLoading(false);
    }
  };

  const createSnapshots = async () => {
    setLoading(true);
    try {
      await RestaurantAPI.createSnapshots();
      alert('Test snapshots created successfully!');
    } catch (err: any) {
      setError(err.message || 'Failed to create snapshots');
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'operational': return 'text-success-600';
      case 'degraded': return 'text-warning-600';
      case 'down': return 'text-error-600';
      default: return 'text-gray-600';
    }
  };

  const getPhaseHealth = () => {
    const phases = [
      { name: 'Foundation (0)', status: 'operational' },
      { name: 'Data (1)', status: 'operational' },
      { name: 'Preferences (2)', status: 'operational' },
      { name: 'Integration (3)', status: 'operational' },
      { name: 'LLM (4)', status: 'operational' },
      { name: 'Display (5)', status: 'operational' },
      { name: 'Hardening (6)', status: 'operational' },
    ];
    return phases;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-primary-600 text-white py-8">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold mb-2">System Status</h1>
          <p className="text-primary-100">
            Real-time monitoring and system health dashboard
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Error */}
        {error && (
          <div className="bg-error-50 border border-error-200 rounded-lg p-4 mb-6">
            <h3 className="text-error-800 font-medium mb-2">Error</h3>
            <p className="text-error-600">{error}</p>
          </div>
        )}

        {/* System Health Overview */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold mb-6">System Health</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {getPhaseHealth().map((phase, index) => (
              <div key={index} className="text-center">
                <div className={`text-2xl font-bold mb-2 ${getHealthColor(phase.status)}`}>
                  {phase.status === 'operational' ? '✅' : phase.status === 'degraded' ? '⚠️' : '❌'}
                </div>
                <div className="text-sm text-gray-600">{phase.name}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Metrics Section */}
        {metrics && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Performance Metrics</h2>
              <select
                value={hours}
                onChange={(e) => setHours(parseInt(e.target.value))}
                className="border rounded px-3 py-1 text-sm"
              >
                <option value={1}>Last 1 hour</option>
                <option value={6}>Last 6 hours</option>
                <option value={24}>Last 24 hours</option>
                <option value={168}>Last 7 days</option>
              </select>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-600 mb-2">
                  {metrics.total_requests}
                </div>
                <div className="text-sm text-gray-600">Total Requests</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-success-600 mb-2">
                  {metrics.successful_requests}
                </div>
                <div className="text-sm text-gray-600">Successful</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-error-600 mb-2">
                  {metrics.failed_requests}
                </div>
                <div className="text-sm text-gray-600">Failed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-warning-600 mb-2">
                  {metrics.avg_processing_time_ms?.toFixed(2)}ms
                </div>
                <div className="text-sm text-gray-600">Avg Response Time</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-3">Top Endpoints</h3>
                <div className="space-y-2">
                  {metrics.top_endpoints?.slice(0, 5).map((endpoint: any, index: number) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-gray-600">{endpoint.endpoint}</span>
                      <span className="font-medium">{endpoint.count}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Error Summary</h3>
                <div className="space-y-2">
                  {Object.entries(metrics.error_summary).map(([errorType, count]) => (
                    <div key={errorType} className="flex justify-between text-sm">
                      <span className="text-gray-600">{errorType}</span>
                      <span className="font-medium text-error-600">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Safety & Rate Limits */}
        {safetyStatus && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold mb-6">Safety & Rate Limits</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-3">Rate Limits</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Requests per minute</span>
                    <span className="font-medium">
                      {safetyStatus.rate_limits?.requests_last_minute || 0} / {safetyStatus.config?.rate_limits_per_minute || 60}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Requests per hour</span>
                    <span className="font-medium">
                      {safetyStatus.rate_limits?.requests_last_hour || 0} / {safetyStatus.config?.rate_limits_per_hour || 1000}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Remaining (minute)</span>
                    <span className="font-medium text-success-600">
                      {safetyStatus.rate_limits?.remaining_minute || 60}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Remaining (hour)</span>
                    <span className="font-medium text-success-600">
                      {safetyStatus.rate_limits?.remaining_hour || 1000}
                    </span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Token Limits</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Current usage</span>
                    <span className="font-medium">{safetyStatus.token_limits?.current_usage || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Limit</span>
                    <span className="font-medium">{safetyStatus.token_limits?.limit || 10000}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Remaining</span>
                    <span className="font-medium text-success-600">
                      {safetyStatus.token_limits?.remaining || 10000}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Test Results */}
        {testResults && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold mb-6">Test Results</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-3">Overall Summary</h3>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Total Tests</span>
                    <span className="font-medium">{testResults.summary?.total_tests || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Passed</span>
                    <span className="font-medium text-success-600">{testResults.summary?.total_passed || 0}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Failed</span>
                    <span className="font-medium text-error-600">{testResults.summary?.total_failed || 0}</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Phase Results</h3>
                <div className="space-y-2">
                  {Object.entries(testResults.phase_summary || {}).map(([phase, results]: [string, any]) => (
                    <div key={phase} className="flex justify-between text-sm">
                      <span className="text-gray-600">Phase {phase}</span>
                      <span className="font-medium">
                        {results.passed}/{results.total_tests}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold mb-6">System Actions</h2>
          <div className="flex flex-wrap gap-4">
            <Button onClick={runTests} loading={loading}>
              {loading ? 'Running Tests...' : 'Run All Tests'}
            </Button>
            <Button onClick={createSnapshots} loading={loading} variant="outline">
              Create Test Snapshots
            </Button>
            <Button onClick={loadSystemStatus} loading={loading} variant="outline">
              Refresh Status
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusPage;
