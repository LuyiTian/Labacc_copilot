import React, { useState } from 'react';

const Login = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    if (!password.trim()) {
      setError('Please enter a password');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // For development, accept demo credentials or any username/password
      // In production, this would authenticate against a real auth system
      const response = await fetch('http://localhost:8002/api/projects/list', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        // Pass user info and session to parent
        onLoginSuccess({
          username: username.trim(),
          sessionId: data.current_session,
          role: 'researcher' // In production, this would come from auth
        });
      } else {
        throw new Error('Authentication failed');
      }
    } catch (err) {
      setError('Login failed. Please check that the server is running.');
      console.error('Login error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = () => {
    onLoginSuccess({
      username: 'Demo User',
      sessionId: `demo_${Date.now()}`,
      role: 'researcher'
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🧬 LabAcc Copilot</h1>
          <p>AI-powered laboratory assistant for wet-lab biologists</p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              disabled={isLoading}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="login-button primary"
            disabled={isLoading}
          >
            {isLoading ? '🔄 Signing in...' : '🚀 Sign In'}
          </button>
        </form>

        <div className="login-divider">
          <span>or</span>
        </div>

        <button 
          onClick={handleDemoLogin}
          className="login-button demo"
          disabled={isLoading}
        >
          🎯 Demo Mode
        </button>

        <div className="login-info">
          <h4>Demo Credentials:</h4>
          <ul>
            <li><strong>Username:</strong> admin</li>
            <li><strong>Password:</strong> password</li>
          </ul>
          
          <h4>Features:</h4>
          <ul>
            <li>📊 Multi-project workspace management</li>
            <li>🤖 AI-powered experimental analysis</li>
            <li>📁 Smart file organization</li>
            <li>🔬 Protocol optimization suggestions</li>
            <li>📚 Literature research integration</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login;