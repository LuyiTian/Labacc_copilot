import React, { useState, useEffect } from 'react';
import QuickHelp from './QuickHelp';
import ProjectCreationModal from './ProjectCreationModal';

const Dashboard = ({ user, authToken, onProjectSelect, onLogout, onAdminPanel }) => {
  const [projects, setProjects] = useState([]);
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
      if (user.sessionId) {
        headers['X-Session-ID'] = user.sessionId;
      }
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }
      
      const response = await fetch(`${API_BASE}/api/projects/list`, { headers });
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (err) {
      setError('Failed to load projects: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectCreated = async (projectData) => {
    // Refresh the projects list after creation
    await loadProjects();
    setShowCreateModal(false);
  };

  const selectProject = async (projectId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/projects/select`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': user.sessionId
        },
        body: JSON.stringify({ project_id: projectId })
      });

      if (!response.ok) {
        throw new Error(`Failed to select project: ${response.statusText}`);
      }

      const data = await response.json();
      onProjectSelect(data.selected_project, user.sessionId);
    } catch (err) {
      setError('Failed to select project: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="user-info">
          <h1>Welcome, {user.username}! 👋</h1>
          <p>Choose a project to start working with the AI assistant</p>
        </div>
        <div className="header-buttons">
          {user.role === 'admin' && (
            <button onClick={onAdminPanel} className="admin-button">
              ⚙️ Admin Panel
            </button>
          )}
          <button onClick={onLogout} className="logout-button">
            🚪 Logout
          </button>
        </div>
      </div>

      <QuickHelp />
      
      <div className="dashboard-content">
        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-number">{projects.length}</div>
            <div className="stat-label">Available Projects</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{user.role}</div>
            <div className="stat-label">Role</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">Active</div>
            <div className="stat-label">Status</div>
          </div>
        </div>

        {error && (
          <div className="dashboard-error">
            ⚠️ {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        <div className="projects-section">
          <div className="projects-header">
            <h2>📁 Your Projects</h2>
            <button 
              onClick={() => setShowCreateModal(true)}
              className="create-project-btn"
              disabled={loading}
            >
              {loading ? '⏳' : '➕'} Create Project
            </button>
          </div>

          {loading ? (
            <div className="projects-loading">
              <div className="spinner"></div>
              <p>Loading projects...</p>
            </div>
          ) : projects.length === 0 ? (
            <div className="no-projects">
              <div className="no-projects-icon">📂</div>
              <h3>No Projects Found</h3>
              <p>Create a project to get started with LabAcc Copilot</p>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="create-first-project-btn"
                disabled={loading}
              >
                🚀 Create Your First Project
              </button>
            </div>
          ) : (
            <div className="projects-grid">
              {projects.map((project) => (
                <div
                  key={project.project_id}
                  className="project-card"
                  onClick={() => selectProject(project.project_id)}
                >
                  <div className="project-header">
                    <h3>{project.name}</h3>
                    <div className="project-permission">{project.permission}</div>
                  </div>
                  <div className="project-info">
                    <div className="project-id">{project.project_id}</div>
                  </div>
                  <div className="project-actions">
                    <span className="open-project">Open Project →</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dashboard-help">
          <h3>🤖 What can LabAcc Copilot do?</h3>
          <div className="help-features">
            <div className="feature">
              <span className="feature-icon">🔬</span>
              <div>
                <h4>Experiment Analysis</h4>
                <p>Analyze protocols, data files, and suggest optimizations</p>
              </div>
            </div>
            <div className="feature">
              <span className="feature-icon">📊</span>
              <div>
                <h4>Data Processing</h4>
                <p>Process CSV files, generate insights, and identify patterns</p>
              </div>
            </div>
            <div className="feature">
              <span className="feature-icon">📚</span>
              <div>
                <h4>Literature Research</h4>
                <p>Search scientific literature and get relevant papers</p>
              </div>
            </div>
            <div className="feature">
              <span className="feature-icon">🎯</span>
              <div>
                <h4>Protocol Optimization</h4>
                <p>Get suggestions to improve experimental protocols</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {showCreateModal && (
        <ProjectCreationModal
          sessionId={user.sessionId}
          authToken={authToken}
          onClose={() => setShowCreateModal(false)}
          onProjectCreated={handleProjectCreated}
        />
      )}
    </div>
  );
};

export default Dashboard;