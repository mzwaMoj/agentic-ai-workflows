import React, { useState } from 'react';
import ResultCard from './ResultCard';
import InsightsPanel from './InsightsPanel';
import './ResultsDisplay.css';

const ResultsDisplay = ({ results, interpretedAnswer, query }) => {
  const [selectedResult, setSelectedResult] = useState(null);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'grid'

  if (!query) {
    return (
      <div className="welcome-state">
        <div className="welcome-content">
          <div className="welcome-icon">🔍</div>
          <h2>Welcome to Regulatory Document Intelligence</h2>
          <p>Search through your regulatory documents to find the latest compliance information, guidelines, and standards.</p>
          <div className="features-grid">
            <div className="feature-card">
              <span className="feature-icon">📊</span>
              <h3>Smart Search</h3>
              <p>AI-powered search that understands context and intent</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🤖</span>
              <h3>GPT Integration</h3>
              <p>Get intelligent interpretations of complex regulations</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">📈</span>
              <h3>Version Tracking</h3>
              <p>Always access the latest regulatory information</p>
            </div>
            <div className="feature-card">
              <span className="feature-icon">🎯</span>
              <h3>Precise Results</h3>
              <p>Find exactly what you need with advanced filtering</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (results.length === 0 && !interpretedAnswer) {
    return (
      <div className="no-results">
        <div className="no-results-content">
          <div className="no-results-icon">🔍</div>
          <h3>No results found for "{query}"</h3>
          <p>Try adjusting your search terms or filters</p>
        </div>
      </div>
    );
  }

  return (
    <div className="results-display">
      {interpretedAnswer && (
        <div className="interpreted-answer">
          <div className="answer-header">
            <div className="answer-icon">
              <svg viewBox="0 0 24 24" className="gpt-icon">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <h3>AI-Powered Answer</h3>
            <span className="powered-by">Powered by GPT-4</span>
          </div>
          <div className="answer-content">
            <p>{interpretedAnswer}</p>
          </div>
          <div className="answer-disclaimer">
            <svg className="info-icon" viewBox="0 0 24 24">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
            </svg>
            This answer is generated based on the search results below. Always verify with the source documents.
          </div>
        </div>
      )}

      <div className="results-header">
        <h3 className="results-count">
          Found {results.length} relevant document{results.length !== 1 ? 's' : ''}
        </h3>
        <div className="view-controls">
          <button 
            className={`view-button ${viewMode === 'list' ? 'active' : ''}`}
            onClick={() => setViewMode('list')}
          >
            <svg viewBox="0 0 24 24">
              <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/>
            </svg>
            List
          </button>
          <button 
            className={`view-button ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
          >
            <svg viewBox="0 0 24 24">
              <path d="M4 11h5V5H4v6zm0 7h5v-6H4v6zm6 0h5v-6h-5v6zm6 0h5v-6h-5v6zm-6-7h5V5h-5v6zm6-6v6h5V5h-5z"/>
            </svg>
            Grid
          </button>
        </div>
      </div>

      <div className={`results-container ${viewMode}`}>
        <div className="results-list">
          {results.map((result, index) => (
            <ResultCard 
              key={result.id || index}
              result={result}
              index={index}
              isSelected={selectedResult?.id === result.id}
              onClick={() => setSelectedResult(result)}
              viewMode={viewMode}
            />
          ))}
        </div>

        {selectedResult && viewMode === 'list' && (
          <div className="result-details">
            <InsightsPanel result={selectedResult} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsDisplay;