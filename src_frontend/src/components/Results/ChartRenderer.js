import React, { useEffect, useRef } from 'react';

const ChartRenderer = ({ chartData, chartLayout, title }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (chartData && chartRef.current && window.Plotly) {
      try {
        // Clean up invalid properties
        const cleanData = Array.isArray(chartData) ? chartData.map(trace => {
          const cleanTrace = { ...trace };
          if (cleanTrace.marker && cleanTrace.marker.shadow) {
            delete cleanTrace.marker.shadow;
          }
          return cleanTrace;
        }) : chartData;

        const layout = {
          autosize: true,
          margin: { l: 60, r: 30, t: 50, b: 60 },
          ...chartLayout
        };

        const config = {
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        };

        window.Plotly.newPlot(chartRef.current, cleanData, layout, config);
      } catch (error) {
        console.error('Error rendering chart:', error);
        chartRef.current.innerHTML = `<div class="chart-error">Failed to render chart: ${error.message}</div>`;
      }
    }
  }, [chartData, chartLayout]);

  return (
    <div className="chart-renderer">
      {title && <h4 className="chart-title">{title}</h4>}
      <div ref={chartRef} className="chart-container"></div>
    </div>
  );
};

export default ChartRenderer;
