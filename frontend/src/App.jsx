import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { Network, Server, Cpu, Activity, Clock } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function App() {
  const [metrics, setMetrics] = useState({
    network_load: 0,
    cloud_load: 0,
    edge_load: 0,
    slice_utilization: { eMBB: 0, URLLC: 0, mMTC: 0 },
    recent_decisions: []
  });

  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await axios.get(`${API_BASE}/metrics`);
        setMetrics(res.data);

        // Add to history for chart
        setHistory(prev => {
          const newHistory = [...prev, {
            time: new Date().toLocaleTimeString(),
            'Network Load': res.data.network_load,
            'Edge Load': res.data.edge_load,
            'Cloud Load': res.data.cloud_load
          }];
          if (newHistory.length > 20) return newHistory.slice(1);
          return newHistory;
        });
      } catch (err) {
        console.error("Error fetching metrics", err);
      }
    };

    const interval = setInterval(fetchMetrics, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>5G AI Orchestrator</h1>
        <div className="live-indicator">
          <div className="pulse"></div>
          LIVE
        </div>
      </header>

      {/* Top KPIs */}
      <div className="kpi-row">
        <div className="card">
          <div className="card-title">
            <Activity size={20} color="var(--accent-cyan)" /> Total Network Load
          </div>
          <div className="kpi-value">{metrics.network_load.toFixed(1)}%</div>
        </div>
        <div className="card">
          <div className="card-title">
            <Server size={20} color="var(--accent-purple)" /> Edge Compute Load
          </div>
          <div className="kpi-value">{metrics.edge_load.toFixed(1)}%</div>
        </div>
        <div className="card">
          <div className="card-title">
            <Cpu size={20} color="var(--accent-pink)" /> Cloud Compute Load
          </div>
          <div className="kpi-value">{metrics.cloud_load.toFixed(1)}%</div>
        </div>
      </div>

      <div className="grid-layout">
        {/* Main Chart */}
        <div className="card chart-section">
          <div className="card-title">
            <Network size={20} /> Real-time Resource Orchestration
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={history}>
              <defs>
                <linearGradient id="colorNetwork" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--accent-cyan)" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="var(--accent-cyan)" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorEdge" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--accent-purple)" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="var(--accent-purple)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="var(--text-muted)" />
              <YAxis stroke="var(--text-muted)" />
              <CartesianGrid strokeDasharray="3 3" stroke="var(--glass-border)" />
              <Tooltip
                contentStyle={{ backgroundColor: 'var(--glass-bg)', borderColor: 'var(--glass-border)' }}
                itemStyle={{ color: 'var(--text-main)' }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Area type="monotone" dataKey="Network Load" stroke="var(--accent-cyan)" fillOpacity={1} fill="url(#colorNetwork)" />
              <Area type="monotone" dataKey="Edge Load" stroke="var(--accent-purple)" fillOpacity={1} fill="url(#colorEdge)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Slice Utilization */}
        <div className="card slice-section">
          <div className="card-title">
            <Network size={20} /> 5G Slice Utilization
          </div>

          <div className="slice-stat">
            <div className="slice-header">
              <span style={{ color: 'var(--eMBB-color)' }}>eMBB (Video/AR)</span>
              <span>{metrics.slice_utilization.eMBB.toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${metrics.slice_utilization.eMBB}%`, backgroundColor: 'var(--eMBB-color)' }}
              ></div>
            </div>
          </div>

          <div className="slice-stat">
            <div className="slice-header">
              <span style={{ color: 'var(--URLLC-color)' }}>URLLC (Emergency/Auto)</span>
              <span>{metrics.slice_utilization.URLLC.toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${metrics.slice_utilization.URLLC}%`, backgroundColor: 'var(--URLLC-color)' }}
              ></div>
            </div>
          </div>

          <div className="slice-stat">
            <div className="slice-header">
              <span style={{ color: 'var(--mMTC-color)' }}>mMTC (IoT Sensors)</span>
              <span>{metrics.slice_utilization.mMTC.toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${metrics.slice_utilization.mMTC}%`, backgroundColor: 'var(--mMTC-color)' }}
              ></div>
            </div>
          </div>
        </div>

        {/* Recent AI Decisions */}
        <div className="card decisions-table-container">
          <div className="card-title">
            <Clock size={20} /> AI Decision Log
          </div>
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Device ID</th>
                <th>User Type</th>
                <th>Task Need</th>
                <th>Target Slice</th>
                <th>Offload AI Decision</th>
                <th>Resource %</th>
              </tr>
            </thead>
            <tbody>
              {metrics.recent_decisions.map((dec, i) => (
                <tr key={i}>
                  <td style={{ color: 'var(--text-muted)' }}>
                    {new Date(dec.timestamp).toLocaleTimeString()}
                  </td>
                  <td style={{ fontFamily: 'monospace' }}>{dec.user_id}</td>
                  <td>{dec.user_type_str}</td>
                  <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Bw: {dec.bandwidth_need.toFixed(1)}, Lat: {dec.latency_tolerance.toFixed(0)}ms
                  </td>
                  <td>
                    <span className={`badge badge-slice-${dec.slice_type}`}>
                      {dec.slice_type}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-offload-${dec.offloading_decision}`}>
                      {dec.offloading_decision}
                    </span>
                  </td>
                  <td>{dec.resource_allocation.toFixed(1)}%</td>
                </tr>
              ))}
              {metrics.recent_decisions.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    Waiting for traffic...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default App;
