import React, { useState, useEffect } from 'react';

const AdminPanel = ({ user, authToken, onBack }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  
  // New user form state
  const [newUser, setNewUser] = useState({
    username: '',
    password: '',
    email: '',
    role: 'user'
  });

  const API_BASE = 'http://localhost:8002';

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/auth/users`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to load users');
      }
      
      const data = await response.json();
      setUsers(Array.isArray(data) ? data : data.users || []);
    } catch (err) {
      setError('Failed to load users: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createUser = async (e) => {
    e.preventDefault();
    
    if (!newUser.username || !newUser.password) {
      setError('Username and password are required');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/auth/create-user`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newUser)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create user');
      }
      
      const data = await response.json();
      
      // Reset form and reload users
      setNewUser({ username: '', password: '', email: '', role: 'user' });
      setShowCreateForm(false);
      await loadUsers();
      
    } catch (err) {
      setError('Failed to create user: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (userId) => {
    if (!confirm(`Delete user ${userId}?`)) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/auth/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to delete user');
      }
      
      await loadUsers();
    } catch (err) {
      setError('Failed to delete user: ' + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel-overlay">
      <div className="admin-panel">
        <div className="admin-panel-header">
          <h2>👤 User Management</h2>
          <button onClick={onBack} className="close-button">✕</button>
        </div>

        {error && (
          <div className="admin-error">
            ⚠️ {error}
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        <div className="admin-panel-actions">
          <button 
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="create-user-button"
            disabled={loading}
          >
            {showCreateForm ? '✕ Cancel' : '➕ Create User'}
          </button>
          <button 
            onClick={loadUsers}
            className="refresh-button"
            disabled={loading}
          >
            🔄 Refresh
          </button>
        </div>

        {showCreateForm && (
          <form onSubmit={createUser} className="create-user-form">
            <h3>Create New User</h3>
            <div className="form-row">
              <input
                type="text"
                placeholder="Username"
                value={newUser.username}
                onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                required
                disabled={loading}
              />
              <input
                type="password"
                placeholder="Password"
                value={newUser.password}
                onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                required
                disabled={loading}
              />
            </div>
            <div className="form-row">
              <input
                type="email"
                placeholder="Email (optional)"
                value={newUser.email}
                onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                disabled={loading}
              />
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                disabled={loading}
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <button type="submit" disabled={loading}>
              {loading ? '⏳ Creating...' : '✅ Create User'}
            </button>
          </form>
        )}

        <div className="users-list">
          <h3>Current Users</h3>
          {loading ? (
            <div className="loading">Loading users...</div>
          ) : users.length === 0 ? (
            <div className="no-users">No users found</div>
          ) : (
            <table className="users-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.user_id}>
                    <td>{user.username}</td>
                    <td>{user.email || '-'}</td>
                    <td>
                      <span className={`role-badge ${user.role}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
                    <td>
                      {user.username !== 'admin' && (
                        <button 
                          onClick={() => deleteUser(user.user_id)}
                          className="delete-button"
                          disabled={loading}
                        >
                          🗑️
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;