/**
 * FullScreenChartModal Component
 * Displays charts in full-screen modal or opens in new browser window
 */

import React, { useRef, useEffect, useState } from 'react';
import './FullScreenChartModal.css';

const FullScreenChartModal = ({ 
  isOpen, 
  onClose, 
  chartHtml, 
  title, 
  message = null // Original message context
}) => {
  const modalRef = useRef(null);
  const iframeRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Handle escape key to close modal
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  // Handle click outside modal to close
  const handleModalClick = (event) => {
    if (event.target === modalRef.current) {
      onClose();
    }
  };

  // Render chart in iframe when modal opens
  useEffect(() => {
    if (isOpen && chartHtml && iframeRef.current) {
      try {
        setIsLoading(true);
        setError(null);

        // Create enhanced iframe document with better styling
        const iframeDoc = createFullScreenIframeDocument(chartHtml, title);
        iframeRef.current.srcdoc = iframeDoc;
      } catch (err) {
        console.error('Error rendering full-screen chart:', err);
        setError(err.message);
      }
    }
  }, [isOpen, chartHtml, title]);

  const createFullScreenIframeDocument = (chartHtml, chartTitle) => {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${chartTitle || 'Data Visualization'}</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
          body { 
            margin: 0; 
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #ffffff;
            height: 100vh;
            display: flex;
            flex-direction: column;
          }
          .chart-header {
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #0033A1;
          }
          .chart-title {
            color: #0033A1;
            font-size: 1.5em;
            font-weight: 600;
            margin: 0;
          }
          .chart-container { 
            flex: 1;
            width: 100%; 
            min-height: calc(100vh - 100px);
            display: flex;
            justify-content: center;
            align-items: center;
          }
          .plotly .modebar {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 4px !important;
          }
          .plotly .modebar-btn {
            color: #0033A1 !important;
          }
          .plotly .modebar-btn:hover {
            background: rgba(0, 51, 161, 0.1) !important;
          }
          /* Make charts fully responsive */
          .js-plotly-plot {
            width: 100% !important;
            height: 100% !important;
          }
          .plotly-graph-div {
            width: 100% !important;
            height: 100% !important;
          }
        </style>
      </head>
      <body>
        <div class="chart-header">
          <h1 class="chart-title">${chartTitle || 'Data Visualization'}</h1>
        </div>
        <div class="chart-container">
          ${chartHtml}
        </div>
        <script>
          // Ensure chart is fully responsive
          window.addEventListener('resize', function() {
            if (window.Plotly) {
              const plotlyDivs = document.querySelectorAll('.js-plotly-plot');
              plotlyDivs.forEach(div => {
                window.Plotly.Plots.resize(div);
              });
            }
          });
          
          // Auto-resize after load
          window.addEventListener('load', function() {
            setTimeout(() => {
              if (window.Plotly) {
                const plotlyDivs = document.querySelectorAll('.js-plotly-plot');
                plotlyDivs.forEach(div => {
                  window.Plotly.Plots.resize(div);
                });
              }
            }, 100);
          });
        </script>
      </body>
      </html>
    `;
  };

  const handleIframeLoad = () => {
    setIsLoading(false);
  };  const openInNewWindow = () => {
    try {
      const newWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
      
      if (newWindow) {
        const iframeDoc = createFullScreenIframeDocument(chartHtml, title);
        
        newWindow.document.write(iframeDoc);
        newWindow.document.close();
        newWindow.focus();
        
        // Optionally close the modal after opening in new window
        onClose();
      } else {
        alert('Please allow pop-ups to open the chart in a new window. Check your browser settings or look for a pop-up blocker icon in the address bar.');
      }
    } catch (err) {
      console.error('Failed to open chart in new window:', err);
      alert(`Failed to open chart in new window: ${err.message}. Please check your browser settings.`);
    }
  };

  const downloadChart = async (format = 'png') => {
    try {
      // For iframe-based charts, we'll need to communicate with the iframe
      // This is a simplified implementation
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = 1200;
      canvas.height = 800;
      
      // Fill with white background
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // Add title
      ctx.fillStyle = '#0033A1';
      ctx.font = '24px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(title || 'Data Visualization', canvas.width / 2, 40);
      
      // Convert to blob and download
      canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${title || 'chart'}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }, `image/${format}`);
    } catch (err) {
      console.error('Failed to download chart:', err);
      alert('Download failed. You can use the browser\'s right-click menu to save the chart.');
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fullscreen-chart-modal" ref={modalRef} onClick={handleModalClick}>
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">{title || 'Data Visualization'}</h2>
          <div className="modal-controls">
            <button 
              onClick={() => downloadChart('png')}
              className="control-btn download-btn"
              title="Download as PNG"
            >
              📥 PNG
            </button>
            <button 
              onClick={() => downloadChart('pdf')}
              className="control-btn download-btn"
              title="Download as PDF"
            >
              📄 PDF
            </button>            <button 
              onClick={openInNewWindow}
              className="control-btn new-window-btn"
              title="Open in New Window"
            >
              🔗 New Window
            </button>
            <button 
              onClick={onClose}
              className="control-btn close-btn"
              title="Close (Esc)"
            >
              ✕ Close
            </button>
          </div>
        </div>

        <div className="modal-body">
          {isLoading && (
            <div className="loading-overlay">
              <div className="loading-spinner"></div>
              <p>Loading full-screen chart...</p>
            </div>
          )}

          {error && (
            <div className="error-overlay">
              <div className="error-message">
                <h3>Failed to load chart</h3>
                <p>{error}</p>
                <button onClick={() => setError(null)} className="retry-btn">
                  Retry
                </button>
              </div>
            </div>
          )}

          <iframe
            ref={iframeRef}
            className="fullscreen-chart-iframe"
            title={title || 'Data Visualization'}
            onLoad={handleIframeLoad}
            style={{ 
              opacity: isLoading ? 0 : 1,
              transition: 'opacity 0.3s ease-in-out'
            }}
          />
        </div>

        {message && (
          <div className="modal-footer">
            <details className="context-info">
              <summary>Chart Context</summary>
              <div className="context-content">
                <p><strong>Generated from:</strong> {message.content?.substring(0, 100)}...</p>
                {message.sqlQuery && (
                  <div className="sql-context">
                    <strong>SQL Query:</strong>
                    <pre><code>{message.sqlQuery}</code></pre>
                  </div>
                )}
                <p><strong>Timestamp:</strong> {new Date(message.timestamp).toLocaleString()}</p>
              </div>
            </details>
          </div>
        )}
      </div>
    </div>
  );
};

export default FullScreenChartModal;
