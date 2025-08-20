import React, { useState } from 'react';
import './ProjectCreationModal.css';

const ProjectCreationModal = ({ sessionId, authToken, onClose, onProjectCreated }) => {
  const [mode, setMode] = useState(null); // null, 'new', 'import'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // New Research form state
  const [projectName, setProjectName] = useState('');
  const [hypothesis, setHypothesis] = useState('');
  const [plannedExperiments, setPlannedExperiments] = useState('');
  const [expectedOutcomes, setExpectedOutcomes] = useState('');
  
  // Import Data form state
  const [importName, setImportName] = useState('');
  const [importDescription, setImportDescription] = useState('');
  const [selectedFiles, setSelectedFiles] = useState(null);
  
  const API_BASE = 'http://localhost:8002';
  
  const handleCreateNew = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/projects/create-new`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId,
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          name: projectName,
          hypothesis,
          planned_experiments: plannedExperiments.split(',').map(e => e.trim()).filter(e => e),
          expected_outcomes: expectedOutcomes
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create project: ${response.statusText}`);
      }
      
      const data = await response.json();
      onProjectCreated(data.project_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const handleImportData = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('name', importName);
      formData.append('description', importDescription);
      
      // Add all selected files
      if (selectedFiles) {
        for (let i = 0; i < selectedFiles.length; i++) {
          formData.append('files', selectedFiles[i]);
        }
      }
      
      const response = await fetch(`${API_BASE}/api/projects/import-data`, {
        method: 'POST',
        headers: {
          'X-Session-ID': sessionId,
          'Authorization': `Bearer ${authToken}`
        },
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`Failed to import data: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Show conversion results if any
      if (data.conversions && data.conversions.length > 0) {
        const conversionSummary = data.conversions.join('\n');
        alert(`Project imported successfully!\n\nFile conversions:\n${conversionSummary}`);
      }
      
      onProjectCreated(data.project_id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
    
    // Auto-suggest project name from first file/folder
    if (files.length > 0 && !importName) {
      const firstName = files[0].name.replace(/\.(zip|tar|gz)$/i, '');
      setImportName(firstName);
    }
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    setSelectedFiles(files);
    
    if (files.length > 0 && !importName) {
      const firstName = files[0].name.replace(/\.(zip|tar|gz)$/i, '');
      setImportName(firstName);
    }
  };
  
  const handleDragOver = (e) => {
    e.preventDefault();
  };
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        
        {!mode && (
          <>
            <h2>Create New Project</h2>
            <p className="modal-subtitle">Choose how you want to start your project</p>
            
            <div className="creation-options">
              <button 
                className="option-card"
                onClick={() => setMode('new')}
                disabled={loading}
              >
                <span className="option-icon">🧪</span>
                <h3>Start New Research</h3>
                <p>Plan experiments from hypothesis</p>
              </button>
              
              <button 
                className="option-card"
                onClick={() => setMode('import')}
                disabled={loading}
              >
                <span className="option-icon">📁</span>
                <h3>Import Existing Data</h3>
                <p>Organize completed experiments</p>
              </button>
            </div>
          </>
        )}
        
        {mode === 'new' && (
          <>
            <button className="back-button" onClick={() => setMode(null)}>← Back</button>
            <h2>🧪 Start New Research</h2>
            
            <form onSubmit={handleCreateNew}>
              <div className="form-group">
                <label htmlFor="projectName">
                  Project Name <span className="required">*</span>
                </label>
                <input
                  id="projectName"
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="e.g., CRISPR_efficiency_study"
                  required
                  disabled={loading}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="hypothesis">
                  Research Question / Hypothesis <span className="required">*</span>
                </label>
                <textarea
                  id="hypothesis"
                  value={hypothesis}
                  onChange={(e) => setHypothesis(e.target.value)}
                  placeholder="What question are you trying to answer? What is your hypothesis?"
                  rows={4}
                  required
                  disabled={loading}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="experiments">
                  Planned Experiments <span className="optional">(optional)</span>
                </label>
                <input
                  id="experiments"
                  type="text"
                  value={plannedExperiments}
                  onChange={(e) => setPlannedExperiments(e.target.value)}
                  placeholder="e.g., control, treatment_1, treatment_2 (comma-separated)"
                  disabled={loading}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="outcomes">
                  Expected Outcomes <span className="optional">(optional)</span>
                </label>
                <textarea
                  id="outcomes"
                  value={expectedOutcomes}
                  onChange={(e) => setExpectedOutcomes(e.target.value)}
                  placeholder="What results do you expect to see?"
                  rows={3}
                  disabled={loading}
                />
              </div>
              
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-actions">
                <button type="button" onClick={onClose} disabled={loading}>
                  Cancel
                </button>
                <button type="submit" className="primary" disabled={loading || !projectName || !hypothesis}>
                  {loading ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </>
        )}
        
        {mode === 'import' && (
          <>
            <button className="back-button" onClick={() => setMode(null)}>← Back</button>
            <h2>📁 Import Existing Data</h2>
            
            <form onSubmit={handleImportData}>
              <div className="form-group">
                <label htmlFor="importFiles">
                  Select Files or Folders <span className="required">*</span>
                </label>
                <div 
                  className="drop-zone"
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                >
                  <input
                    id="importFiles"
                    type="file"
                    multiple
                    webkitdirectory=""
                    directory=""
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />
                  <label htmlFor="importFiles" className="drop-zone-label">
                    {selectedFiles ? (
                      <div>
                        <p>📦 {selectedFiles.length} file(s) selected</p>
                        <ul className="file-list">
                          {Array.from(selectedFiles).slice(0, 5).map((file, i) => (
                            <li key={i}>{file.name}</li>
                          ))}
                          {selectedFiles.length > 5 && <li>... and {selectedFiles.length - 5} more</li>}
                        </ul>
                      </div>
                    ) : (
                      <>
                        <p>🔽 Drag & drop folders here</p>
                        <p>or click to browse</p>
                        <p className="hint">Accepts: Folders, ZIP files, multiple files</p>
                      </>
                    )}
                  </label>
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="importName">
                  Project Name <span className="required">*</span>
                </label>
                <input
                  id="importName"
                  type="text"
                  value={importName}
                  onChange={(e) => setImportName(e.target.value)}
                  placeholder="e.g., scRNAseq_analysis"
                  required
                  disabled={loading}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="importDesc">
                  Brief Description <span className="optional">(optional)</span>
                </label>
                <textarea
                  id="importDesc"
                  value={importDescription}
                  onChange={(e) => setImportDescription(e.target.value)}
                  placeholder="What kind of experiments are these?"
                  rows={3}
                  disabled={loading}
                />
              </div>
              
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-actions">
                <button type="button" onClick={onClose} disabled={loading}>
                  Cancel
                </button>
                <button type="submit" className="primary" disabled={loading || !importName || !selectedFiles}>
                  {loading ? 'Importing...' : 'Import Data'}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default ProjectCreationModal;