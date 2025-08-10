/**
 * Chart Service
 * Handles rendering and interaction with Plotly charts
 */

class ChartService {
  /**
   * Render Plotly chart from HTML string in React component
   * @param {string} chartHtml - HTML string containing Plotly chart
   * @param {string} containerId - DOM element ID to render chart
   * @returns {Promise<void>}
   */
  async renderChart(chartHtml, containerId) {
    try {
      // Extract Plotly data from HTML if possible
      const plotlyData = this.extractPlotlyData(chartHtml);
      
      if (plotlyData && window.Plotly) {
        const container = document.getElementById(containerId);
        if (container) {
          await window.Plotly.newPlot(container, plotlyData.data, plotlyData.layout, {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            displaylogo: false
          });
        }
      }
    } catch (error) {
      console.error('Failed to render chart:', error);
      throw error;
    }
  }

  /**
   * Extract Plotly data and layout from HTML string
   * @param {string} chartHtml - HTML containing Plotly chart
   * @returns {Object|null} Plotly data and layout or null
   */
  extractPlotlyData(chartHtml) {
    try {
      // This is a simplified extraction - in practice you might need more robust parsing
      const scriptMatch = chartHtml.match(/Plotly\.newPlot\([^,]+,\s*(\{.*?\}),\s*(\{.*?\})/s);
      if (scriptMatch) {
        const data = JSON.parse(scriptMatch[1]);
        const layout = JSON.parse(scriptMatch[2]);
        return { data, layout };
      }
      return null;
    } catch (error) {
      console.warn('Could not extract Plotly data from HTML:', error);
      return null;
    }
  }

  /**
   * Create iframe source document for chart HTML
   * @param {string} chartHtml - Chart HTML content
   * @returns {string} Complete HTML document for iframe
   */
  createIframeDocument(chartHtml) {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
          body { 
            margin: 0; 
            padding: 10px;
            font-family: Arial, sans-serif; 
            background: #ffffff;
          }
          .chart-container { 
            width: 100%; 
            height: calc(100vh - 20px);
            min-height: 400px;
          }
          /* Override Plotly's default colors for better integration */
          .plotly .modebar {
            background: rgba(255, 255, 255, 0.9) !important;
          }
        </style>
      </head>
      <body>
        <div class="chart-container">
          ${chartHtml}
        </div>        <script>
          // Ensure charts are responsive
          window.addEventListener('resize', function() {
            const plots = document.querySelectorAll('.plotly-graph-div');
            plots.forEach(plot => {
              if (window.Plotly) {
                window.Plotly.Plots.resize(plot);
              }
            });
          });
          
          // Send height to parent for responsive iframe
          function updateHeight() {
            const height = document.body.scrollHeight;
            if (window.parent) {
              window.parent.postMessage({ type: 'chartHeight', height }, '*');            }
          }
          
          setTimeout(updateHeight, 100);
          window.addEventListener('resize', updateHeight);
        </script>
      </body>
      </html>
    `;
  }

  /**
   * Create enhanced iframe document for full-screen chart display
   * @param {string} chartHtml - Chart HTML content
   * @param {string} title - Chart title
   * @returns {string} Complete HTML document for full-screen iframe
   */
  createFullScreenIframeDocument(chartHtml, title = 'Data Visualization') {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${title}</title>
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
            flex-shrink: 0;
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
          <h1 class="chart-title">${title}</h1>
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
  }

  /**
   * Download chart as image (if Plotly is available)
   * @param {string} containerId - Chart container ID
   * @param {string} format - Image format ('png', 'jpeg', 'svg', 'pdf')
   * @param {string} filename - Download filename
   */
  async downloadChart(containerId, format = 'png', filename = 'chart') {
    try {
      if (!window.Plotly) {
        throw new Error('Plotly library not available for download');
      }

      const container = document.getElementById(containerId);
      if (!container) {
        throw new Error('Chart container not found');
      }

      const imageData = await window.Plotly.toImage(container, {
        format: format,
        width: 1200,
        height: 800
      });

      // Create download link
      const link = document.createElement('a');
      link.href = imageData;
      link.download = `${filename}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Failed to download chart:', error);
      throw error;
    }
  }

  /**
   * Check if chart HTML contains valid Plotly content
   * @param {string} chartHtml - Chart HTML to validate
   * @returns {boolean} True if valid chart content
   */
  isValidChart(chartHtml) {
    if (!chartHtml || typeof chartHtml !== 'string') {
      return false;
    }
    
    // Check for Plotly indicators
    return chartHtml.includes('plotly') || 
           chartHtml.includes('Plotly') || 
           chartHtml.includes('plotly-graph-div');
  }

  /**
   * Get chart metadata from HTML
   * @param {string} chartHtml - Chart HTML content
   * @returns {Object} Chart metadata
   */
  getChartMetadata(chartHtml) {
    const metadata = {
      hasChart: this.isValidChart(chartHtml),
      chartType: 'unknown',
      title: null
    };

    if (!metadata.hasChart) {
      return metadata;
    }

    try {
      // Try to extract chart type and title
      if (chartHtml.includes('"type":"bar"')) {
        metadata.chartType = 'bar';
      } else if (chartHtml.includes('"type":"line"')) {
        metadata.chartType = 'line';
      } else if (chartHtml.includes('"type":"pie"')) {
        metadata.chartType = 'pie';
      } else if (chartHtml.includes('"type":"scatter"')) {
        metadata.chartType = 'scatter';
      }

      // Try to extract title
      const titleMatch = chartHtml.match(/"title":\s*"([^"]+)"/);
      if (titleMatch) {
        metadata.title = titleMatch[1];
      }
    } catch (error) {
      console.warn('Could not extract chart metadata:', error);
    }

    return metadata;
  }
}

// Create and export singleton instance
const chartService = new ChartService();
export default chartService;
