import React, { useState, useEffect } from 'react';
import './InsightsPanel.css';

const InsightsPanel = ({ result, onClose }) => {
  const [insights, setInsights] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');
  const [error, setError] = useState(null);
  // Temporarily hardcode the correct API endpoint for Python backend
  const [apiEndpoint] = useState('http://localhost:8000/api');

  const fetchInsights = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiEndpoint}/documents/${result.id}/insights`);
      
      if (!response.ok) {
        // If insights API fails, create basic insights from the document data
        setInsights({
          keyPoints: extractKeyPoints(result.content),
          relatedDocuments: [],
          complianceImpact: 'Medium',
          effectiveDate: result.lastmodified,
          supersedes: null
        });
      } else {
        const data = await response.json();
        setInsights(data);
      }
    } catch (error) {
      console.error('Error fetching insights:', error);
      setError('Unable to fetch insights. Please try again later.');
      
      // Provide basic insights from available data
      setInsights({
        keyPoints: extractKeyPoints(result.content),
        relatedDocuments: [],
        complianceImpact: 'Medium',
        effectiveDate: result.lastmodified,
        supersedes: null
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (result && result.id) {
      fetchInsights();
    }
  }, [result, fetchInsights]);

  const extractKeyPoints = (content) => {
    // Extract key points from content
    if (!content) return ['Document content not available'];
    
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 20);
    const keyPoints = [];
    
    // Look for important patterns
    sentences.forEach(sentence => {
      const trimmed = sentence.trim();
      if (trimmed.match(/must|shall|required|compliance|regulation|standard|policy/i)) {
        keyPoints.push(trimmed);
      }
    });
    
    // Return top 3 key points or default message
    return keyPoints.length > 0 
      ? keyPoints.slice(0, 3).map(point => point.substring(0, 150) + '...')
      : ['This document contains regulatory information relevant to your search'];
  };

  const getImpactColor = (impact) => {
    const colors = {
      'High': '#FF4757',
      'Medium': '#FFA502',
      'Low': '#2ED573'
    };
    return colors[impact] || '#747D8C';
  };

  if (isLoading) {
    return (
      <div className="insights-panel loading">
        <div className="insights-header">
          <h3>Document Insights</h3>
          <button className="close-button" onClick={onClose}>
            <svg viewBox="0 0 24 24">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        <div className="loading-content">
          <div className="spinner"></div>
          <p>Analyzing document...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="insights-panel">
      <div className="insights-header">
        <h3>Document Insights</h3>
        <button className="close-button" onClick={onClose}>
          <svg viewBox="0 0 24 24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>

      <div className="insights-tabs">
        <button 
          className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          Summary
        </button>
        <button 
          className={`tab ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
        <button 
          className={`tab ${activeTab === 'related' ? 'active' : ''}`}
          onClick={() => setActiveTab('related')}
        >
          Related
        </button>
      </div>

      <div className="insights-content">
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {activeTab === 'summary' && (
          <div className="summary-tab">
            <div className="document-info">
              <h4>{result.title}</h4>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Type</span>
                  <span className="info-value">{result.filetype}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Version</span>
                  <span className="info-value">v{result.version || 1}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Last Modified</span>
                  <span className="info-value">
                    {new Date(result.lastmodified).toLocaleDateString()}
                  </span>
                </div>
                {insights?.effectiveDate && (
                  <div className="info-item">
                    <span className="info-label">Effective Date</span>
                    <span className="info-value">
                      {new Date(insights.effectiveDate).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {insights?.keyPoints && insights.keyPoints.length > 0 && (
              <div className="key-points">
                <h5>Key Points</h5>
                <ul>
                  {insights.keyPoints.map((point, index) => (
                    <li key={index}>
                      <svg viewBox="0 0 24 24" className="bullet-icon">
                        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                      </svg>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {insights?.complianceImpact && (
              <div className="compliance-impact">
                <h5>Compliance Impact</h5>
                <div 
                  className="impact-badge"
                  style={{ backgroundColor: getImpactColor(insights.complianceImpact) }}
                >
                  {insights.complianceImpact}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'details' && (
          <div className="details-tab">
            <div className="detail-section">
              <h5>Document Metadata</h5>
              <div className="metadata-list">
                <div className="metadata-item">
                  <span className="metadata-label">Document ID</span>
                  <span className="metadata-value">{result.id}</span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">File Name</span>
                  <span className="metadata-value">{result.filename}</span>
                </div>
                {insights?.supersedes && (
                  <div className="metadata-item">
                    <span className="metadata-label">Supersedes</span>
                    <span className="metadata-value">{insights.supersedes}</span>
                  </div>
                )}
                <div className="metadata-item">
                  <span className="metadata-label">Search Score</span>
                  <span className="metadata-value">
                    {((result['@search.score'] || 0) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h5>Content Preview</h5>
              <div className="content-preview">
                {result.content ? result.content.substring(0, 500) + '...' : 'Content not available'}
              </div>
            </div>

            {result.metadata && (
              <div className="detail-section">
                <h5>Additional Information</h5>
                <div className="metadata-list">
                  {(() => {
                    try {
                      const meta = JSON.parse(result.metadata);
                      return Object.entries(meta).map(([key, value]) => (
                        <div key={key} className="metadata-item">
                          <span className="metadata-label">{key}</span>
                          <span className="metadata-value">{String(value)}</span>
                        </div>
                      ));
                    } catch {
                      return null;
                    }
                  })()}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'related' && (
          <div className="related-tab">
            <h5>Related Documents</h5>
            {insights?.relatedDocuments && insights.relatedDocuments.length > 0 ? (
              <div className="related-list">
                {insights.relatedDocuments.map((doc) => (
                  <div key={doc.id} className="related-item">
                    <div className="related-info">
                      <span className="related-title">{doc.title}</span>
                      <span className="relevance-score">
                        {(doc.relevance * 100).toFixed(0)}% match
                      </span>
                    </div>
                    <div className="relevance-bar-container">
                      <div 
                        className="relevance-bar"
                        style={{ width: `${doc.relevance * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-related">No related documents found.</p>
            )}
          </div>
        )}
      </div>

      <div className="insights-actions">
        <button 
          className="action-btn primary"
          onClick={() => {
            // Download or open document logic
            console.log('Opening document:', result.id);
          }}
        >
          <svg viewBox="0 0 24 24">
            <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
          </svg>
          Open Document
        </button>
        <button 
          className="action-btn"
          onClick={() => {
            // Share logic
            if (navigator.share) {
              navigator.share({
                title: result.title,
                text: `Check out this document: ${result.title}`,
                url: window.location.href
              });
            }
          }}
        >
          <svg viewBox="0 0 24 24">
            <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
          </svg>
          Share
        </button>
      </div>
    </div>
  );
};

export default InsightsPanel;