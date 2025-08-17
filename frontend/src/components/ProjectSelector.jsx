import React, { useState, useEffect } from 'react';
import ProjectCreationModal from './ProjectCreationModal';

const ProjectSelector = ({ onProjectSelected, sessionId }) => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const API_BASE = 'http://localhost:8002';

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const headers = {};
      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await fetch(`${API_BASE}/api/projects/list`, { headers });
      const data = await response.json();
      setProjects(data.projects || []);
      
      // Auto-store session ID if returned
      if (data.current_session && !sessionId) {
        onProjectSelected(null, data.current_session);
      }
    } catch (err) {
      setError('Failed to load projects: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectProject = async (projectId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/projects/select`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({ project_id: projectId })
      });

      if (!response.ok) {
        throw new Error(`Failed to select project: ${response.statusText}`);
      }

      const data = await response.json();
      setSelectedProject(data.selected_project);
      onProjectSelected(data.selected_project, sessionId);
    } catch (err) {
      setError('Failed to select project: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectCreated = async (projectId) => {
    // Reload projects to include the new one
    await loadProjects();
    // Auto-select the new project
    await selectProject(projectId);
    setShowCreateModal(false);
  };

  if (selectedProject) {
    return (
      <div className="project-selector selected">
        <div className="selected-project">
          <h3>📁 Current Project: {selectedProject.replace('project_', '').replace(/_/g, ' ')}</h3>
          <button onClick={() => {setSelectedProject(null); onProjectSelected(null, sessionId);}} className="change-project-btn">
            Change Project
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="project-selector">
      <div className="project-selector-content">
        <h2>🚀 Select a Project</h2>
        <p>Choose which project to work with. The AI agent will operate within the selected project.</p>
        
        {error && <div className="error">{error}</div>}
        
        {loading ? (
          <div className="loading">Loading projects...</div>
        ) : (
          <>
            <div className="projects-list">
              {projects.length === 0 ? (
                <div className="no-projects">
                  <p>No projects found.</p>
                  <button onClick={() => setShowCreateModal(true)} className="create-project-btn">
                    ➕ Create Project
                  </button>
                </div>
              ) : (
                projects.map((project) => (
                  <div
                    key={project.project_id}
                    className="project-card"
                    onClick={() => selectProject(project.project_id)}
                  >
                    <h3>{project.name}</h3>
                    <p>Permission: {project.permission}</p>
                    <div className="project-id">ID: {project.project_id}</div>
                  </div>
                ))
              )}
            </div>
            
            {projects.length > 0 && (
              <div className="project-actions">
                <button onClick={() => setShowCreateModal(true)} className="create-project-btn">
                  ➕ Create New Project
                </button>
              </div>
            )}
          </>
        )}
      </div>
      
      {showCreateModal && (
        <ProjectCreationModal
          sessionId={sessionId}
          onClose={() => setShowCreateModal(false)}
          onProjectCreated={handleProjectCreated}
        />
      )}
    </div>
  );
};

export default ProjectSelector;