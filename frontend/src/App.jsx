import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import ChatPanel from './components/ChatPanel';
import './App.css';
import './styles/ChatPanel.css';
import './styles/Auth.css';

function App() {
  // Authentication state
  const [user, setUser] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  
  // File manager state (original functionality)
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [showFiles, setShowFiles] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const API_BASE = 'http://localhost:8002';

  // Handle login success
  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setSessionId(userData.sessionId);
  };

  // Handle logout
  const handleLogout = () => {
    setUser(null);
    setSelectedProject(null);
    setSessionId(null);
    setCurrentPath('/');
    setFiles([]);
    setSelectedFiles([]);
  };

  // Handle project selection from dashboard
  const handleProjectSelect = (projectId, sessionId) => {
    setSelectedProject(projectId);
    setSessionId(sessionId);
  };

  // Load files when path changes
  useEffect(() => {
    loadFiles(currentPath);
  }, [currentPath]);

  const loadFiles = async (path) => {
    if (!selectedProject) return;
    
    setLoading(true);
    setError(null);
    try {
      const headers = {};
      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await fetch(`${API_BASE}/api/files/list?path=${encodeURIComponent(path)}`, {
        headers
      });
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

    // Check if any files need conversion
    const needsConversion = Array.from(files).some(file => {
      const ext = file.name.split('.').pop().toLowerCase();
      return ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'].includes(ext);
    });

    if (needsConversion) {
      setUploadStatus('Converting documents to Markdown...');
      setIsUploading(true);
    }

    const formData = new FormData();
    formData.append('path', currentPath);
    for (let file of files) {
      formData.append('files', file);
    }

    try {
      const headers = {};
      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await fetch(`${API_BASE}/api/files/upload`, {
        method: 'POST',
        headers,
        body: formData,
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Check if files were converted
        const convertedFiles = result.files?.filter(f => f.conversion_status === 'success');
        if (convertedFiles && convertedFiles.length > 0) {
          setUploadStatus('Files converted! Agent is analyzing...');
          
          // Clear status after 3 seconds
          setTimeout(() => {
            setUploadStatus('');
            setIsUploading(false);
          }, 3000);
        } else {
          setUploadStatus('');
          setIsUploading(false);
        }
        
        loadFiles(currentPath); // Reload files
      } else {
        setError('Upload failed');
        setUploadStatus('');
        setIsUploading(false);
      }
    } catch (err) {
      setError('Upload error: ' + err.message);
      setUploadStatus('');
      setIsUploading(false);
    }
  };

  const handleCreateFolder = async () => {
    const folderName = prompt('Enter folder name:');
    if (!folderName) return;

    try {
      const headers = { 'Content-Type': 'application/json' };
      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await fetch(`${API_BASE}/api/files/folder`, {
        method: 'POST',
        headers,
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
      const headers = { 'Content-Type': 'application/json' };
      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await fetch(`${API_BASE}/api/files`, {
        method: 'DELETE',
        headers,
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

  // Load files when project changes or path changes
  useEffect(() => {
    if (selectedProject) {
      loadFiles(currentPath);
    }
  }, [currentPath, selectedProject]);


  // Main render logic - implements the requested flow
  if (!user) {
    // Step 1: User Login
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  if (!selectedProject) {
    // Step 2: Project Management Dashboard  
    return (
      <Dashboard 
        user={user}
        onProjectSelect={handleProjectSelect}
        onLogout={handleLogout}
      />
    );
  }

  // Step 3: Project Workspace (Original UI Layout)
  return (
    <div className="app-container">
      <div className="app-header">
        <h1>LabAcc Copilot - {selectedProject.replace('project_', '').replace(/_/g, ' ')}</h1>
        <div className="header-info">
          Modern file management for wet-lab biologists
        </div>
      </div>
      
      <div className="app-content">
        {/* Original File Manager - Left Side */}
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

          {/* Upload Status */}
          {uploadStatus && (
            <div className="upload-status" style={{
              padding: '10px',
              backgroundColor: '#e3f2fd',
              color: '#1976d2',
              textAlign: 'center',
              borderBottom: '1px solid #bbdefb'
            }}>
              {uploadStatus}
            </div>
          )}

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
        
        {/* Chat Panel - Updated for session-based system */}
        {selectedProject && (
          <ChatPanel 
            currentFolder={currentPath}
            selectedFiles={selectedFiles.map(f => f.path)}
            showFiles={showFiles}
            sessionId={sessionId}
            selectedProject={selectedProject}
            isUploading={isUploading}
            uploadStatus={uploadStatus}
          />
        )}
        
        {/* Project Controls - Show when project selected */}
        {selectedProject && (
          <div className="project-controls">
            <div className="current-project">
              📁 {selectedProject.replace('project_', '').replace(/_/g, ' ')}
            </div>
            <button 
              className="change-project-btn"
              onClick={() => {
                setSelectedProject(null);
                setSessionId(null);
                setCurrentPath('/');
                setFiles([]);
              }}
            >
              Change Project
            </button>
          </div>
        )}
        
        {/* Toggle Files Button */}
        {selectedProject && (
          <button 
            className="files-toggle-button"
            onClick={() => setShowFiles(!showFiles)}
            title={showFiles ? 'Hide Files' : 'Show Files'}
          >
            {showFiles ? '📁 Hide Files' : '📁 Show Files'}
          </button>
        )}
      </div>
    </div>
  );
}

export default App;