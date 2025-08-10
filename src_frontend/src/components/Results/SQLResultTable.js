/**
 * SQLResultTable Component
 * Displays SQL query results in a formatted table
 */

import React, { useState, useMemo } from 'react';
import './SQLResultTable.css';

const SQLResultTable = ({ 
  results = [], 
  sqlQuery = '', 
  executionTime = null,
  maxRows = 100,
  className = '',
  onError 
}) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Process and validate results
  const processedResults = useMemo(() => {
    if (!Array.isArray(results) || results.length === 0) {
      return { columns: [], rows: [], totalRows: 0 };
    }

    try {
      // Get column names from first row
      const firstRow = results[0];
      const columns = Object.keys(firstRow);
      
      // Process rows
      const rows = results.slice(0, maxRows).map((row, index) => ({
        id: index,
        ...row
      }));

      return { columns, rows, totalRows: results.length };
    } catch (error) {
      console.error('Error processing SQL results:', error);
      if (onError) {
        onError(error);
      }
      return { columns: [], rows: [], totalRows: 0 };
    }
  }, [results, maxRows, onError]);

  // Sorting logic
  const sortedResults = useMemo(() => {
    if (!sortConfig.key || processedResults.rows.length === 0) {
      return processedResults.rows;
    }

    return [...processedResults.rows].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];

      // Handle null/undefined values
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return sortConfig.direction === 'asc' ? 1 : -1;
      if (bVal == null) return sortConfig.direction === 'asc' ? -1 : 1;

      // Handle different data types
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
      }

      // String comparison
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      
      if (aStr < bStr) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aStr > bStr) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
  }, [processedResults.rows, sortConfig]);

  // Pagination logic
  const paginatedResults = useMemo(() => {
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return sortedResults.slice(startIndex, endIndex);
  }, [sortedResults, currentPage, rowsPerPage]);

  const totalPages = Math.ceil(sortedResults.length / rowsPerPage);

  const handleSort = (columnKey) => {
    setSortConfig(prevConfig => ({
      key: columnKey,
      direction: prevConfig.key === columnKey && prevConfig.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(Math.max(1, Math.min(newPage, totalPages)));
  };

  const formatCellValue = (value) => {
    if (value == null) return <span className="null-value">NULL</span>;
    if (typeof value === 'boolean') return value ? 'True' : 'False';
    if (typeof value === 'number') {
      return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(2);
    }
    if (typeof value === 'string' && value.length > 100) {
      return <span title={value}>{value.substring(0, 100)}...</span>;
    }
    return String(value);
  };

  const getSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) return '⇅';
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  if (processedResults.totalRows === 0) {
    return (
      <div className={`sql-result-table empty ${className}`}>
        <div className="empty-state">
          <h4>No Results Found</h4>
          <p>The query returned no data.</p>
          {sqlQuery && (
            <details className="query-details">
              <summary>View SQL Query</summary>
              <pre className="sql-query">{sqlQuery}</pre>
            </details>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`sql-result-table ${className}`}>
      {/* Header with query info */}
      <div className="table-header">
        <div className="table-info">
          <h3>Query Results</h3>
          <div className="result-stats">
            <span className="row-count">
              {processedResults.totalRows.toLocaleString()} rows
            </span>
            {executionTime && (
              <span className="execution-time">
                • {executionTime.toFixed(2)}s
              </span>
            )}
          </div>
        </div>

        {sqlQuery && (
          <details className="query-details">
            <summary>SQL Query</summary>
            <pre className="sql-query">{sqlQuery}</pre>
          </details>
        )}
      </div>

      {/* Table controls */}
      <div className="table-controls">
        <div className="rows-per-page">
          <label>
            Rows per page:
            <select 
              value={rowsPerPage} 
              onChange={(e) => {
                setRowsPerPage(Number(e.target.value));
                setCurrentPage(1);
              }}
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </label>
        </div>

        <div className="pagination">
          <button 
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage <= 1}
            className="page-btn"
          >
            ← Previous
          </button>
          <span className="page-info">
            Page {currentPage} of {totalPages}
          </span>
          <button 
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
            className="page-btn"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Results table */}
      <div className="table-container">
        <table className="results-table">
          <thead>
            <tr>
              {processedResults.columns.map(column => (
                <th 
                  key={column}
                  onClick={() => handleSort(column)}
                  className={`sortable ${sortConfig.key === column ? 'sorted' : ''}`}
                >
                  <div className="column-header">
                    <span className="column-name">{column}</span>
                    <span className="sort-icon">{getSortIcon(column)}</span>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedResults.map((row) => (
              <tr key={row.id}>
                {processedResults.columns.map(column => (
                  <td key={`${row.id}-${column}`}>
                    {formatCellValue(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer pagination */}
      <div className="table-footer">
        <div className="showing-info">
          Showing {((currentPage - 1) * rowsPerPage) + 1} to {Math.min(currentPage * rowsPerPage, sortedResults.length)} of {sortedResults.length} results
        </div>
      </div>
    </div>
  );
};

export default SQLResultTable;
