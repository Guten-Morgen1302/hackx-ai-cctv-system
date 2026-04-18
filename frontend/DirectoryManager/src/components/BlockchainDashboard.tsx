import React, { useState, useEffect } from 'react';
import './BlockchainDashboard.css';

interface VideoInfo {
  name: string;
  exists: boolean;
  size_mb: number;
  active: boolean;
}

interface BlockData {
  index: number;
  timestamp: string;
  event_data: {
    camera_id: string;
    event_type: string;
    person_id: string;
    zone: string;
    severity: string;
    image_hash: string;
  };
  hash: string;
  verified?: boolean;
}

interface RiskScore {
  person_id: string;
  score: number;
  risk_tier: string;
  trend: string;
}

interface IdentityData {
  person_id: string;
  name: string;
  role: string;
  department: string;
  access_zones: string[];
  enrollment_timestamp: string;
}

export const BlockchainDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'evidence' | 'identity' | 'risk' | 'videos'>('videos');
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [currentVideo, setCurrentVideo] = useState<string>('test5.mp4');
  const [videoAnalytics, setVideoAnalytics] = useState<any>(null);
  const [evidenceChain, setEvidenceChain] = useState<BlockData[]>([]);
  const [identities, setIdentities] = useState<IdentityData[]>([]);
  const [riskScores, setRiskScores] = useState<Record<string, RiskScore>>({});
  const [chainHealth, setChainHealth] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedPerson, setSelectedPerson] = useState<string | null>(null);

  // Load available videos
  useEffect(() => {
    fetchAvailableVideos();
    fetchVideoAnalytics(currentVideo);
  }, []);

  const fetchAvailableVideos = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/videos/available');
      const data = await response.json();
      if (data.success) {
        setVideos(data.available_videos);
        setCurrentVideo(data.current_video);
      }
    } catch (error) {
      console.error('Error fetching videos:', error);
    }
  };

  const switchVideo = async (videoName: string) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5001/api/videos/switch/${videoName}`, {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        setCurrentVideo(videoName);
        // Reload all data for new video
        setTimeout(() => {
          fetchVideoAnalytics(videoName);
          fetchEvidenceChain();
          fetchIdentities();
          fetchRiskScores();
        }, 500);
      }
    } catch (error) {
      console.error('Error switching video:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchVideoAnalytics = async (videoName: string) => {
    try {
      const response = await fetch(`http://localhost:5001/api/videos/analytics/${videoName}`);
      const data = await response.json();
      if (data.success) {
        setVideoAnalytics(data.analytics);
      }
    } catch (error) {
      console.error('Error fetching video analytics:', error);
    }
  };

  const fetchEvidenceChain = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/chain');
      const data = await response.json();
      if (data.success) {
        setEvidenceChain(data.chain);
      }
    } catch (error) {
      console.error('Error fetching evidence chain:', error);
    }
  };

  const fetchIdentities = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/identity');
      const data = await response.json();
      if (data.success) {
        setIdentities(data.identities);
      }
    } catch (error) {
      console.error('Error fetching identities:', error);
    }
  };

  const fetchRiskScores = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/risk/scores');
      const data = await response.json();
      if (data.success) {
        setRiskScores(data.scores);
      }
    } catch (error) {
      console.error('Error fetching risk scores:', error);
    }
  };

  const fetchChainHealth = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/chain/verify');
      const data = await response.json();
      if (data.success) {
        setChainHealth(data.chain_health);
      }
    } catch (error) {
      console.error('Error fetching chain health:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'evidence') {
      fetchEvidenceChain();
      fetchChainHealth();
    } else if (activeTab === 'identity') {
      fetchIdentities();
    } else if (activeTab === 'risk') {
      fetchRiskScores();
    }
  }, [activeTab]);

  const getRiskColor = (score: number): string => {
    if (score <= 30) return '#10b981'; // Green
    if (score <= 55) return '#f59e0b'; // Yellow
    if (score <= 75) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const getRiskTier = (score: number): string => {
    if (score <= 30) return '🟢 LOW';
    if (score <= 55) return '🟡 MEDIUM';
    if (score <= 75) return '🟠 HIGH';
    return '🔴 CRITICAL';
  };

  const getHighRiskPersons = () => {
    return Object.values(riskScores)
      .filter((r) => r.score > 55)
      .sort((a, b) => b.score - a.score);
  };

  return (
    <div className="blockchain-dashboard">
      <div className="dashboard-header">
        <h1>🔐 SecureVista Blockchain & Risk System</h1>
        <div className="current-status">
          <span className="status-badge">📹 Video: {currentVideo}</span>
          <span className="status-badge">⛓️ Blocks: {evidenceChain.length}</span>
          <span className="status-badge">👥 Tracked: {Object.keys(riskScores).length}</span>
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'videos' ? 'active' : ''}`}
          onClick={() => setActiveTab('videos')}
        >
          📹 Video Filter
        </button>
        <button
          className={`tab ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          📋 Evidence Chain
        </button>
        <button
          className={`tab ${activeTab === 'identity' ? 'active' : ''}`}
          onClick={() => setActiveTab('identity')}
        >
          👤 Identity Registry
        </button>
        <button
          className={`tab ${activeTab === 'risk' ? 'active' : ''}`}
          onClick={() => setActiveTab('risk')}
        >
          ⚠️ Risk Scores
        </button>
      </div>

      <div className="tab-content">
        {/* VIDEO FILTER TAB */}
        {activeTab === 'videos' && (
          <div className="video-filter-section">
            <h2>📹 Video Selection</h2>
            <p>Select a test video to load. Videos process 1 by 1.</p>
            
            <div className="video-grid">
              {videos.map((video) => (
                <div
                  key={video.name}
                  className={`video-card ${video.active ? 'active' : ''} ${!video.exists ? 'missing' : ''}`}
                  onClick={() => video.exists && switchVideo(video.name)}
                >
                  <div className="video-icon">📹</div>
                  <div className="video-name">{video.name}</div>
                  <div className="video-size">
                    {video.exists ? `${video.size_mb} MB` : 'Not Found'}
                  </div>
                  {video.active && <div className="active-badge">✓ ACTIVE</div>}
                  {!video.exists && <div className="missing-badge">✗ Missing</div>}
                </div>
              ))}
            </div>

            {/* VIDEO ANALYTICS DISPLAY */}
            {videoAnalytics && (
              <div className="video-analytics-panel">
                <h3>📊 {videoAnalytics.name} - {videoAnalytics.description}</h3>
                
                <div className="analytics-grid">
                  <div className="analytics-card">
                    <div className="analytics-label">People Detected</div>
                    <div className="analytics-value">{videoAnalytics.people_detected}</div>
                    <div className="analytics-subtext">{videoAnalytics.crowd_detected}</div>
                  </div>

                  <div className="analytics-card">
                    <div className="analytics-label">Location</div>
                    <div className="analytics-value" style={{ fontSize: '0.9rem' }}>
                      {videoAnalytics.location}
                    </div>
                    <div className="analytics-subtext">Zone Info</div>
                  </div>

                  <div className="analytics-card">
                    <div className="analytics-label">Entry/Exit</div>
                    <div className="analytics-value">
                      {videoAnalytics.entry}/{videoAnalytics.exit}
                    </div>
                    <div className="analytics-subtext">In/Out Count</div>
                  </div>

                  <div className="analytics-card">
                    <div className="analytics-label">Status</div>
                    <div className="analytics-value" style={{ fontSize: '0.85rem' }}>
                      {videoAnalytics.status}
                    </div>
                    <div className="analytics-subtext">Activity</div>
                  </div>
                </div>

                {videoAnalytics.alerts && videoAnalytics.alerts.length > 0 && (
                  <div className="alerts-panel">
                    <h4>🚨 Active Alerts</h4>
                    {videoAnalytics.alerts.map((alert: any, idx: number) => (
                      <div key={idx} className="alert-item">
                        <span className="alert-type">{alert.type.toUpperCase()}</span>
                        <span className="alert-severity" style={{ 
                          color: alert.severity === 'CRITICAL' ? '#ef4444' : alert.severity === 'HIGH' ? '#f97316' : '#f59e0b'
                        }}>
                          {alert.severity}
                        </span>
                        <span className="alert-detail">{alert.count || alert.person_id || alert.trigger_time}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            <div className="video-info">
              <h3>ℹ️ How It Works</h3>
              <ul>
                <li>✅ Select any video from the list above</li>
                <li>✅ System loads and processes it in real-time</li>
                <li>✅ Detections appear 1 by 1 on the feed</li>
                <li>✅ Loitering detection triggers after 23 seconds on test5.mp4</li>
                <li>✅ Other videos work normally without loitering overlay</li>
              </ul>
            </div>
          </div>
        )}

        {/* EVIDENCE CHAIN TAB */}
        {activeTab === 'evidence' && (
          <div className="evidence-section">
            <h2>📋 Evidence Chain</h2>

            {chainHealth && (
              <div className="chain-health">
                <div className={`health-badge ${chainHealth.is_valid ? 'valid' : 'compromised'}`}>
                  {chainHealth.is_valid ? '✅ VERIFIED' : '❌ COMPROMISED'}
                </div>
                <div className="health-stats">
                  <span>Total Blocks: {chainHealth.total_blocks}</span>
                  <span>Integrity: {chainHealth.integrity}</span>
                </div>
              </div>
            )}

            <div className="evidence-list">
              {evidenceChain.length === 0 ? (
                <p className="empty-state">No events recorded yet</p>
              ) : (
                evidenceChain.map((block) => (
                  <div key={block.index} className="evidence-block">
                    <div className="block-header">
                      <span className="block-index">Block #{block.index}</span>
                      <span className="block-hash">{block.hash.substring(0, 16)}...</span>
                      <span className="block-verified">✅</span>
                    </div>
                    <div className="block-details">
                      <p>
                        <strong>Event:</strong> {block.event_data.event_type}
                      </p>
                      <p>
                        <strong>Person:</strong> ID: {block.event_data.person_id}
                      </p>
                      <p>
                        <strong>Zone:</strong> {block.event_data.zone}
                      </p>
                      <p>
                        <strong>Severity:</strong>{' '}
                        <span
                          className={`severity ${block.event_data.severity.toLowerCase()}`}
                        >
                          {block.event_data.severity}
                        </span>
                      </p>
                      <p>
                        <strong>Time:</strong> {new Date(block.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* IDENTITY REGISTRY TAB */}
        {activeTab === 'identity' && (
          <div className="identity-section">
            <h2>👤 Identity Registry</h2>

            <div className="identity-list">
              {identities.length === 0 ? (
                <p className="empty-state">No enrolled persons</p>
              ) : (
                identities.map((identity) => (
                  <div key={identity.person_id} className="identity-card">
                    <div className="identity-header">
                      <span className="person-id">ID: {identity.person_id}</span>
                      <span className="person-name">{identity.name}</span>
                    </div>
                    <div className="identity-details">
                      <p>
                        <strong>Role:</strong> {identity.role}
                      </p>
                      <p>
                        <strong>Department:</strong> {identity.department}
                      </p>
                      <p>
                        <strong>Access Zones:</strong> {identity.access_zones.join(', ')}
                      </p>
                      <p>
                        <strong>Enrolled:</strong>{' '}
                        {new Date(identity.enrollment_timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* RISK SCORES TAB */}
        {activeTab === 'risk' && (
          <div className="risk-section">
            <h2>⚠️ Risk Scoring System</h2>

            <div className="risk-summary">
              <div className="risk-stat">
                <span className="stat-label">Total Tracked</span>
                <span className="stat-value">{Object.keys(riskScores).length}</span>
              </div>
              <div className="risk-stat">
                <span className="stat-label">High Risk</span>
                <span className="stat-value critical">{getHighRiskPersons().length}</span>
              </div>
            </div>

            {getHighRiskPersons().length > 0 && (
              <div className="high-risk-panel">
                <h3>🔴 High Risk Persons (Score {'>'}  55)</h3>
                <div className="risk-boxes">
                  {getHighRiskPersons().map((person) => (
                    <div
                      key={person.person_id}
                      className="risk-box"
                      style={{ borderLeftColor: getRiskColor(person.score) }}
                      onClick={() => setSelectedPerson(person.person_id)}
                    >
                      <div className="risk-score" style={{ color: getRiskColor(person.score) }}>
                        {person.score.toFixed(1)}/100
                      </div>
                      <div className="risk-tier">{getRiskTier(person.score)}</div>
                      <div className="person-id">Person {person.person_id}</div>
                      <div className="risk-trend">{person.trend}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(riskScores).length === 0 && (
              <p className="empty-state">No risk data available</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BlockchainDashboard;
