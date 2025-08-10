import React, { useEffect, useRef } from 'react';

const SimpleDataChart = ({ sqlResults, chartType = 'bar', title }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (sqlResults && sqlResults.length > 0 && chartRef.current && window.Plotly) {
      try {
        const data = sqlResults;
        const columns = Object.keys(data[0]);
        
        // Simple heuristic for chart creation
        let plotData = [];
        let layout = {
          title: title || 'Data Visualization',
          autosize: true,
          margin: { l: 60, r: 30, t: 50, b: 60 }
        };

        if (columns.length >= 2) {
          const xColumn = columns[0]; // First column as X
          const yColumn = columns[1]; // Second column as Y
          
          const xValues = data.map(row => row[xColumn]);
          const yValues = data.map(row => row[yColumn]);

          if (chartType === 'pie') {
            plotData = [{
              type: 'pie',
              labels: xValues,
              values: yValues,
              textinfo: 'label+percent',
              hovertemplate: '<b>%{label}</b><br>Value: %{value}<br>Percent: %{percent}<extra></extra>'
            }];
          } else if (chartType === 'line') {
            plotData = [{
              type: 'scatter',
              mode: 'lines+markers',
              x: xValues,
              y: yValues,
              name: yColumn,
              line: { color: '#1f77b4', width: 3 },
              marker: { size: 6 }
            }];
            layout.xaxis = { title: xColumn };
            layout.yaxis = { title: yColumn };
          } else { // bar chart (default)
            plotData = [{
              type: 'bar',
              x: xValues,
              y: yValues,
              name: yColumn,
              marker: { 
                color: '#1f77b4',
                opacity: 0.8
              }
            }];
            layout.xaxis = { title: xColumn };
            layout.yaxis = { title: yColumn };
          }

          const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
          };

          window.Plotly.newPlot(chartRef.current, plotData, layout, config);
        } else {
          chartRef.current.innerHTML = '<div class="chart-error">Not enough data columns for visualization</div>';
        }
      } catch (error) {
        console.error('Error creating simple chart:', error);
        chartRef.current.innerHTML = `<div class="chart-error">Failed to create chart: ${error.message}</div>`;
      }
    }
  }, [sqlResults, chartType, title]);

  return (
    <div className="simple-data-chart">
      <div ref={chartRef} className="chart-container"></div>
    </div>
  );
};

export default SimpleDataChart;
