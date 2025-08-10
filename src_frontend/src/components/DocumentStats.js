import React, { useState, useEffect } from 'react';
import './DocumentStats.css';

const DocumentStats = ({ stats }) => {
  const [animatedStats, setAnimatedStats] = useState({});
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (stats) {
      // Animate numbers
      const animateValue = (start, end, duration, key) => {
        const increment = (end - start) / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
          current += increment;
          if (current >= end) {
            current = end;
            clearInterval(timer);
          }
          setAnimatedStats(prev => ({ ...prev, [key]: Math.floor(current) }));
        }, 16);
      };

      // Calculate total
      const total = Object.values(stats).reduce((sum, count) => sum + count, 0);
      animateValue(0, total, 1000, 'total');

      // Animate individual stats
      Object.entries(stats).forEach(([key, value]) => {
        animateValue(0, value, 800, key);
      });
    }
  }, [stats]);

  if (!stats) {
    return (
      <div className="document-stats loading">
        <div className="stats-header">
          <h3>Document Statistics</h3>
        </div>
        <div className="loading-skeleton">
          <div className="skeleton-item"></div>
          <div className="skeleton-item"></div>
          <div className="skeleton-item"></div>
        </div>
      </div>
    );
  }

  const total = animatedStats.total || 0;

  const getPercentage = (value) => {
    return total > 0 ? ((value / total) * 100).toFixed(1) : 0;
  };

  const getBarColor = (type) => {
    const colors = {
      'PDF': '#FF6B6B',
      'Word': '#4ECDC4',
      'Excel': '#45B7D1',
      'PowerPoint': '#F7DC6F',
      'Text': '#BB8FCE',
      'Image': '#F8B500',
      'CSV': '#52C41A',
      'Web': '#1890FF',
      'Other': '#95A5A6'
    };
    return colors[type] || '#95A5A6';
  };

  return (
    <div className={`document-stats ${isVisible ? 'visible' : 'hidden'}`}>
      <div className="stats-header">
        <h3>Document Statistics</h3>
        <button 
          className="toggle-stats"
          onClick={() => setIsVisible(!isVisible)}
          title={isVisible ? 'Hide statistics' : 'Show statistics'}
        >
          <svg viewBox="0 0 24 24">
            <path d={isVisible ? 
              "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" :
              "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
            }/>
          </svg>
        </button>
      </div>

      {isVisible && (
        <>
          <div className="total-documents">
            <div className="total-number">{total.toLocaleString()}</div>
            <div className="total-label">Total Documents</div>
          </div>

          <div className="stats-breakdown">
            {Object.entries(stats).map(([type, count]) => {
              const percentage = getPercentage(animatedStats[type] || 0);
              const animatedCount = animatedStats[type] || 0;
              
              return (
                <div key={type} className="stat-item">
                  <div className="stat-header">
                    <span className="stat-type">{type}</span>
                    <span className="stat-count">{animatedCount.toLocaleString()}</span>
                  </div>
                  <div className="stat-bar-container">
                    <div 
                      className="stat-bar"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: getBarColor(type)
                      }}
                    >
                      <span className="stat-percentage">{percentage}%</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="stats-footer">
            <div className="last-updated">
              <svg viewBox="0 0 24 24" className="clock-icon">
                <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
              </svg>
              Updated just now
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DocumentStats;