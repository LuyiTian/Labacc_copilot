import React, { useState, useEffect } from 'react';
import ChatPanel from './components/ChatPanel';
import './App.css';
import './styles/ChatPanel.css';

function App() {
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [showFiles, setShowFiles] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE = 'http://localhost:8002';

  // Load files when path changes
  useEffect(() => {
    loadFiles(currentPath);
  }, [currentPath]);

  const loadFiles = async (path) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/files/list?path=${encodeURIComponent(path)}`);
      const data = await response.json();
      setFiles(data.files || []);
    } catch (err) {
      setError('Failed to load files: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileClick = (file, event) => {
    if (file.is_dir) {
      // Navigate into directory
      const newPath = currentPath === '/' 
        ? `/${file.name}` 
        : `${currentPath}/${file.name}`;
      setCurrentPath(newPath);
    } else {
      // Handle multi-select with Ctrl/Cmd key
      if (event?.ctrlKey || event?.metaKey) {
        const isSelected = selectedFiles.some(f => f.path === file.path);
        if (isSelected) {
          setSelectedFiles(selectedFiles.filter(f => f.path !== file.path));
        } else {
          setSelectedFiles([...selectedFiles, file]);
        }
      } else {
        // Single select
        setSelectedFile(file);
        setSelectedFiles([file]);
      }
    }
  };

  const handleBackClick = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
    setCurrentPath(parentPath);
  };

  const handleUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const formData = new FormData();
    formData.append('path', currentPath);
    for (let file of files) {
      formData.append('files', file);
    }

    try {
      const response = await fetch(`${API_BASE}/api/files/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        loadFiles(currentPath); // Reload files
      } else {
        setError('Upload failed');
      }
    } catch (err) {
      setError('Upload error: ' + err.message);
    }
  };

  const handleCreateFolder = async () => {
    const folderName = prompt('Enter folder name:');
    if (!folderName) return;

    try {
      const response = await fetch(`${API_BASE}/api/files/folder`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          path: currentPath,
          folder_name: folderName,
        }),
      });

      if (response.ok) {
        loadFiles(currentPath);
      } else {
        setError('Failed to create folder');
      }
    } catch (err) {
      setError('Error creating folder: ' + err.message);
    }
  };

  const handleDelete = async (file) => {
    if (!confirm(`Delete ${file.name}?`)) return;

    try {
      const response = await fetch(`${API_BASE}/api/files`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          paths: [file.path],
        }),
      });

      if (response.ok) {
        loadFiles(currentPath);
        if (selectedFile?.path === file.path) {
          setSelectedFile(null);
        }
      } else {
        setError('Failed to delete file');
      }
    } catch (err) {
      setError('Error deleting file: ' + err.message);
    }
  };

  const getFileIcon = (file) => {
    if (file.is_dir) return '📁';
    
    const ext = file.name.split('.').pop().toLowerCase();
    switch(ext) {
      case 'csv':
      case 'xlsx':
      case 'xls':
        return '📊';
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
        return '🖼️';
      case 'pdf':
        return '📑';
      case 'txt':
      case 'md':
      case 'log':
        return '📝';
      case 'py':
      case 'js':
      case 'json':
        return '💻';
      default:
        return '📄';
    }
  };

  return (
    <div className="app-container">
      <div className="app-header">
        <h1>LabAcc Copilot - File Manager</h1>
        <div className="header-info">
          Modern file management for wet-lab biologists
        </div>
      </div>
      
      <div className="app-content">
        {showFiles && (
          <div className="file-manager-section">
          {/* Toolbar */}
          <div className="toolbar">
            <button 
              className="toolbar-btn"
              onClick={handleBackClick} 
              disabled={currentPath === '/'}
            >
              ← Back
            </button>
            <span className="path-display">{currentPath}</span>
            <button className="toolbar-btn" onClick={handleCreateFolder}>
              + New Folder
            </button>
            <label className="toolbar-btn upload-button">
              ↑ Upload
              <input 
                type="file" 
                multiple 
                onChange={handleUpload}
                style={{ display: 'none' }}
              />
            </label>
            <button className="toolbar-btn" onClick={() => loadFiles(currentPath)}>
              ↻ Refresh
            </button>
          </div>

          {/* File List */}
          <div className="file-list">
            {loading && <div className="loading">Loading...</div>}
            {error && <div className="error">{error}</div>}
            
            {!loading && files.map(file => (
              <div 
                key={file.path}
                className={`file-item ${
                  selectedFile?.path === file.path || selectedFiles.some(f => f.path === file.path) 
                    ? 'selected' : ''
                }`}
                onClick={(e) => handleFileClick(file, e)}
              >
                <span className="file-icon">
                  {getFileIcon(file)}
                </span>
                <span className="file-name">{file.name}</span>
                <span className="file-size">
                  {file.is_dir ? '' : `${(file.size / 1024).toFixed(1)} KB`}
                </span>
                <button 
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(file);
                  }}
                  title="Delete"
                >
                  ×
                </button>
              </div>
            ))}
            
            {!loading && files.length === 0 && (
              <div className="empty-state">
                No files in this directory
              </div>
            )}
          </div>
          </div>
        )}
        
        {/* Chat Panel */}
        <ChatPanel 
          currentFolder={currentPath}
          selectedFiles={selectedFiles.map(f => f.path)}
          showFiles={showFiles}
        />
        
        {/* Toggle Files Button */}
        <button 
          className="files-toggle-button"
          onClick={() => setShowFiles(!showFiles)}
          title={showFiles ? 'Hide Files' : 'Show Files'}
        >
          {showFiles ? '📁 Hide Files' : '📁 Show Files'}
        </button>
      </div>
    </div>
  );
}

export default App;