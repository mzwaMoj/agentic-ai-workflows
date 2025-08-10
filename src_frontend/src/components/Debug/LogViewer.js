import React, { useState, useEffect } from 'react';
import logger from '../../services/logger';

const LogViewer = ({ isVisible, onClose }) => {
  const [logs, setLogs] = useState([]);
  const [filter, setFilter] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    if (!isVisible) return;

    const refreshLogs = () => {
      setLogs([...logger.getAllLogs()]);
    };

    refreshLogs();

    if (autoRefresh) {
      const interval = setInterval(refreshLogs, 1000);
      return () => clearInterval(interval);
    }
  }, [isVisible, autoRefresh]);

  const filteredLogs = logs.filter(log => 
    filter === 'all' || log.level === filter
  );

  const getLevelColor = (level) => {
    switch (level) {
      case 'error': return '#ff4444';
      case 'warn': return '#ffaa00';
      case 'info': return '#4444ff';
      case 'success': return '#44ff44';
      case 'debug': return '#666666';
      default: return '#000000';
    }
  };

  if (!isVisible) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.8)',
      zIndex: 10000,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        height: '100%',
        borderRadius: '8px',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px',
          borderBottom: '1px solid #eee',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h3>Frontend Logs ({filteredLogs.length})</h3>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <select 
              value={filter} 
              onChange={(e) => setFilter(e.target.value)}
              style={{ padding: '4px 8px' }}
            >
              <option value="all">All Levels</option>
              <option value="error">Errors</option>
              <option value="warn">Warnings</option>
              <option value="info">Info</option>
              <option value="success">Success</option>
              <option value="debug">Debug</option>
            </select>
            <label style={{ fontSize: '14px' }}>
              <input 
                type="checkbox" 
                checked={autoRefresh} 
                onChange={(e) => setAutoRefresh(e.target.checked)}
                style={{ marginRight: '4px' }}
              />
              Auto-refresh
            </label>
            <button 
              onClick={() => logger.downloadLogs()}
              style={{ padding: '4px 8px', marginRight: '8px' }}
            >
              Download
            </button>
            <button 
              onClick={() => logger.clearLogs()}
              style={{ padding: '4px 8px', marginRight: '8px' }}
            >
              Clear
            </button>
            <button onClick={onClose} style={{ padding: '4px 8px' }}>✕</button>
          </div>
        </div>

        {/* Logs */}
        <div style={{
          flex: 1,
          overflow: 'auto',
          padding: '8px',
          fontFamily: 'monospace',
          fontSize: '12px'
        }}>
          {filteredLogs.map((log, index) => (
            <div key={index} style={{
              marginBottom: '4px',
              padding: '4px',
              borderLeft: `3px solid ${getLevelColor(log.level)}`,
              backgroundColor: index % 2 === 0 ? '#f9f9f9' : 'white'
            }}>
              <div style={{ fontWeight: 'bold', color: getLevelColor(log.level) }}>
                [{log.level.toUpperCase()}] {log.timestamp} - {log.message}
              </div>
              {log.data && (
                <div style={{ marginTop: '4px', color: '#666', fontSize: '11px' }}>
                  {JSON.stringify(log.data, null, 2)}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LogViewer;
