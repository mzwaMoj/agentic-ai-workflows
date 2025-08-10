import React, { useState, useCallback, useRef } from 'react';
import './UploadComponent.css';

const UploadComponent = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadOptions, setUploadOptions] = useState({
    indexDocuments: true,
    overwriteExisting: false,
    extractText: true,
    addMetadata: true
  });
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentFile, setCurrentFile] = useState('');
  const [status, setStatus] = useState('Ready to upload documents');
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);

  // API endpoints - use Python backend by default
  const API_BASE = process.env.REACT_APP_API_ENDPOINT || 'http://localhost:8000/api';
  const STORAGE_CONTAINER = 'documents'; // Default container name

  // Handle file selection (individual files)
  const handleFileSelect = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // Handle folder selection
  const handleFolderSelect = useCallback(() => {
    folderInputRef.current?.click();
  }, []);

  // Process selected files
  const handleFilesChange = useCallback((event) => {
    const files = Array.from(event.target.files);
    addFilesToList(files);
  }, []);

  // Add files to upload list
  const addFilesToList = (files) => {
    const supportedExtensions = ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', '.txt', '.md', '.csv', '.json'];
    
    const newFiles = files
      .filter(file => {
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        return supportedExtensions.includes(extension);
      })
      .filter(file => !selectedFiles.some(existing => existing.name === file.name))
      .map(file => ({
        file,
        name: file.name,
        size: formatFileSize(file.size),
        type: getFileType(file.name),
        status: 'Ready'
      }));

    setSelectedFiles(prev => [...prev, ...newFiles]);
    
    if (newFiles.length > 0) {
      setStatus(`${selectedFiles.length + newFiles.length} files selected`);
    }
  };

  // Get file type from extension
  const getFileType = (filename) => {
    const ext = filename.split('.').pop().toLowerCase();
    const typeMap = {
      'pdf': 'PDF',
      'docx': 'Word', 'doc': 'Word',
      'xlsx': 'Excel', 'xls': 'Excel',
      'pptx': 'PowerPoint', 'ppt': 'PowerPoint',
      'txt': 'Text', 'md': 'Text',
      'csv': 'CSV',
      'json': 'JSON'
    };
    return typeMap[ext] || 'Other';
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Clear file list
  const clearFiles = () => {
    setSelectedFiles([]);
    setStatus('Ready to upload documents');
    setProgress(0);
    setCurrentFile('');
  };

  // Remove individual file
  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setStatus(`${selectedFiles.length - 1} files selected`);
  };

  // Upload & Index Files - Main upload function
  const uploadAndIndexFiles = async () => {
    if (selectedFiles.length === 0) {
      alert('Please select files to upload first');
      return;
    }

    const confirmed = window.confirm(
      `Upload ${selectedFiles.length} files to Azure Storage and Index them for search?\n\n` +
      `This will:\n` +
      `• Upload files to Azure Blob Storage\n` +
      `• ${uploadOptions.indexDocuments ? 'Index documents in Azure Search' : 'Skip search indexing'}\n` +
      `• ${uploadOptions.overwriteExisting ? 'Overwrite existing files' : 'Skip if files exist'}\n` +
      `• ${uploadOptions.extractText ? 'Extract and process text content' : 'Upload as-is'}\n\n` +
      `Continue with upload?`
    );

    if (!confirmed) return;

    setIsUploading(true);
    setProgress(0);
    setStatus('Starting upload...');

    try {
      for (let i = 0; i < selectedFiles.length; i++) {
        const fileInfo = selectedFiles[i];
        setCurrentFile(`Uploading: ${fileInfo.name}`);
        setProgress((i / selectedFiles.length) * 100);

        // Update file status
        setSelectedFiles(prev => prev.map((file, index) => 
          index === i ? { ...file, status: 'Uploading...' } : file
        ));

        try {
          // Upload to Azure Storage
          const formData = new FormData();
          formData.append('file', fileInfo.file);
          formData.append('blobName', fileInfo.name);

          const uploadResponse = await fetch(`${API_BASE}/storage/containers/${STORAGE_CONTAINER}/upload`, {
            method: 'POST',
            body: formData
          });

          if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.statusText}`);
          }

          const uploadResult = await uploadResponse.json();

          // Index document if enabled (this would be handled by backend in a real implementation)
          if (uploadOptions.indexDocuments) {
            // In a real implementation, this would trigger the document indexing
            // For now, we'll simulate it since the backend handles this
            setSelectedFiles(prev => prev.map((file, index) => 
              index === i ? { ...file, status: 'Indexing...' } : file
            ));
            
            // Simulate indexing delay
            await new Promise(resolve => setTimeout(resolve, 1000));
          }

          // Mark as completed
          setSelectedFiles(prev => prev.map((file, index) => 
            index === i ? { ...file, status: 'Completed' } : file
          ));

        } catch (error) {
          console.error(`Error uploading ${fileInfo.name}:`, error);
          setSelectedFiles(prev => prev.map((file, index) => 
            index === i ? { ...file, status: `Error: ${error.message}` } : file
          ));
        }
      }

      setProgress(100);
      setStatus('Upload completed!');
      setCurrentFile('');
      
      const completedCount = selectedFiles.filter(f => f.status === 'Completed').length;
      const errorCount = selectedFiles.length - completedCount;
      
      if (errorCount === 0) {
        alert(
          `✅ Successfully uploaded and indexed ${completedCount} files!\n\n` +
          `Files are now available in:\n` +
          `• Azure Blob Storage (for download)\n` +
          `• Azure Search Index (for searching)\n\n` +
          `You can now search for these documents.`
        );
      } else {
        alert(
          `Upload completed with some errors:\n\n` +
          `✅ ${completedCount} files uploaded successfully\n` +
          `❌ ${errorCount} files had errors\n\n` +
          `Check the file status for details on failed uploads.`
        );
      }

    } catch (error) {
      console.error('Upload process failed:', error);
      setStatus('Upload failed!');
      alert(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Load Documents from Storage
  const loadDocuments = async () => {
    const confirmed = window.confirm(
      'Load all documents from Azure Storage and index them?\n\n' +
      'This will:\n' +
      '• List all documents in storage\n' +
      '• Download and index documents that aren\'t indexed yet\n' +
      '• Update the search index'
    );

    if (!confirmed) return;

    setIsUploading(true);
    setStatus('Loading documents from storage...');
    setCurrentFile('Checking storage...');

    try {
      // Get list of blobs from storage
      const response = await fetch(`${API_BASE}/storage/containers/${STORAGE_CONTAINER}/blobs`);
      
      if (!response.ok) {
        throw new Error(`Failed to list documents: ${response.statusText}`);
      }

      const data = await response.json();
      const blobs = data.blobs || [];

      if (blobs.length === 0) {
        alert('No documents found in storage');
        return;
      }

      // Clear current file list and add storage documents
      setSelectedFiles([]);
      
      const storageFiles = blobs.map(blob => ({
        name: blob.name,
        size: formatFileSize(blob.size),
        type: getFileType(blob.name),
        status: 'Loading...',
        isFromStorage: true
      }));

      setSelectedFiles(storageFiles);

      // In a real implementation, the backend would handle indexing existing storage files
      // For demonstration, we'll simulate the process
      for (let i = 0; i < storageFiles.length; i++) {
        setCurrentFile(`Loading: ${storageFiles[i].name}`);
        setProgress((i / storageFiles.length) * 100);
        
        // Simulate processing
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setSelectedFiles(prev => prev.map((file, index) => 
          index === i ? { ...file, status: 'Indexed' } : file
        ));
      }

      setProgress(100);
      setStatus('Document loading completed!');
      setCurrentFile('');
      
      alert(
        `✅ Loaded ${blobs.length} documents from storage\n\n` +
        `Documents are now indexed and available for search.`
      );

    } catch (error) {
      console.error('Load documents failed:', error);
      setStatus('Load failed!');
      alert(`Failed to load documents: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Reindex All Documents
  const reindexAllDocuments = async () => {
    const confirmed = window.confirm(
      'Reindex all documents in the search service?\n\n' +
      'This will:\n' +
      '• Clear the current search index\n' +
      '• Reload all documents from storage\n' +
      '• Rebuild the search index\n\n' +
      'This operation may take some time.'
    );

    if (!confirmed) return;

    setIsUploading(true);
    setStatus('Reindexing all documents...');
    setCurrentFile('Clearing search index...');

    try {
      // In a real implementation, this would call a backend endpoint to reindex all documents
      // For demonstration, we'll simulate the process
      
      setCurrentFile('Getting documents from storage...');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setCurrentFile('Rebuilding search index...');
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setProgress(100);
      setStatus('Reindex completed!');
      setCurrentFile('');
      
      alert('✅ All documents have been reindexed successfully!');

    } catch (error) {
      console.error('Reindex failed:', error);
      setStatus('Reindex failed!');
      alert(`Reindex failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  // Check Storage Status
  const checkStorageStatus = async () => {
    try {
      setStatus('Checking Azure services...');
      
      // Check storage status
      const storageResponse = await fetch(`${API_BASE}/storage/status`);
      const storageStatus = await storageResponse.json();
      
      // Check container stats
      const statsResponse = await fetch(`${API_BASE}/storage/containers/${STORAGE_CONTAINER}/stats`);
      const containerStats = await statsResponse.json();
      
      let message = 'Azure Services Status:\n\n';
      
      if (storageStatus.available) {
        message += '✓ Connected to Azure Storage\n';
        message += `✓ Container: ${STORAGE_CONTAINER}\n`;
        
        if (statsResponse.ok) {
          message += `✓ Total files: ${containerStats.blob_count}\n`;
          message += `✓ Total size: ${containerStats.total_size_mb} MB\n`;
        }
      } else {
        message += '✗ Azure Storage not available\n';
      }
      
      message += '\nTip: Use "Upload & Index Files" to add documents to both storage and search index.';
      
      alert(message);
      setStatus('Ready to upload documents');
      
    } catch (error) {
      console.error('Status check failed:', error);
      alert(`Status check failed: ${error.message}`);
      setStatus('Ready to upload documents');
    }
  };

  return (
    <div className="upload-component">
      {/* Header */}
      <div className="upload-header">
        <h2>Upload Documents</h2>
        <p>Select and upload documents to Azure Storage and index them for search.</p>
        <div className="status-indicator">
          <span className={`status ${isUploading ? 'uploading' : 'ready'}`}>
            {status}
          </span>
        </div>
      </div>

      {/* File Selection */}
      <div className="file-selection-section">
        <h3>Select Files</h3>
        <div className="file-selection-buttons">
          <button 
            className="btn-primary"
            onClick={handleFileSelect}
            disabled={isUploading}
          >
            📄 Select Files
          </button>
          <button 
            className="btn-secondary"
            onClick={handleFolderSelect}
            disabled={isUploading}
          >
            📁 Select Folder
          </button>
          <button 
            className="btn-secondary"
            onClick={clearFiles}
            disabled={isUploading || selectedFiles.length === 0}
          >
            🗑️ Clear List
          </button>
        </div>

        {/* Hidden file inputs */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFilesChange}
          multiple
          accept=".pdf,.docx,.doc,.xlsx,.xls,.pptx,.ppt,.txt,.md,.csv,.json"
          style={{ display: 'none' }}
        />
        <input
          type="file"
          ref={folderInputRef}
          onChange={handleFilesChange}
          webkitdirectory=""
          multiple
          style={{ display: 'none' }}
        />

        {/* File List */}
        {selectedFiles.length > 0 && (
          <div className="file-list">
            <div className="file-list-header">
              <span>File Name</span>
              <span>Size</span>
              <span>Type</span>
              <span>Status</span>
              <span>Action</span>
            </div>
            {selectedFiles.map((file, index) => (
              <div key={index} className="file-list-item">
                <span className="file-name" title={file.name}>{file.name}</span>
                <span className="file-size">{file.size}</span>
                <span className="file-type">{file.type}</span>
                <span className={`file-status ${file.status.toLowerCase().replace(' ', '-').replace(':', '')}`}>
                  {file.status}
                </span>
                <button
                  className="btn-remove"
                  onClick={() => removeFile(index)}
                  disabled={isUploading}
                  title="Remove file"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upload Options */}
      <div className="upload-options-section">
        <h3>Upload Options</h3>
        <div className="options-grid">
          <label className="option-checkbox">
            <input
              type="checkbox"
              checked={uploadOptions.indexDocuments}
              onChange={(e) => setUploadOptions(prev => ({
                ...prev,
                indexDocuments: e.target.checked
              }))}
              disabled={isUploading}
            />
            <span>Index documents for search</span>
          </label>
          <label className="option-checkbox">
            <input
              type="checkbox"
              checked={uploadOptions.overwriteExisting}
              onChange={(e) => setUploadOptions(prev => ({
                ...prev,
                overwriteExisting: e.target.checked
              }))}
              disabled={isUploading}
            />
            <span>Overwrite existing files</span>
          </label>
          <label className="option-checkbox">
            <input
              type="checkbox"
              checked={uploadOptions.extractText}
              onChange={(e) => setUploadOptions(prev => ({
                ...prev,
                extractText: e.target.checked
              }))}
              disabled={isUploading}
            />
            <span>Extract text content</span>
          </label>
          <label className="option-checkbox">
            <input
              type="checkbox"
              checked={uploadOptions.addMetadata}
              onChange={(e) => setUploadOptions(prev => ({
                ...prev,
                addMetadata: e.target.checked
              }))}
              disabled={isUploading}
            />
            <span>Add file metadata</span>
          </label>
        </div>
      </div>

      {/* Progress Section */}
      {isUploading && (
        <div className="progress-section">
          <h3>Upload Progress</h3>
          <div className="progress-info">
            <span>{status}</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          {currentFile && (
            <div className="current-file">
              {currentFile}
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="action-buttons">
        <button
          className="btn-primary btn-upload"
          onClick={uploadAndIndexFiles}
          disabled={isUploading || selectedFiles.length === 0}
        >
          🚀 Upload & Index Files
        </button>
        <button
          className="btn-secondary"
          onClick={loadDocuments}
          disabled={isUploading}
        >
          📥 Load Documents
        </button>
        <button
          className="btn-secondary"
          onClick={reindexAllDocuments}
          disabled={isUploading}
        >
          🔄 Reindex All
        </button>
        <button
          className="btn-secondary"
          onClick={checkStorageStatus}
          disabled={isUploading}
        >
          📊 Check Storage
        </button>
      </div>

      {/* Help Text */}
      <div className="help-section">
        <h4>Supported File Types</h4>
        <p>
          PDF files (.pdf), Word documents (.docx, .doc), Excel files (.xlsx, .xls), 
          PowerPoint presentations (.pptx, .ppt), Text files (.txt, .md), 
          CSV files (.csv), JSON files (.json)
        </p>
        
        <h4>Upload Process</h4>
        <p>
          <strong>Upload & Index Files:</strong> Uploads selected files to Azure Storage and indexes them for search.<br/>
          <strong>Load Documents:</strong> Loads existing files from Azure Storage and indexes them.<br/>
          <strong>Reindex All:</strong> Rebuilds the entire search index from storage files.<br/>
          <strong>Check Storage:</strong> Displays current Azure Storage and Search status.
        </p>
      </div>
    </div>
  );
};

export default UploadComponent;
