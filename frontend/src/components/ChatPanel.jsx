import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
// Removed socket.io-client import - using native WebSocket instead
import ToolCallIndicator from './ToolCallIndicator';
import '../styles/ChatPanel.css';

const API_SERVER = 'http://localhost:8002/api/chat';

const ChatPanel = ({ currentFolder, selectedFiles, showFiles, sessionId, selectedProject }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);

  // Initialize session-based connection
  useEffect(() => {
    if (sessionId && selectedProject) {
      setIsConnected(true);
      
      // Add welcome message for selected project
      setMessages([{
        id: 'welcome',
        content: `🚀 **Welcome to LabAcc Copilot!**\n\nYou're now working in project: **${selectedProject.replace('project_', '').replace(/_/g, ' ')}**\n\nI can help you:\n- 📁 List and analyze experiments\n- 🔬 Read and interpret data files\n- 📊 Diagnose experimental issues\n- 🎯 Suggest optimizations\n- 📚 Research literature\n\nTry asking: *"List my experiments"* or *"What's in this project?"*`,
        author: 'Assistant',
        createdAt: new Date().toISOString(),
        type: 'ai_message'
      }]);
      
      // Connect WebSocket for tool call updates
      if (socketRef.current) {
        socketRef.current.close();
      }
      
      const ws = new WebSocket(`ws://localhost:8002/ws/agent/${sessionId}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected for session:', sessionId);
        setIsConnected(true);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'tool_call') {
            console.log('Tool call update:', data);
            // Tool call indicators will be handled by ToolCallIndicator component
          }
        } catch (err) {
          console.error('WebSocket message parse error:', err);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };
      
      socketRef.current = ws;
    } else if (!selectedProject) {
      setIsConnected(false);
      setMessages([{
        id: 'no-project',
        content: 'Please select a project to start chatting with the AI agent.',
        author: 'System',
        createdAt: new Date().toISOString(),
        type: 'system_message'
      }]);
    }
    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [sessionId, selectedProject]);

  // Update context when folder or files change
  useEffect(() => {
    if (sessionId) {
      // Send context update to server
      fetch(`${API_SERVER}/context`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId,
          currentFolder,
          selectedFiles
        })
      }).catch(console.error);
    }
  }, [currentFolder, selectedFiles, sessionId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (messageContent) => {
    if (!isConnected || isLoading) return;

    const userMessage = {
      id: Date.now(),
      content: messageContent,
      author: 'User',
      createdAt: new Date().toISOString(),
      type: 'user_message'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_SERVER}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-ID': sessionId
        },
        body: JSON.stringify({
          message: messageContent,
          session_id: sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = {
          id: Date.now() + 1,
          content: data.response || 'I received your message but had trouble processing it.',
          author: data.author || 'Assistant',
          createdAt: new Date().toISOString(),
          type: 'ai_message'
        };
        
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        author: 'System',
        createdAt: new Date().toISOString(),
        type: 'error_message'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !isConnected || isLoading) return;
    
    const messageContent = inputValue.trim();
    setInputValue('');
    
    await sendMessage(messageContent);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message) => {
    const isUser = message.author === 'User' || message.type === 'user_message';
    const isSystem = message.type === 'system_message' || message.type === 'error_message';
    
    return (
      <div
        key={message.id}
        className={`message ${isUser ? 'user-message' : isSystem ? 'system-message' : 'ai-message'}`}
      >
        <div className="message-header">
          <span className="message-author">
            {isUser ? 'You' : (message.author || 'Assistant')}
          </span>
          <span className="message-time">
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
              // Better table rendering
              table({ children }) {
                return (
                  <div className="markdown-table-wrapper">
                    <table className="markdown-table">{children}</table>
                  </div>
                );
              },
              // Handle table cells with line breaks
              td({ children }) {
                // Recursively process content to handle <br> tags
                const processContent = (node) => {
                  if (!node) return null;
                  
                  // If it's an array, process each item
                  if (Array.isArray(node)) {
                    return node.map((item, index) => 
                      <React.Fragment key={index}>{processContent(item)}</React.Fragment>
                    );
                  }
                  
                  // If it's a string, check for <br> tags
                  if (typeof node === 'string') {
                    // Check if the string contains <br> tags
                    if (node.includes('<br')) {
                      const parts = node.split(/<br\s*\/?>/gi);
                      return parts.map((part, index) => (
                        <React.Fragment key={index}>
                          {part}
                          {index < parts.length - 1 && <br />}
                        </React.Fragment>
                      ));
                    }
                    return node;
                  }
                  
                  // If it's a React element with children, process the children
                  if (node.props && node.props.children) {
                    return React.cloneElement(node, {
                      ...node.props,
                      children: processContent(node.props.children)
                    });
                  }
                  
                  return node;
                };
                
                return <td>{processContent(children)}</td>;
              },
              // Also handle th elements the same way
              th({ children }) {
                const processContent = (node) => {
                  if (!node) return null;
                  
                  if (Array.isArray(node)) {
                    return node.map((item, index) => 
                      <React.Fragment key={index}>{processContent(item)}</React.Fragment>
                    );
                  }
                  
                  if (typeof node === 'string') {
                    if (node.includes('<br')) {
                      const parts = node.split(/<br\s*\/?>/gi);
                      return parts.map((part, index) => (
                        <React.Fragment key={index}>
                          {part}
                          {index < parts.length - 1 && <br />}
                        </React.Fragment>
                      ));
                    }
                    return node;
                  }
                  
                  if (node.props && node.props.children) {
                    return React.cloneElement(node, {
                      ...node.props,
                      children: processContent(node.props.children)
                    });
                  }
                  
                  return node;
                };
                
                return <th>{processContent(children)}</th>;
              }
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    );
  };

  return (
    <div className={`chat-panel ${!showFiles ? 'full-width' : ''}`}>
      <div className="chat-header">
        <h3>AI Assistant</h3>
        <div className="connection-status">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Connected' : 'Connecting...'}
        </div>
      </div>
      
      {currentFolder && (
        <div className="chat-context">
          <span className="context-label">📁 Current folder:</span>
          <span className="context-value">{currentFolder}</span>
        </div>
      )}
      
      {selectedFiles && selectedFiles.length > 0 && (
        <div className="chat-context">
          <span className="context-label">📎 Selected files:</span>
          <span className="context-value">{selectedFiles.length} files</span>
        </div>
      )}
      
      {/* Tool Call Indicator */}
      <ToolCallIndicator sessionId={sessionId} />
      
      <div className="chat-messages">
        {messages.map(renderMessage)}
        {isLoading && (
          <div className="message ai-message loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            isConnected 
              ? "Ask me about your experiments, data analysis, or file organization..." 
              : "Chat unavailable - Chainlit server not running"
          }
          disabled={!isConnected || isLoading}
          rows={2}
        />
        <button
          className="chat-send-button"
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || !isConnected || isLoading}
        >
          {isLoading ? '...' : '➤'}
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;