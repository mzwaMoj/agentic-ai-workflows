import React from 'react';
import './SQLCodeModal.css';

const SQLCodeModal = ({ isOpen, onClose, sqlCode, title = "Generated SQL Code" }) => {
  if (!isOpen) return null;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(sqlCode)
      .then(() => {
        // Could add toast notification here
        console.log('SQL code copied to clipboard');
      })
      .catch(err => {
        console.error('Failed to copy SQL code:', err);
      });
  };

  return (
    <div className="sql-modal-overlay" onClick={onClose}>
      <div className="sql-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="sql-modal-header">
          <h3>{title}</h3>
          <button className="sql-modal-close" onClick={onClose}>
            ✕
          </button>
        </div>
        
        <div className="sql-modal-body">
          <div className="sql-code-container">
            <pre className="sql-code-display">
              <code>{sqlCode}</code>
            </pre>
          </div>
          
          <div className="sql-modal-actions">
            <button 
              className="copy-sql-btn"
              onClick={copyToClipboard}
              title="Copy SQL to clipboard"
            >
              📋 Copy SQL
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SQLCodeModal;
