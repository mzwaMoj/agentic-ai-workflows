import React, { useState, useEffect } from 'react';
import logger from '../../services/logger';
import './LogViewer.css';

const LogViewer = ({ isOpen, onClose }) => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadLogs();
      const interval = setInterval(loadLogs, 1000); // Refresh every second
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  useEffect(() => {
    applyFilters();
  }, [logs, filter, searchTerm]);

  const loadLogs = () => {
    const allLogs = logger.getAllLogs();
    setLogs(allLogs);
  };

  const applyFilters = () => {
    let filtered = logs;

    // Apply level filter
    if (filter !== 'all') {
      filtered = filtered.filter(log => log.level === filter);
    }

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (log.data && JSON.stringify(log.data).toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    setFilteredLogs(filtered);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getLevelColor = (level) => {
    const colors = {
      error: '#ff4444',
      warn: '#ffaa00',
      info: '#4444ff',
      debug: '#666666',
      success: '#44ff44'
    };
    return colors[level] || '#000000';
  };

  const clearLogs = () => {
    logger.clearLogs();
    setLogs([]);
    setFilteredLogs([]);
  };

  const downloadLogs = () => {
    logger.downloadLogs();
  };

  if (!isOpen) return null;

  return (
    <div className="log-viewer-overlay">
      <div className="log-viewer">
        <div className="log-viewer-header">
          <h3>Frontend Logs</h3>
          <div className="log-viewer-controls">
            <select 
              value={filter} 
              onChange={(e) => setFilter(e.target.value)}
              className="log-filter"
            >
              <option value="all">All Levels</option>
              <option value="error">Errors</option>
              <option value="warn">Warnings</option>
              <option value="info">Info</option>
              <option value="debug">Debug</option>
              <option value="success">Success</option>
            </select>
            
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="log-search"
            />
            
            <label className="auto-scroll-label">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
              />
              Auto-scroll
            </label>
            
            <button onClick={clearLogs} className="log-button clear">
              Clear
            </button>
            
            <button onClick={downloadLogs} className="log-button download">
              Download
            </button>
            
            <button onClick={onClose} className="log-button close">
              Close
            </button>
          </div>
        </div>
        
        <div className="log-viewer-content">
          <div className="log-viewer-stats">
            <span className="log-stat">
              Total: {logs.length}
            </span>
            <span className="log-stat">
              Filtered: {filteredLogs.length}
            </span>
            <span className="log-stat">
              Errors: {logs.filter(l => l.level === 'error').length}
            </span>
            <span className="log-stat">
              Warnings: {logs.filter(l => l.level === 'warn').length}
            </span>
          </div>
          
          <div className="log-entries" id="log-entries">
            {filteredLogs.map((log, index) => (
              <div key={index} className={`log-entry log-${log.level}`}>
                <div className="log-entry-header">
                  <span 
                    className="log-level"
                    style={{ color: getLevelColor(log.level) }}
                  >
                    [{log.level.toUpperCase()}]
                  </span>
                  <span className="log-timestamp">
                    {formatTimestamp(log.timestamp)}
                  </span>
                </div>
                <div className="log-message">
                  {log.message}
                </div>
                {log.data && (
                  <div className="log-data">
                    <pre>{JSON.stringify(log.data, null, 2)}</pre>
                  </div>
                )}
              </div>
            ))}
            
            {filteredLogs.length === 0 && (
              <div className="no-logs">
                No logs match the current filter criteria.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogViewer;
