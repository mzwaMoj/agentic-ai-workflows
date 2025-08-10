/**
 * ResultsContainer Component
 * Manages and displays SQL results, charts, and related information
 */

import React, { useState } from 'react';
import ChartViewer from '../Charts/ChartViewer';
import SQLResultTable from './SQLResultTable';
import './ResultsContainer.css';

const ResultsContainer = ({ 
  results, 
  onError,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState('chart');
  const [error, setError] = useState(null);

  // Calculate derived values (moved before hooks)
  const hasValidResults = results && results.success;
  const hasChart = hasValidResults && results.chart_html && results.chart_html.trim().length > 0;
  const hasData = hasValidResults && results.sql_results && Array.isArray(results.sql_results) && results.sql_results.length > 0;
  const hasResponse = hasValidResults && results.response && results.response.trim().length > 0;

  // Determine default active tab - moved before early return
  React.useEffect(() => {
    if (hasChart && activeTab !== 'chart') {
      setActiveTab('chart');
    } else if (!hasChart && hasData) {
      setActiveTab('table');
    } else if (!hasChart && !hasData && hasResponse) {
      setActiveTab('response');
    }
  }, [hasChart, hasData, hasResponse, activeTab]);

  // Handle errors from child components
  const handleError = (err) => {
    setError(err);
    if (onError) {
      onError(err);
    }
  };

  // Reset error state
  const clearError = () => {
    setError(null);
  };

  // Validate results structure - early return after all hooks
  if (!hasValidResults) {
    return (
      <div className={`results-container error ${className}`}>
        <div className="error-state">
          <h4>No Results Available</h4>
          <p>
            {results?.error || 'No data returned from the query.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`results-container ${className}`}>
      {error && (
        <div className="error-banner">
          <span className="error-message">⚠️ {error.message || error}</span>
          <button onClick={clearError} className="error-close">✕</button>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="results-tabs">
        {hasChart && (
          <button
            className={`tab-button ${activeTab === 'chart' ? 'active' : ''}`}
            onClick={() => setActiveTab('chart')}
          >
            📊 Chart
          </button>
        )}
        
        {hasData && (
          <button
            className={`tab-button ${activeTab === 'table' ? 'active' : ''}`}
            onClick={() => setActiveTab('table')}
          >
            📋 Data ({results.sql_results.length})
          </button>
        )}
        
        {hasResponse && (
          <button
            className={`tab-button ${activeTab === 'response' ? 'active' : ''}`}
            onClick={() => setActiveTab('response')}
          >
            💬 Analysis
          </button>
        )}

        {results.sql_query && (
          <button
            className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
            onClick={() => setActiveTab('query')}
          >
            🔍 SQL Query
          </button>
        )}
      </div>

      {/* Tab Content */}
      <div className="results-content">
        {/* Chart Tab */}
        {activeTab === 'chart' && hasChart && (
          <div className="tab-panel chart-panel">
            <ChartViewer
              chartHtml={results.chart_html}
              title="Data Visualization"
              onError={handleError}
            />
          </div>
        )}

        {/* Table Tab */}
        {activeTab === 'table' && hasData && (
          <div className="tab-panel table-panel">
            <SQLResultTable
              results={results.sql_results}
              sqlQuery={results.sql_query}
              executionTime={results.execution_time}
              onError={handleError}
            />
          </div>
        )}

        {/* Response/Analysis Tab */}
        {activeTab === 'response' && hasResponse && (
          <div className="tab-panel response-panel">
            <div className="response-content">
              <h3>AI Analysis</h3>
              <div className="response-text">
                {results.response.split('\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
              
              {results.execution_time && (
                <div className="response-meta">
                  <small>Generated in {results.execution_time.toFixed(2)} seconds</small>
                </div>
              )}
            </div>
          </div>
        )}

        {/* SQL Query Tab */}
        {activeTab === 'query' && results.sql_query && (
          <div className="tab-panel query-panel">
            <div className="query-content">
              <h3>Generated SQL Query</h3>
              <div className="query-container">
                <pre className="sql-code">{results.sql_query}</pre>
                <button
                  className="copy-button"
                  onClick={() => {
                    navigator.clipboard.writeText(results.sql_query)
                      .then(() => {
                        // Could add a toast notification here
                        console.log('SQL copied to clipboard');
                      })
                      .catch(err => {
                        console.error('Failed to copy SQL:', err);
                      });
                  }}
                >
                  📋 Copy SQL
                </button>
              </div>
              
              {results.execution_time && (
                <div className="query-meta">
                  <small>
                    Executed in {results.execution_time.toFixed(2)} seconds
                    {hasData && ` • ${results.sql_results.length} rows returned`}
                  </small>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Fallback for no content */}
        {!hasChart && !hasData && !hasResponse && !results.sql_query && (
          <div className="tab-panel empty-panel">
            <div className="empty-content">
              <h4>No Content Available</h4>
              <p>The query completed but returned no displayable results.</p>
            </div>
          </div>
        )}
      </div>

      {/* Results Summary Footer */}
      <div className="results-summary">
        <div className="summary-stats">
          {hasData && (
            <span className="stat">
              📊 {results.sql_results.length} rows
            </span>
          )}
          {results.execution_time && (
            <span className="stat">
              ⏱️ {results.execution_time.toFixed(2)}s
            </span>
          )}
          {hasChart && (
            <span className="stat">
              📈 Chart generated
            </span>
          )}
        </div>
        
        <div className="summary-actions">
          <button 
            className="action-button"
            onClick={() => {
              // Export functionality could be added here
              console.log('Export functionality to be implemented');
            }}
          >
            📤 Export
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsContainer;
