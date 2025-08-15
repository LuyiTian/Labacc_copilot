import React, { useState, useEffect } from 'react';

const ProjectSelector = ({ onProjectSelected, sessionId }) => {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const createDemoProject = async () => {
    setLoading(true);
    setError(null);
    try {
      const headers = {};
      if (sessionId) {
        headers['X-Session-ID'] = sessionId;
      }
      
      const response = await fetch(`${API_BASE}/api/projects/create-demo`, {
        method: 'POST',
        headers
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        // Reload projects to include the new one
        await loadProjects();
        // Auto-select the demo project
        await selectProject(data.project_id);
      }
    } catch (err) {
      setError('Failed to create demo project: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
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
                  <button onClick={createDemoProject} className="create-demo-btn">
                    Create Demo Project
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
              <div className="demo-section">
                <button onClick={createDemoProject} className="create-demo-btn secondary">
                  + Create Demo Project
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ProjectSelector;