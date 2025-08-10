import React from 'react';
import './ResultCard.css';

const ResultCard = ({ result, index, isSelected, onClick, viewMode }) => {
  const getFileIcon = (fileType) => {
    const icons = {
      'PDF': '📄',
      'Word': '📝',
      'Excel': '📊',
      'PowerPoint': '📑',
      'Text': '📃',
      'Image': '🖼️',
      'CSV': '📈',
      'Web': '🌐'
    };
    return icons[fileType] || '📎';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays < 1) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      });
    }
  };

  const getRelevanceClass = (score) => {
    if (score >= 0.8) return 'high';
    if (score >= 0.6) return 'medium';
    return 'low';
  };

  const truncateText = (text, maxLength) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <div 
      className={`result-card ${isSelected ? 'selected' : ''} ${viewMode}`}
      onClick={onClick}
    >
      <div className="result-header">
        <span className="file-icon">{getFileIcon(result.filetype)}</span>
        <div className="result-title-section">
          <h4 className="result-title">{result.title}</h4>
          <div className="result-meta">
            <span className="file-type">{result.filetype}</span>
            <span className="separator">•</span>
            <span className="last-modified">{formatDate(result.lastmodified)}</span>
            {result.version > 1 && (
              <>
                <span className="separator">•</span>
                <span className="version">v{result.version}</span>
              </>
            )}
          </div>
        </div>
        <div className={`relevance-indicator ${getRelevanceClass(result['@search.score'])}`}>
          <div className="relevance-bar" style={{ width: `${result['@search.score'] * 100}%` }}></div>
        </div>
      </div>

      <div className="result-content">
        {result['@search.highlights']?.content ? (
          <p 
            className="result-excerpt highlighted"
            dangerouslySetInnerHTML={{ 
              __html: result['@search.highlights'].content[0] 
            }}
          />
        ) : (
          <p className="result-excerpt">
            {truncateText(result.content, 200)}
          </p>
        )}
      </div>

      {result.tags && result.tags.length > 0 && (
        <div className="result-tags">
          {result.tags.slice(0, 3).map((tag, idx) => (
            <span key={idx} className="tag">{tag}</span>
          ))}
          {result.tags.length > 3 && (
            <span className="tag more">+{result.tags.length - 3}</span>
          )}
        </div>
      )}

      <div className="result-actions">
        <button className="action-button" title="View document">
          <svg viewBox="0 0 24 24">
            <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
          </svg>
        </button>
        <button className="action-button" title="Download">
          <svg viewBox="0 0 24 24">
            <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
          </svg>
        </button>
        <button className="action-button" title="Share">
          <svg viewBox="0 0 24 24">
            <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ResultCard;