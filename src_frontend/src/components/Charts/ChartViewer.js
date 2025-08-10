/**
 * ChartViewer Component
 * Renders Plotly charts from HTML strings using iframe approach
 */

import React, { useRef, useEffect, useState } from 'react';
import chartService from '../../services/chartService';
import FullScreenChartModal from './FullScreenChartModal';
import './ChartViewer.css';

const ChartViewer = ({ chartHtml, title, className = '', onError }) => {
  const iframeRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [chartMetadata, setChartMetadata] = useState(null);
  const [showFullScreenChart, setShowFullScreenChart] = useState(false);

  useEffect(() => {
    if (chartHtml) {
      try {
        // Get chart metadata
        const metadata = chartService.getChartMetadata(chartHtml);
        setChartMetadata(metadata);

        if (!metadata.hasChart) {
          throw new Error('Invalid chart data provided');
        }

        // Create iframe document
        const iframeDoc = chartService.createIframeDocument(chartHtml);
        
        // Set iframe content
        if (iframeRef.current) {
          iframeRef.current.srcdoc = iframeDoc;
        }

        setError(null);
      } catch (err) {
        console.error('Chart rendering error:', err);
        setError(err.message);
        if (onError) {
          onError(err);
        }
      }
    }
  }, [chartHtml, onError]);

  const handleIframeLoad = () => {
    setIsLoading(false);
  };
  const handleDownload = async (format = 'png') => {
    try {
      // For iframe-based charts, we'll need to implement download differently
      // This is a placeholder for now
      console.log('Download functionality for iframe charts to be implemented');
    } catch (err) {
      console.error('Failed to download chart:', err);
    }
  };  const openFullScreenChart = () => {
    if (chartHtml) {
      setShowFullScreenChart(true);
    }
  };

  if (!chartHtml) {
    return null;
  }

  if (error) {
    return (
      <div className={`chart-viewer error ${className}`}>
        <div className="chart-error">
          <h4>Chart Rendering Error</h4>
          <p>{error}</p>
          <button 
            onClick={() => setError(null)}
            className="retry-button"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`chart-viewer ${className}`}>      {title && (        
        <div className="chart-header">
          <h3 className="chart-title">{title}</h3>
          <div className="chart-controls">
            <button 
              onClick={() => handleDownload('png')}
              className="download-btn"
              title="Download as PNG"
            >
              📥 PNG
            </button>
            <button 
              onClick={() => handleDownload('pdf')}
              className="download-btn"
              title="Download as PDF"
            >
              📄 PDF
            </button>
          </div>
        </div>
      )}<div className="chart-container">
        {isLoading && (
          <div className="chart-loading">
            <div className="loading-spinner"></div>
            <p>Loading chart...</p>
          </div>
        )}
        
        <iframe
          ref={iframeRef}
          className="chart-iframe"
          title={title || 'Data Visualization'}
          onLoad={handleIframeLoad}
          style={{
            opacity: isLoading ? 0 : 1,
            transition: 'opacity 0.3s ease-in-out'
          }}
        />
      </div>

      {/* Full Screen Button */}
      <div className="chart-actions">
        <button 
          onClick={openFullScreenChart}
          className="fullscreen-action-btn"
          title="View chart in full screen"
        >
          🔍 View Full Screen
        </button>
      </div>
      {chartMetadata && (
        <div className="chart-info">
          <small className="chart-metadata">
            Chart Type: {chartMetadata.chartType} | 
            {chartMetadata.title && ` Title: ${chartMetadata.title}`}
          </small>
        </div>
      )}

      {/* Full Screen Chart Modal */}
      <FullScreenChartModal
        isOpen={showFullScreenChart}
        onClose={() => setShowFullScreenChart(false)}
        chartHtml={chartHtml}
        title={title}
      />
    </div>
  );
};

export default ChartViewer;
