import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const SessionChatPanel = ({ selectedProject, sessionId }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const API_BASE = 'http://localhost:8002';

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize welcome message when project is selected
  useEffect(() => {
    if (selectedProject) {
      setMessages([{
        id: 'welcome',
        content: `🚀 **Welcome to LabAcc Copilot!**\n\nYou're now working in project: **${selectedProject.replace('project_', '').replace(/_/g, ' ')}**\n\nI can help you:\n- 📁 List and analyze experiments\n- 🔬 Read and interpret data files\n- 📊 Diagnose experimental issues\n- 🎯 Suggest optimizations\n- 📚 Research literature\n\nTry asking: *"List my experiments"* or *"What's in this project?"*`,
        author: 'Assistant',
        createdAt: new Date().toISOString(),
        type: 'ai_message'
      }]);
    } else {
      setMessages([]);
    }
  }, [selectedProject]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    if (!selectedProject) {
      setError('Please select a project first');
      return;
    }

    const userMessage = {
      id: Date.now().toString(),
      content: inputValue,
      author: 'Human',
      createdAt: new Date().toISOString(),
      type: 'human_message'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    const currentInput = inputValue;
    setInputValue('');

    try {
      const response = await fetch(`${API_BASE}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({
          message: currentInput,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        author: 'Assistant',
        createdAt: new Date().toISOString(),
        type: 'ai_message'
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (err) {
      console.error('Chat error:', err);
      setError(`Failed to send message: ${err.message}`);
      
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: `❌ **Error**: ${err.message}\n\nPlease check that the backend server is running on port 8002.`,
        author: 'System',
        createdAt: new Date().toISOString(),
        type: 'error_message'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!selectedProject) {
    return (
      <div className="chat-panel">
        <div className="chat-placeholder">
          <h3>Select a Project</h3>
          <p>Please select a project to start chatting with the AI agent.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h3>🤖 LabAcc Copilot Chat</h3>
        <div className="project-info">
          Working in: <strong>{selectedProject.replace('project_', '').replace(/_/g, ' ')}</strong>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-header">
              <span className="author">{message.author}</span>
              <span className="timestamp">
                {new Date(message.createdAt).toLocaleTimeString()}
              </span>
            </div>
            <div className="message-content">
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkBreaks]}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                  table({ children }) {
                    return (
                      <div className="table-wrapper">
                        <table>{children}</table>
                      </div>
                    );
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message ai_message loading">
            <div className="message-header">
              <span className="author">Assistant</span>
              <span className="timestamp">Thinking...</span>
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
          <button onClick={() => setError(null)} className="close-error">×</button>
        </div>
      )}

      <div className="chat-input-container">
        <div className="chat-input">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask about your ${selectedProject.replace('project_', '').replace(/_/g, ' ')} project...`}
            rows="2"
            disabled={isLoading}
          />
          <button 
            onClick={sendMessage} 
            disabled={isLoading || !inputValue.trim()}
            className="send-button"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
        <div className="chat-help">
          <small>Press Enter to send • Shift+Enter for new line</small>
        </div>
      </div>
    </div>
  );
};

export default SessionChatPanel;