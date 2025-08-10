import React, { useState } from 'react';
import './FilterPanel.css';

const FilterPanel = ({ onFilterChange, documentStats }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [filters, setFilters] = useState({
    documentTypes: [],
    dateRange: { start: null, end: null },
    versions: 'latest' // 'latest', 'all', 'specific'
  });

  const documentTypes = [
    { value: 'PDF', label: 'PDF Documents', icon: '📄' },
    { value: 'Word', label: 'Word Documents', icon: '📝' },
    { value: 'Excel', label: 'Excel Sheets', icon: '📊' },
    { value: 'PowerPoint', label: 'Presentations', icon: '📑' },
    { value: 'Text', label: 'Text Files', icon: '📃' },
    { value: 'Image', label: 'Images', icon: '🖼️' },
    { value: 'CSV', label: 'CSV Files', icon: '📈' },
    { value: 'Web', label: 'Web Pages', icon: '🌐' }
  ];

  const handleDocumentTypeChange = (type) => {
    const newTypes = filters.documentTypes.includes(type)
      ? filters.documentTypes.filter(t => t !== type)
      : [...filters.documentTypes, type];
    
    const newFilters = { ...filters, documentTypes: newTypes };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleDateRangeChange = (field, value) => {
    const newFilters = {
      ...filters,
      dateRange: { ...filters.dateRange, [field]: value }
    };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleVersionChange = (version) => {
    const newFilters = { ...filters, versions: version };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const clearedFilters = {
      documentTypes: [],
      dateRange: { start: null, end: null },
      versions: 'latest'
    };
    setFilters(clearedFilters);
    onFilterChange(clearedFilters);
  };

  const activeFilterCount = 
    filters.documentTypes.length + 
    (filters.dateRange.start ? 1 : 0) + 
    (filters.dateRange.end ? 1 : 0) +
    (filters.versions !== 'latest' ? 1 : 0);

  return (
    <div className={`filter-panel ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="filter-header" onClick={() => setIsExpanded(!isExpanded)}>
        <h3>
          <svg className="filter-icon" viewBox="0 0 24 24">
            <path d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/>
          </svg>
          Filters
          {activeFilterCount > 0 && (
            <span className="filter-count">{activeFilterCount}</span>
          )}
        </h3>
        <button className="toggle-button">
          <svg viewBox="0 0 24 24" className={isExpanded ? 'rotate' : ''}>
            <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
          </svg>
        </button>
      </div>

      {isExpanded && (
        <div className="filter-content">
          {activeFilterCount > 0 && (
            <button className="clear-filters" onClick={clearFilters}>
              Clear all filters
            </button>
          )}

          <div className="filter-section">
            <h4>Document Type</h4>
            <div className="filter-options">
              {documentTypes.map(type => (
                <label key={type.value} className="filter-checkbox">
                  <input
                    type="checkbox"
                    checked={filters.documentTypes.includes(type.value)}
                    onChange={() => handleDocumentTypeChange(type.value)}
                  />
                  <span className="checkbox-custom"></span>
                  <span className="type-icon">{type.icon}</span>
                  <span className="type-label">{type.label}</span>
                  {documentStats && documentStats[type.value] > 0 && (
                    <span className="type-count">{documentStats[type.value]}</span>
                  )}
                </label>
              ))}
            </div>
          </div>

          <div className="filter-section">
            <h4>Date Range</h4>
            <div className="date-inputs">
              <input
                type="date"
                className="date-input"
                placeholder="Start date"
                value={filters.dateRange.start || ''}
                onChange={(e) => handleDateRangeChange('start', e.target.value)}
              />
              <span className="date-separator">to</span>
              <input
                type="date"
                className="date-input"
                placeholder="End date"
                value={filters.dateRange.end || ''}
                onChange={(e) => handleDateRangeChange('end', e.target.value)}
              />
            </div>
            <div className="quick-dates">
              <button 
                className="quick-date-btn"
                onClick={() => {
                  const today = new Date();
                  const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
                  handleDateRangeChange('start', lastWeek.toISOString().split('T')[0]);
                  handleDateRangeChange('end', today.toISOString().split('T')[0]);
                }}
              >
                Last 7 days
              </button>
              <button 
                className="quick-date-btn"
                onClick={() => {
                  const today = new Date();
                  const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);
                  handleDateRangeChange('start', lastMonth.toISOString().split('T')[0]);
                  handleDateRangeChange('end', today.toISOString().split('T')[0]);
                }}
              >
                Last 30 days
              </button>
            </div>
          </div>

          <div className="filter-section">
            <h4>Document Version</h4>
            <div className="version-options">
              <label className="filter-radio">
                <input
                  type="radio"
                  name="version"
                  value="latest"
                  checked={filters.versions === 'latest'}
                  onChange={() => handleVersionChange('latest')}
                />
                <span className="radio-custom"></span>
                <span className="radio-label">Latest version only</span>
              </label>
              <label className="filter-radio">
                <input
                  type="radio"
                  name="version"
                  value="all"
                  checked={filters.versions === 'all'}
                  onChange={() => handleVersionChange('all')}
                />
                <span className="radio-custom"></span>
                <span className="radio-label">All versions</span>
              </label>
              <label className="filter-radio">
                <input
                  type="radio"
                  name="version"
                  value="specific"
                  checked={filters.versions === 'specific'}
                  onChange={() => handleVersionChange('specific')}
                />
                <span className="radio-custom"></span>
                <span className="radio-label">Specific version</span>
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;