import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SimpleDataChart from '../Results/SimpleDataChart';
import FullScreenChartModal from '../Charts/FullScreenChartModal';
import './ChatMessage.css';

const ChatMessage = ({ message, isUser }) => {
  const chartRef = useRef(null);
  const [chartFailed, setChartFailed] = useState(false);
  const [showFallbackChart, setShowFallbackChart] = useState(false);
  const [showFullScreenChart, setShowFullScreenChart] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
  };

  const openFullScreenChart = () => {
    if (message.chartHtml) {
      setShowFullScreenChart(true);
    }
  };

  useEffect(() => {
    if (message.chartHtml && chartRef.current && window.Plotly) {
      try {
        chartRef.current.innerHTML = '';
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = message.chartHtml;

        const scripts = tempDiv.querySelectorAll('script');
        let chartRendered = false;

        for (let script of scripts) {
          if (script.textContent.includes('Plotly.newPlot')) {
            try {
              const scriptContent = script.textContent;
              const dataMatch = scriptContent.match(/Plotly\.newPlot\([^,]+,\s*(\[.*?\]),\s*(\{.*?\})/s);

              if (dataMatch) {
                const plotData = JSON.parse(dataMatch[1]);
                const plotLayout = JSON.parse(dataMatch[2]);

                const config = {
                  responsive: true,
                  displayModeBar: true,
                  displaylogo: false,
                  modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
                };

                plotLayout.autosize = true;
                plotLayout.margin = { l: 60, r: 30, t: 50, b: 60 };

                plotData.forEach(trace => {
                  if (trace.marker && trace.marker.shadow) {
                    delete trace.marker.shadow;
                  }
                });

                window.Plotly.newPlot(chartRef.current, plotData, plotLayout, config);
                chartRendered = true;
              }
            } catch (error) {
              console.error('Error parsing Plotly data:', error);
            }
            break;
          }
        }

        if (!chartRendered) {
          try {
            const iframe = document.createElement('iframe');
            iframe.style.width = '100%';
            iframe.style.height = '400px';
            iframe.style.border = 'none';
            chartRef.current.appendChild(iframe);

            const doc = iframe.contentDocument || iframe.contentWindow.document;
            doc.open();
            doc.write(`
              <!DOCTYPE html>
              <html>
              <head>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>body { margin: 0; padding: 10px; }</style>
              </head>
              <body>
                ${message.chartHtml}
              </body>
              </html>
            `);
            doc.close();
            chartRendered = true;
          } catch (error) {
            console.error('Error rendering chart in iframe:', error);
          }
        }

        if (!chartRendered) {
          setChartFailed(true);
          chartRef.current.innerHTML = `
            <div class="chart-error">
              <p>Advanced chart rendering failed. <button onclick="window.showFallbackChart?.()">Try Simple Chart</button></p>
              <details>
                <summary>Show raw chart HTML</summary>
                <pre style="font-size: 10px; overflow: auto; max-height: 200px;">${message.chartHtml.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
              </details>
            </div>
          `;
          window.showFallbackChart = () => setShowFallbackChart(true);
        }
      } catch (error) {
        console.error('Error rendering chart:', error);
        chartRef.current.innerHTML = `<div class="chart-error">Failed to render chart: ${error.message}</div>`;
      }
    }
  }, [message.chartHtml]);

  // Component for limiting table rows with show more/less functionality
  const LimitedTable = ({ children }) => {
    const [showAllRows, setShowAllRows] = useState(false);
    const maxRows = 5;
    
    // Extract table parts
    const tableChildren = React.Children.toArray(children);
    let thead = null;
    let tbody = null;
    
    tableChildren.forEach(child => {
      if (child.type === 'thead') {
        thead = child;
      } else if (child.type === 'tbody') {
        tbody = child;
      }
    });
    
    if (!tbody) {
      return (
        <div className="table-container">
          <table className="markdown-table">{children}</table>
        </div>
      );
    }
    
    const rows = React.Children.toArray(tbody.props.children);
    const shouldLimit = rows.length > maxRows;
    const visibleRows = showAllRows ? rows : rows.slice(0, maxRows);
    
    return (
      <div className="table-container">
        <table className="markdown-table">
          {thead}
          <tbody>
            {visibleRows}
          </tbody>
        </table>
        {shouldLimit && (
          <div className="table-controls" style={{
            textAlign: 'center',
            padding: '8px',
            background: '#f8f9fa',
            borderTop: '1px solid #e9ecef',
            fontSize: '0.8rem'
          }}>
            <button
              onClick={() => setShowAllRows(!showAllRows)}
              style={{
                background: '#0033A1',
                color: 'white',
                border: 'none',
                padding: '4px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.75rem',
                fontWeight: '500'
              }}
              onMouseOver={(e) => e.target.style.background = '#002080'}
              onMouseOut={(e) => e.target.style.background = '#0033A1'}
            >
              {showAllRows ? `Show Less (${maxRows} rows)` : `Show All (${rows.length} rows)`}
            </button>
          </div>
        )}
      </div>
    );
  };

  const customComponents = {
    h3: ({ children }) => {
      const text = children && children[0];
      if (text === 'Main Response Section') {
        return <h3 className="main-section-header">{children}</h3>;
      }
      if (text === 'Source References Section') {
        return <h3 className="references-header">{children}</h3>;
      }
      return <h3>{children}</h3>;
    },
    ul: ({ children }) => <ul className="markdown-list">{children}</ul>,
    ol: ({ children }) => <ol className="markdown-list">{children}</ol>,    table: ({ children }) => <LimitedTable>{children}</LimitedTable>,
    thead: ({ children }) => <thead>{children}</thead>,
    tbody: ({ children }) => <tbody>{children}</tbody>,
    tr: ({ children }) => <tr>{children}</tr>,
    th: ({ children }) => <th>{children}</th>,    td: ({ children }) => {
      // Enhanced content type detection for better cell formatting
      const content = children && children[0];
      let cellClass = '';
      
      if (typeof content === 'string') {
        const trimmedContent = content.trim();
        
        // Currency detection (includes $, €, £, ¥, etc.)
        const isCurrency = /^[\$€£¥₹₽]/.test(trimmedContent) || /\$|€|£|¥|₹|₽/.test(trimmedContent);
        
        // Number detection (integers, decimals, percentages)
        const isNumber = /^-?\d{1,3}(,\d{3})*(\.\d+)?%?$/.test(trimmedContent) || 
                        /^-?\d+(\.\d+)?$/.test(trimmedContent);
        
        // Percentage detection
        const isPercentage = /^\d+(\.\d+)?%$/.test(trimmedContent);
        
        // Date detection (basic patterns)
        const isDate = /^\d{1,2}\/\d{1,2}\/\d{4}$/.test(trimmedContent) ||
                      /^\d{4}-\d{2}-\d{2}$/.test(trimmedContent) ||
                      /^\d{1,2}-\w{3}-\d{4}$/.test(trimmedContent);
        
        // Center alignment for short codes, IDs, or status
        const isCenter = trimmedContent.length <= 5 && /^[A-Z0-9]+$/.test(trimmedContent);
        
        if (isCurrency) {
          cellClass = 'currency-cell';
        } else if (isPercentage) {
          cellClass = 'number-cell'; // Treat percentages as numbers for right alignment
        } else if (isNumber) {
          cellClass = 'number-cell';
        } else if (isDate) {
          cellClass = 'center-cell';
        } else if (isCenter) {
          cellClass = 'center-cell';
        } else {
          cellClass = 'text-cell';
        }
      }
      
      return (
        <td className={cellClass}>
          {children}
        </td>
      );
    },
  };  return (
    <div className={`chat-message-wrapper ${isUser ? 'right' : 'left'}`}>
      <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}>
        <div className="message-content">
          {/* Chart section for assistant messages */}          {!isUser && message.hasChart && (
            <div className="message-chart-section">
              {/* Chart container with click-to-fullscreen functionality */}              <div 
                className="chart-container" 
                ref={chartRef} 
                style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  width: '100%',
                  minHeight: '300px'
                }}              ></div>

              {/* Full Screen Chart Button */}
              {message.chartHtml && (
                <div className="chart-actions" style={{ textAlign: 'center', marginTop: '10px', marginBottom: '10px' }}>
                  <button 
                    onClick={openFullScreenChart}
                    className="fullscreen-action-btn"
                    title="View chart in full screen"
                    style={{
                      background: '#0033A1',
                      color: 'white',
                      border: 'none',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.85rem',
                      fontWeight: '500',
                      transition: 'all 0.2s ease',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}
                    onMouseOver={(e) => {
                      e.target.style.background = '#002080';
                      e.target.style.transform = 'translateY(-1px)';
                      e.target.style.boxShadow = '0 2px 8px rgba(0, 51, 161, 0.3)';
                    }}
                    onMouseOut={(e) => {
                      e.target.style.background = '#0033A1';
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = 'none';
                    }}
                  >
                    🔍 View Full Screen
                  </button>
                </div>
              )}

              {(chartFailed || showFallbackChart) && message.sqlResults && (
                <div className="fallback-chart-section">
                  <div className="fallback-chart-header">
                    <h5>📊 Simple Data Visualization</h5>
                    <div className="chart-type-buttons">
                      <button onClick={() => setShowFallbackChart('bar')} className="chart-type-btn">Bar</button>
                      <button onClick={() => setShowFallbackChart('pie')} className="chart-type-btn">Pie</button>
                      <button onClick={() => setShowFallbackChart('line')} className="chart-type-btn">Line</button>
                    </div>
                  </div>
                  <SimpleDataChart
                    sqlResults={message.sqlResults}
                    chartType={typeof showFallbackChart === 'string' ? showFallbackChart : 'bar'}
                    title="Data Analysis"
                  />
                </div>
              )}
            </div>
          )}

          {/* Message text content */}
          <div className="message-text">
            {!isUser ? (
              <div className="markdown-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={customComponents}>
                  {message.content}
                </ReactMarkdown>
              </div>
            ) : (
              message.content
            )}
          </div>          {/* Message metadata */}
          <div className="message-meta">
            {!isUser && (
              <button
                className="copy-button"
                onClick={copyToClipboard}
                title="Copy to clipboard"
              >
                📋
              </button>
            )}
          </div>        </div>
      </div>
      
      {/* Full Screen Chart Modal */}
      <FullScreenChartModal
        isOpen={showFullScreenChart}
        onClose={() => setShowFullScreenChart(false)}
        chartHtml={message.chartHtml}
        title="Data Visualization"
        message={message}
      />
    </div>
  );
};

export default ChatMessage;
